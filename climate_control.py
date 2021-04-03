import logging
import time

import sensor_repo as sr
import device_repo as dr
import utils
        
CONTEXT = "climate_control"

HEATING = "verwarming"
TEMP_HEATING_THRESHOLD = 24

utils.setup_logging(CONTEXT)

sensor_repo = sr.sensor_repo("watertemperature")
device_repo = dr.device_repo()

try:
    while True:
        temps = []
        while len(temps) < 60:
            temp = sensor_repo.get_value()
            if temp:
                try:
                    temps.append(float(temp))
                except ValueError:
                    logging.warning(f"[{CONTEXT}] measurement is not a float")
            else:
                logging.warning(f"[{CONTEXT}] measurement could not be retrieved from sensor_repo")
                    
            time.sleep(1)
                         
        if (sum(temps) / len(temps)) > TEMP_HEATING_THRESHOLD:
            device_repo.set_value(HEATING, False)
        else:
            device_repo.set_value(HEATING, True)
except KeyboardInterrupt:
    pass
finally:
    sensor_repo.close_connection()
    device_repo.close_connection()
