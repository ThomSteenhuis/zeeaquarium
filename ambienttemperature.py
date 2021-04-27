import os
import logging
import time

import sensor_repo as sr
import utils
        
CONTEXT = "ambienttemperature"

os.system("modprobe w1_gpio")
os.system("modprobe w1_therm")

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()

try:
    while True:
        temp = utils.read_temp(1, "[" + CONTEXT + "]")

        if temp and temp > 10 and temp < 40 :
            repo.set_value(CONTEXT, temp)
        else:
            logging.warning(f"[{CONTEXT}] invalid measurement")
        
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.error(f"[{CONTEXT}] unknown error")
finally:
    repo.close_connection()
