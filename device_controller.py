import RPi.GPIO as GPIO
import logging
import time

import device_repo as dr
import utils

CONTEXT = "device_controller"

utils.setup_logging(CONTEXT)

repo = dr.device_repo()

pins = []
for name in repo.get_device_names():
    pins.append({ "name": name, "pin": repo.get_pin(name) })

try:
    GPIO.setmode(GPIO.BOARD)
    for p in pins:
        GPIO.setup(p["pin"], GPIO.OUT)
    
    while True:
        for p in pins:
            value = repo.get_value(p["name"])
        
            if value is None or not isinstance(value, bool):
                logging.warning(f"[{CONTEXT}] illegal value")
            else:
                if value:
                    GPIO.output(p["pin"], GPIO.HIGH) # On
                else:
                    GPIO.output(p["pin"], GPIO.LOW) # Off
        
        time.sleep(0.1)          
except KeyboardInterrupt:
    pass
finally:
    repo.close_connection()
    for p in pins:
        GPIO.cleanup(p["pin"])
