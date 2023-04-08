import os
import logging
import time 
from datetime import datetime, timedelta, timezone
from dateutil import parser

import sensor_repo as sr
import utils
        
CONTEXT = "temperature"
USER_ID = utils.read_secret("user_id")
REEF_ID = utils.read_secret("reef_id")

os.system("modprobe w1_gpio")
os.system("modprobe w1_therm")

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()
token = None

try:
    while True:
        measurement_ids = utils.retry_if_none(lambda: repo.get_sensor_measurement_ids())
        temp_sensors = utils.retry_if_none(lambda: repo.get_temp_sensors())
        if temp_sensors:            
            temps = []
            for temp_sensor in temp_sensors.items():
                raw_temp = utils.read_temp(temp_sensor[0], "[" + CONTEXT + "]")
                if raw_temp is None or raw_temp < 15 or raw_temp > 35:
                    logging.warning(f"[{CONTEXT}] invalid measurement of temperature sensor {temp_sensor[0]}")
                else:
                    temps.append((temp_sensor[1], raw_temp))
                    
            temp_dict = {}
            for (key, value) in temps:
               temp_dict.setdefault(key, []).append(value)
            
            for temp_item in temp_dict.items():                
                if len(temp_item[1]) > 0:
                    temp = sum(temp_item[1]) / len(temp_item[1])
                    utils.retry_if_none(lambda : repo.set_value(temp_item[0], temp))
                    
                    if token == None or parser.parse(token['expiresAt']) < datetime.now(timezone.utc) + timedelta(hours = 1):
                        token = utils.retry_if_none(lambda : utils.get_token_client_credentials(CONTEXT))
                    
                    if token != None:
                        now = datetime.utcnow().isoformat()
                        utils.post_measurement(CONTEXT, token["accessToken"], USER_ID, REEF_ID, measurement_ids[temp_item[0]], now, temp)
                else:
                    logging.warning(f"[{CONTEXT}] no valid measurement")
        else:
            logging.warning(f"[{CONTEXT}] temp sensors could not be retrieved from repo")
        
        time.sleep(60)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()