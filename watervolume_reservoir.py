import RPi.GPIO as GPIO
import logging
import time

import sensor_repo as sr
import utils

CONTEXT = "watervolume_reservoir"

PIN_TRIGGER = 36
PIN_ECHO = 22

SPEED_OF_SOUND = 3430 # dm/s
SURFACE_AREA = 2.4 * 2.9 # dm
MAX_VOLUME = 22.5 # dm3

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)
GPIO.output(PIN_TRIGGER, GPIO.LOW)

time.sleep(2)

try:
    while True:
        measurements = []
        while len(measurements) < 300:                
            GPIO.output(PIN_TRIGGER, GPIO.HIGH)            
            time.sleep(0.000001)
            GPIO.output(PIN_TRIGGER, GPIO.LOW)
            
            ref = time.time()
            pulse_start = time.time()
            while GPIO.input(PIN_ECHO)==0 and utils.time_diff(ref, pulse_start) < 0.01:
                pulse_start = time.time()
                
            pulse_end = time.time()
            while GPIO.input(PIN_ECHO)==1 and utils.time_diff(ref, pulse_end) < 0.01:
                pulse_end = time.time()
                
            pulse_time = utils.time_diff(pulse_start, pulse_end)
            if pulse_time < 0.005:
                measurements.append(round(MAX_VOLUME - pulse_time * (SPEED_OF_SOUND / 2) * SURFACE_AREA, 2))
            else:
                logging.warning(f"[{CONTEXT}] invalid measurement")
                
            time.sleep(0.005)
        
        measurements.sort()
        volume = round(sum(measurements[75:225]) / 150, 2)
        
        if not volume is None:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, volume))
        else:
            logging.warning(f"[{CONTEXT}] average could not be calculated")
        
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()
    