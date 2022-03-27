from MCP3008 import MCP3008
import logging
import time

import sensor_repo as sr
import utils

CONTEXT = "leakage"
LEAKAGE_CHANNEL = 6

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()
adc = MCP3008()

try:    
    while True:
        measurements = []
        while len(measurements) < 50:
            value = adc.read( channel = LEAKAGE_CHANNEL )
            measurements.append(value)
            time.sleep(0.01)
    
        measurements.sort()
        leakage = 100 - round(sum(measurements[10:40]) / (30 * 10.23), 2)
        print(leakage)
        
        if not leakage is None:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, leakage))
        else:
            logging.warning(f"[{CONTEXT}] invalid measurement")
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    adc.close()
    repo.close_connection()
    
