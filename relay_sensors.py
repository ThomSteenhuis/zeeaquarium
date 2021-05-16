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
adc = MCP3008()

try:
    while True:
        relay_sensors = device_repo.get_relay_sensors()
        for relay_sensor in relay_sensors:
            device = device_repo.get_device(relay_sensor['relay'])
            device_name = device_repo.get_device_name(device)
            
            measurements = []
            while len(measurements) < 1000:
                measurements.append(adc.read( channel = relay_sensor['channel'] ))
                time.sleep(0.0001)
                
            measurements.sort()
            value = sum(measurements[940:990]) / len(measurements[940:990]) > 0.9
            
            if value:
                sensor_repo.set_value(f"{device_name}_aan", "1")
            else:
                sensor_repo.set_value(f"{device_name}_aan", "0")
        
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    adc.close()
    device_repo.close_connection()
    sensor_repo.close_connection()    
