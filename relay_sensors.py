from ADS1115 import ADS1115
from MCP3008 import MCP3008
import logging
import time

import device_repo as dr
import sensor_repo as sr
import utils

CONTEXT = "relay_sensors"
THRESHOLD = 20;

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()
sensor_repo = sr.sensor_repo()
ads = ADS1115()

try:
    while True:
        relay_sensors = utils.retry_if_none(lambda : device_repo.get_relay_sensors())
        for relay_sensor in relay_sensors:
            device = utils.retry_if_none(lambda : device_repo.get_device(relay_sensor['relay']))
            device_name = utils.retry_if_none(lambda : device_repo.get_device_name(device))
            
            if (device_name is None):
                continue
            
            measurements = []
            tries = 0
            while len(measurements) < 100 and tries < 200:
                try:
                    tries = tries + 1
                    measurements.append(ads.read( channel = relay_sensor['channel'], gain = 16 ))
                except OSError:
                    logging.warning(f"[{CONTEXT}] error getting ads reading for {device_name}")
                
                time.sleep(0.01)
            
            if len(measurements) == 100:
                measurements.sort()
                value = (sum(measurements[50:90]) - sum(measurements[10:50])) / 40
                utils.retry_if_none(lambda : sensor_repo.set_raw_value(f"{device_name}_aan", str(value)))
                
                if value >= THRESHOLD:
                    utils.retry_if_none(lambda : sensor_repo.set_value(f"{device_name}_aan", "1"))
                else:
                    utils.retry_if_none(lambda : sensor_repo.set_value(f"{device_name}_aan", "0"))
            else:
                logging.warning(f"[{CONTEXT}] not enough measurements for {device_name}")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    device_repo.close_connection()
    sensor_repo.close_connection()    
