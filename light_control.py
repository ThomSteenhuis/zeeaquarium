import datetime as dt
import logging
import time

import device_repo as dr
import utils

CONTEXT = "light_control"
LIGHT = "verlichting"

LIGHTS_ON_AT = dt.time(8,0)
LIGHTS_OFF_AT = dt.time(20,0)

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()

old = dt.datetime.now().time()

try:
    while True:
        now = dt.datetime.now().time()
        if (now >= LIGHTS_ON_AT and old < LIGHTS_ON_AT):
            device_repo.set_value(LIGHT, True)
            
        
        if (now >= LIGHTS_OFF_AT and old < LIGHTS_OFF_AT):
            device_repo.set_value(LIGHT, False)
        
        old = now
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    sensor_repo.close_connection()
    