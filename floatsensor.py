import RPi.GPIO as GPIO
import time

import sensor_repo as sr
import utils

CONTEXT = "vlotter"
PIN = 36

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.IN)

try:
    utils.retry_if_none(lambda : repo.set_value(CONTEXT, "0"))
    high_level_cnt = 0;
    
    while True:
        if GPIO.input(PIN) == 0:
            high_level_cnt += 1
        else:
            time.sleep(5)   
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, "0"))                
            high_level_cnt = 0
        
        if high_level_cnt > 100:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, "1"))             
            high_level_cnt = 0           
        
        time.sleep(0.1)    
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    GPIO.cleanup(PIN)
    