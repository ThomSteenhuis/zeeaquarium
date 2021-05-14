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
    repo.set_value(CONTEXT, "0") 
    high_level_cnt = 0;
    while True:
        if GPIO.input(PIN) == 0:
            high_level_cnt += 1
        else:
            time.sleep(5)   
            repo.set_value(CONTEXT, "0")
                
            high_level_cnt = 0
        
        if high_level_cnt > 100:
            repo.set_value(CONTEXT, "1")            
        
        time.sleep(0.1)    
except KeyboardInterrupt:
    pass
except:
    logging.error(f"[{CONTEXT}] unknown error")
finally:
    GPIO.cleanup(PIN)
    