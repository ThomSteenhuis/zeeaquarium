import RPi.GPIO as GPIO
import logging
import time

import device_repo as dr
import utils

CONTEXT = "device_controller"

utils.setup_logging(CONTEXT)

repo = dr.device_repo()

pins = []
for name in utils.retry_if_none(lambda : repo.get_device_names()):
    pins.append({ "name": name, "pin": utils.retry_if_none(lambda : repo.get_pin(name)), "default": utils.retry_if_none(lambda : repo.get_default(name)) })

try:
    GPIO.setmode(GPIO.BOARD)
    for p in pins:
        GPIO.setup(p["pin"], GPIO.OUT)
        time.sleep(0.2)
        GPIO.output(p["pin"], GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(p["pin"], GPIO.LOW)
    
    time.sleep(0.2)
    
    while True:
        for p in pins:
            value = utils.retry_if_none(lambda : repo.get_value(p["name"]))
        
            if value is None or not isinstance(value, bool):
                logging.warning(f"[{CONTEXT}] illegal value")
            else:
                if value and p["default"]:
                    GPIO.output(p["pin"], GPIO.HIGH) # On:
                elif value and not p["default"]:
                    GPIO.output(p["pin"], GPIO.LOW) # On
                elif not value and p["default"]:
                    GPIO.output(p["pin"], GPIO.LOW) # Off
                else:
                    GPIO.output(p["pin"], GPIO.HIGH) # Off
        
        time.sleep(0.2)          
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()
    for p in pins:
        GPIO.cleanup(p["pin"])
