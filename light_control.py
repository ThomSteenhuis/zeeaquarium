import datetime as dt
import logging
import time

import device_repo as dr
import setting_repo as setr
import utils

CONTEXT = "light_control"
LIGHT = "verlichting"
LIGHTS_ON = "verlichting_aan_tijdstip"
LIGHTS_OFF = "verlichting_uit_tijdstip"

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()
setting_repo = setr.setting_repo()

old = dt.datetime.now().time()

try:
    while True:
        lights_on_at = utils.parse_string_to_time(CONTEXT, setting_repo.get_value(LIGHTS_ON))
        lights_off_at = utils.parse_string_to_time(CONTEXT, setting_repo.get_value(LIGHTS_OFF))
        now = dt.datetime.now().time()
        
        if (now >= lights_on_at and old < lights_on_at):
            device_repo.set_value(LIGHT, True)            
        
        if (now >= lights_off_at and old < lights_off_at):
            device_repo.set_value(LIGHT, False)
        
        old = now
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.error(f"[{CONTEXT}] unknown error")
finally:
    device_repo.close_connection()
    setting_repo.close_connection()
