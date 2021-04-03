import RPi.GPIO as GPIO
import logging
import time
import threading

import utils

class watervolume_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(PIN_ECHO, GPIO.IN)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
    
        time.sleep(2)
        
    def run(self):
        global thread
        
        while is_streaming:
            measurements = []
            while is_streaming and len(measurements) < 300:                
                GPIO.output(PIN_TRIGGER, GPIO.HIGH)            
                time.sleep(0.000001)
                GPIO.output(PIN_TRIGGER, GPIO.LOW)
                
                ref = time.time()
                pulse_start = time.time()            
                while is_streaming and GPIO.input(PIN_ECHO)==0 and utils.time_diff(ref, pulse_start) < 0.01:
                    pulse_start = time.time()
                    
                pulse_end = time.time()
                while is_streaming and GPIO.input(PIN_ECHO)==1 and utils.time_diff(ref, pulse_end) < 0.01:
                    pulse_end = time.time()
                    
                pulse_time = utils.time_diff(pulse_start, pulse_end)
                if pulse_time < 0.005:
                    measurements.append(round(MAX_VOLUME - pulse_time * (SPEED_OF_SOUND / 2) * SURFACE_AREA, 2))
                else:
                    logging.warning(f"{CONTEXT} invalid measurement")
                    
                time.sleep(0.01)
            
            if not is_streaming:
                break
            
            measurements.sort()
            volume = round(sum(measurements[75:225]) / 150, 2)
            if not volume is None:
                try:
                    hub_connection.send("broadcastMeasurement", ["watervolume", str(volume)])
                except:
                    logging.warning(f"{CONTEXT} cannot send signalR message")
        
        thread = None

CONTEXT = "[watervolume]"

PIN_TRIGGER = 13
PIN_ECHO = 11

SPEED_OF_SOUND = 3430 # dm/s
SURFACE_AREA = 3.88 * 9.84 # dm
MAX_VOLUME = 196.62 # dm3

hub_connection = None
is_streaming = False
thread = None

def start_thread(connection):
    global hub_connection, is_streaming, thread
    hub_connection = connection
    is_streaming = True
    
    if thread is None:
        thread = watervolume_thread()
        thread.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
    