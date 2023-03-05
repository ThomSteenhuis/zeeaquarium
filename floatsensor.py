from ADS1115 import ADS1115
import time

import sensor_repo as sr
import utils

CONTEXT = "vlotter"
CHANNEL = 8
THRESHOLD = 25000

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()
ads = ADS1115()

try:
    high_level_cnt = 0;
    
    while True:
        value = ads.read( channel = CHANNEL )
        if value < THRESHOLD:
            high_level_cnt += 1
        else:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, "0"))                
            high_level_cnt = 0
            time.sleep(5)
        
        if high_level_cnt > 100:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, "1"))             
            high_level_cnt = 0
        
        time.sleep(0.1)    
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()
    