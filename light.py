from MCP3008 import MCP3008
import logging
import time

import sensor_repo as sr
import utils

CONTEXT = "light"
LIGHT_CHANNEL = 7

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()
adc = MCP3008()

try:    
    while True:
        measurements = []
        while len(measurements) < 300:
            value = adc.read( channel = LIGHT_CHANNEL )
            measurements.append(value)
            time.sleep(0.01)
    
        measurements.sort()
        light = round(sum(measurements[75:225]) / (150 * 10.23), 2)
        
        if not light is None:
            repo.set_value(CONTEXT, light)
        else:
            logging.warning(f"[{CONTEXT}] invalid measurement")
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    adc.close()
    repo.close_connection()
    