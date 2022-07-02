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
        temp_sensors = utils.retry_if_none(lambda: repo.get_temp_sensors())
        if temp_sensors:
            temp_ids = [key for (key, value) in temp_sensors.items() if value == WATER]
            
            temps = []
            for temp_id in temp_ids:
                raw_temp = utils.read_temp(temp_id, "[" + CONTEXT + "]")
                    
                if raw_temp is None or raw_temp < 15 or raw_temp > 35:
                    logging.warning(f"[{CONTEXT}] invalid measurement of temperature sensor {temp_id}")
                else:
                    temps.append((temp_id, raw_temp))
                    
            if len(temps) > 0:
                temps_only = [t[1] for t in temps]
                temp = sum(temps_only) / len(temps_only)
                if len(temps) >= 3:
                    diffs = [(t[0], t[1], abs(temp - t[1])) for t in temps]
                    diffs = sorted(diffs, key=lambda x: x[2], reverse=True)
                    
                    if diffs[0][2] > 0.5:
                        valid_temps = [d[1] for d in diffs[1:]]
                        logging.warning(f"[{CONTEXT}] removed outlier {diffs[0][0]} = {diffs[0][1]}")
                    else:
                        valid_temps = [d[1] for d in diffs]
                    
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