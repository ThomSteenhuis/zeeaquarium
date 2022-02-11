import datetime as dt
import logging
import time

import device_repo as dr
import setting_repo as setr
import utils

CONTEXT = "flow_control"
PUMP_RF = "pomp_rechts_voor"
FLOW_LOW = "stroming_laag_tijdstip"
FLOW_HIGH = "stroming_hoog_tijdstip"

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()
setting_repo = setr.setting_repo()

old = dt.datetime.now().time()

try:
    while True:
        flow_low_at = utils.parse_string_to_time(CONTEXT, utils.retry_if_none(lambda : setting_repo.get_value(FLOW_LOW)))
        flow_high_at = utils.parse_string_to_time(CONTEXT, utils.retry_if_none(lambda : setting_repo.get_value(FLOW_HIGH)))
        
        if flow_low_at is None or flow_high_at is None:
            logging.warning(f"[{CONTEXT}] flow high/low time could be retrieved")
            continue
        
        now = dt.datetime.now().time()
        
        if (now >= flow_high_at and old < flow_high_at):
            utils.retry_if_none(lambda : device_repo.set_value(PUMP_RF, True))            
        
        if (now >= flow_low_at and old < flow_low_at):
            utils.retry_if_none(lambda : device_repo.set_value(PUMP_RF, False))
        
        old = now
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    device_repo.close_connection()
    setting_repo.close_connection()

