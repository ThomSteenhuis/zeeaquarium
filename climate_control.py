import RPi.GPIO as GPIO
import logging
import time

import sensor_repo as sr
import utils
        
CONTEXT = "climate_control"
HEATING_PIN = 33

TEMP_HEATING_THRESHOLD = 24

utils.setup_logging(CONTEXT)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(HEATING_PIN, GPIO.OUT)

repo = sr.sensor_repo("watertemperature")

try:
    while True:
        temps = []
        while len(temps) < 60:
            temp = repo.get_value()
            if temp:
                try:
                    temps.append(float(temp))
                except ValueError:
                    logging.warning(f"[{CONTEXT}] measurement is not a float")
            else:
                logging.warning(f"[{CONTEXT}] measurement could not be retrieved from repo")
                    
            time.sleep(1)
                         
        if (sum(temps) / len(temps)) > TEMP_HEATING_THRESHOLD:
            GPIO.output(HEATING_PIN, GPIO.LOW) # Off
        else:
            GPIO.output(HEATING_PIN, GPIO.HIGH) # On 
except KeyboardInterrupt:
    pass
finally:
    repo.close_connection()
