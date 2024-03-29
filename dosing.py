import datetime as dt
import logging
import time

import device_repo as dr
import setting_repo as setr
import utils

CONTEXT = "dosing"
DOSING_AT = "doseer_tijdstip"
DOSING_PUMPS = [
    {"name": "doseerpomp_1"},
    {"name": "doseerpomp_2"},
    {"name": "doseerpomp_3"},
    {"name": "doseerpomp_4"},
    {"name": "doseerpomp_5"}]

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()
setting_repo = setr.setting_repo()

old = dt.datetime.now().time()

try:
    while True:
        for pump in DOSING_PUMPS:
            utils.retry_if_none(lambda: device_repo.set_value(pump["name"], False))
                
        dosing_at = utils.parse_string_to_time(CONTEXT, utils.retry_if_none(lambda: setting_repo.get_value(DOSING_AT)))
        
        if dosing_at is None:
            logging.warning(f"[{CONTEXT}] dosing time could not be retrieved")
            continue
        
        now = dt.datetime.now().time()
        
        if now >= dosing_at and old < dosing_at:
            for pump in DOSING_PUMPS:
                pump_name = pump["name"]
                try: 
                    dosing_volume = float(utils.retry_if_none(lambda: setting_repo.get_value(f"{pump_name}_volume"), 10))
                except ValueError:
                    logging.warning(f"[{CONTEXT}] cannot convert volume of {pump_name} to floating point number")
                    continue
            
                if not dosing_volume:
                    logging.warning(f"[{CONTEXT}] volume of {pump_name} could not be retrieved")
                    continue
                        
                if dosing_volume <= 0:
                    logging.info(f"[{CONTEXT}] {pump_name}: no need to dose")
                else:
                    try: 
                        dosing_vpm = float(utils.retry_if_none(lambda: setting_repo.get_value(f"{pump_name}_vpm"), 10))
                    except ValueError:
                        logging.warning(f"[{CONTEXT}] cannot convert vpm of {pump_name} to floating point number")
                        continue
                
                    if not dosing_vpm:
                        logging.warning(f"[{CONTEXT}] vpm of {pump_name} could not be retrieved")
                        continue
                
                    time_dose = 60 * dosing_volume / (1000 * dosing_vpm)
                    
                    utils.retry_if_none(lambda: device_repo.set_value(pump_name, True), 10)            
                    time.sleep(time_dose)
                    utils.retry_if_none(lambda: device_repo.set_value(pump_name, False), 10)
                    
                    logging.info(f"[{CONTEXT}] {pump_name}: dosed {round(dosing_volume, 1)}mL")
        
        old = now
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    for pump in DOSING_PUMPS:
        utils.retry_if_none(lambda: device_repo.set_value(pump["name"], False))
    device_repo.close_connection()
    setting_repo.close_connection()