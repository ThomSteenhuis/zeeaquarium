import os
import logging
import time

import sensor_repo as sr
import utils
        
CONTEXT = "watertemperature"
WATER = "water"

os.system("modprobe w1_gpio")
os.system("modprobe w1_therm")

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()

try:
    while True:
        temp_sensors = repo.get_temp_sensors()
        if temp_sensors:
            temp_ids = [key for (key, value) in temp_sensors.items() if value == WATER]
            
            temps = []
            for temp_id in temp_ids:
                raw_temp = utils.read_temp(temp_id, "[" + CONTEXT + "]")
                    
                if raw_temp is None or raw_temp < 15 or raw_temp > 35:
                    logging.warning(f"[{CONTEXT}] invalid measurement of temperature sensor {temp_id}")
                else:
                    temps.append(raw_temp)
                    
            if len(temps) > 0:
                temp = sum(temps) / len(temps)
                if len(temps) >= 3:
                    valid_temps = []
                    for t in temps:
                        if abs(temp - t) <= 0.5:
                            valid_temps.append(t)
                            
                    if len(valid_temps) > 0:
                        temp = sum(valid_temps) / len(valid_temps)
                
                utils.retry_if_none(lambda : repo.set_value(CONTEXT, temp))
            else:
                logging.warning(f"[{CONTEXT}] no valid measurement")
        else:
            logging.warning(f"[{CONTEXT}] temp sensors could not be retrieved from repo")
        
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()