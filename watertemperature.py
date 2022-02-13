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
        temps = []
        temp1 = utils.read_temp(0, "[" + CONTEXT + "]")
        temp2 = utils.read_temp(2, "[" + CONTEXT + "]")
        
        if temp1 is None or temp1 < 15 or temp1 > 35:
            logging.warning(f"[{CONTEXT}] invalid measurement of water temperature sensor 1")
        else:
            temps.append(temp1)
            
        if temp2 is None or temp2 < 15 or temp2 > 35:
            logging.warning(f"[{CONTEXT}] invalid measurement of water temperature sensor 2")
        else:
            temps.append(temp2)
        
        if len(temps) > 0:
            temp = sum(temps) / len(temps)
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, temp))
        else:
            logging.warning(f"[{CONTEXT}] no valid measurement")
        
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()