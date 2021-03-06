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
        lights_on_at = utils.parse_string_to_time(CONTEXT, utils.retry_if_none(lambda : setting_repo.get_value(LIGHTS_ON)))
        lights_off_at = utils.parse_string_to_time(CONTEXT, utils.retry_if_none(lambda : setting_repo.get_value(LIGHTS_OFF)))
        
        if lights_on_at is None or lights_off_at is None:
            logging.warning(f"[{CONTEXT}] lights on/off time could be retrieved")
            continue
        
        now = dt.datetime.now().time()
        
        if (now >= lights_on_at and old < lights_on_at):
            utils.retry_if_none(lambda : device_repo.set_value(LIGHT, True))            
        
        if (now >= lights_off_at and old < lights_off_at):
            utils.retry_if_none(lambda : device_repo.set_value(LIGHT, False))
        
        old = now
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    device_repo.close_connection()
    setting_repo.close_connection()
