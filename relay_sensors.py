from ADS1115 import ADS1115
from MCP3008 import MCP3008
import logging
import time

import device_repo as dr
import sensor_repo as sr
import utils

CONTEXT = "relay_sensors"

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()
sensor_repo = sr.sensor_repo()
ads = ADS1115()
mcp = MCP3008()

try:
    while True:
        relay_sensors = utils.retry_if_none(lambda : device_repo.get_relay_sensors())
        for relay_sensor in relay_sensors:
            device = utils.retry_if_none(lambda : device_repo.get_device(relay_sensor['relay']))
            device_name = utils.retry_if_none(lambda : device_repo.get_device_name(device))
            device_voltage_threshold = utils.retry_if_none(lambda: device_repo.get_device_voltage_threshold(device))
            
            if not device_voltage_threshold:
                logging.warning(f"[{CONTEXT}] {device_name} voltage threshold could not be retrieved from repo")
                device_voltage_threshold = 0.5                
            
            measurements = []
            if relay_sensor['source'] == 'mcp':
                while len(measurements) < 1000:
                    measurements.append(mcp.read( channel = relay_sensor['channel'] ))
                    time.sleep(0.0001)
                    
                measurements.sort()
                value = sum(measurements[500:990]) / 490 > sum(measurements[10:500]) / 490 + device_voltage_threshold
            else:                
                while len(measurements) < 100:
                    measurements.append(ads.read( channel = relay_sensor['channel'] - 8, gain = 16 ))
                    time.sleep(0.0001)
                    
                measurements.sort()
                value = sum(measurements[50:99]) / 49 > sum(measurements[1:50]) / 49 + device_voltage_threshold
            
            if value:
                utils.retry_if_none(lambda : sensor_repo.set_value(f"{device_name}_aan", "1"))
            else:
                utils.retry_if_none(lambda : sensor_repo.set_value(f"{device_name}_aan", "0"))
        
        time.sleep(1)
        
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    mcp.close()
    device_repo.close_connection()
    sensor_repo.close_connection()    
