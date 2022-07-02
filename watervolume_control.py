import datetime as dt
import logging
import time

import device_repo as dr
import sensor_repo as sr
import setting_repo as setr
import utils

CONTEXT = "watervolume_control"
ATO = "ato"
FLOATSENSOR = "vlotter"
WATER_TOPOFF_AT1 = "water_bijvul_tijdstip1"
WATER_TOPOFF_AT2 = "water_bijvul_tijdstip2"
WATERVOLUME_TARGET = "watervolume_streefwaarde"
WATERVOLUME_AVG = "watervolume_avg"
MAX_TOPOFF_VOLUME = 1.5
VOLUME_PM = 0.5

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()
sensor_repo = sr.sensor_repo()
setting_repo = setr.setting_repo()

old = dt.datetime.now().time()

try:
    while True:
        utils.retry_if_none(lambda: device_repo.set_value(ATO, False))
        
        if utils.retry_if_none(lambda: sensor_repo.get_value(FLOATSENSOR, 0)) == "1":
            logging.warning(f"[{CONTEXT}] water level too high")
        
        water_topoff_at1 = utils.parse_string_to_time(CONTEXT, utils.retry_if_none(lambda: setting_repo.get_value(WATER_TOPOFF_AT1)))
        water_topoff_at2 = utils.parse_string_to_time(CONTEXT, utils.retry_if_none(lambda: setting_repo.get_value(WATER_TOPOFF_AT2)))
        
        if water_topoff_at1 is None:
            logging.warning(f"[{CONTEXT}] water topoff time 1 could not be retrieved")
            continue
        
        if water_topoff_at2 is None:
            logging.warning(f"[{CONTEXT}] water topoff time 2 could not be retrieved")
            continue
        
        now = dt.datetime.now().time()
        
        if now >= water_topoff_at1 and old < water_topoff_at1 or now >= water_topoff_at2 and old < water_topoff_at2:
            try: 
                watervolume_target = float(utils.retry_if_none(lambda: setting_repo.get_value(WATERVOLUME_TARGET)))
                watervolume_current = float(utils.retry_if_none(lambda: sensor_repo.get_value(WATERVOLUME_AVG, 3600)))
            except ValueError:
                logging.warning(f"[{CONTEXT}] cannot convert value to floating point number")
                continue
            
            if not watervolume_target:
                logging.warning(f"[{CONTEXT}] target watervolume could be retrieved")
                continue
                
            if not watervolume_current:
                logging.warning(f"[{CONTEXT}] current watervolume could be retrieved")
                continue
            
            watervolume_topoff = min(MAX_TOPOFF_VOLUME, watervolume_target - watervolume_current)
            
            if watervolume_topoff <= 0:
                logging.info(f"[{CONTEXT}] no need to top off")
            else:            
                time_topoff = 60 * watervolume_topoff / VOLUME_PM
                
                utils.retry_if_none(lambda: device_repo.set_value(ATO, True))            
                time.sleep(time_topoff)
                utils.retry_if_none(lambda: device_repo.set_value(ATO, False))
                
                logging.info(f"[{CONTEXT}] topped off {round(watervolume_topoff, 1)}L")
        
        old = now
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    utils.retry_if_none(lambda: device_repo.set_value(ATO, False))
    device_repo.close_connection()
    setting_repo.close_connection()
