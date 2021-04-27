import logging
import time

import sensor_repo as sr
import setting_repo as setr
import device_repo as dr
import utils
        
CONTEXT = "climate_control"

HEATING = "verwarming"
COOLING = "ventilatoren"
HEATING_THRESHOLD = "verwarming_drempel"
COOLING_THRESHOLD = "ventilator_drempel"
TEMP = "watertemperature"
MAX_QUERIES = 100

utils.setup_logging(CONTEXT)

sensor_repo = sr.sensor_repo()
setting_repo = setr.setting_repo()
device_repo = dr.device_repo()

try:
    while True:
        temp_heating_threshold = float(setting_repo.get_value(HEATING_THRESHOLD))
        temp_cooling_threshold = float(setting_repo.get_value(COOLING_THRESHOLD))
        
        temps = []
        queries = 0
        while len(temps) < 60 and queries < MAX_QUERIES:
            queries += 1
            temp = sensor_repo.get_value(TEMP)
            if temp:
                try:
                    temps.append(float(temp))
                except ValueError:
                    logging.warning(f"[{CONTEXT}] measurement is not a float")
            else:
                logging.warning(f"[{CONTEXT}] measurement could not be retrieved from sensor_repo")
                    
            time.sleep(1)
        
        if queries >= MAX_QUERIES:
            device_repo.set_value(HEATING, True) #default    
            device_repo.set_value(COOLING, False) #default
            
        if (sum(temps) / len(temps)) > temp_heating_threshold:
            device_repo.set_value(HEATING, False) #Off
        else:
            device_repo.set_value(HEATING, True) #On
            
        if (sum(temps) / len(temps)) > temp_cooling_threshold:
            device_repo.set_value(COOLING, True) #On
        else:
            device_repo.set_value(COOLING, False) #Off
except KeyboardInterrupt:
    pass
except:
    logging.error(f"[{CONTEXT}] unknown error")
finally:
    sensor_repo.close_connection()
    setting_repo.close_connection()
    device_repo.close_connection()
