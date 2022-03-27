import os
import logging
import time

import sensor_repo as sr
import utils

AMBIENT = "ambient"
CONTEXT = "ambienttemperature"

os.system("modprobe w1_gpio")
os.system("modprobe w1_therm")

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()

try:
    while True:
        temp_sensors = repo.get_temp_sensors()
        if temp_sensors:
            temp_ids = [key for (key, value) in temp_sensors.items() if value == AMBIENT]
            
            if len(temp_ids) == 1:
                temp = utils.read_temp(temp_ids[0], "[" + CONTEXT + "]")

                if temp and temp > 10 and temp < 40 :
                    utils.retry_if_none(lambda : repo.set_value(CONTEXT, temp))
                else:
                    logging.warning(f"[{CONTEXT}] invalid measurement")
            else:
                logging.warning(f"[{CONTEXT}] could not find ambient temperature sensor")
        else:
            logging.warning(f"[{CONTEXT}] temp sensors could not be retrieved from repo")
        
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()
