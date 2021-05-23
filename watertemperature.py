import os
import logging
import time

import sensor_repo as sr
import utils
        
CONTEXT = "watertemperature"

os.system("modprobe w1_gpio")
os.system("modprobe w1_therm")

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()

try:
    while True:
        temp = utils.read_temp(0, "[" + CONTEXT + "]")

        if temp and temp > 15 and temp < 35:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, temp))
        else:
            logging.warning(f"[{CONTEXT}] invalid measurement")
        
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()