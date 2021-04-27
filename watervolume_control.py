import datetime as dt
import logging
import time

import device_repo as dr
import sensor_repo as sr
import setting_repo as setr
import utils

CONTEXT = "watervolume_control"
ATO = "ato"
WATER_TOPOFF_AT = "water_bijvul_tijdstip"
WATERVOLUME_TARGET = "watervolume_streefwaarde"
WATERVOLUME_AVG = "watervolume_avg"
WATERVOLUME_RESERVOIR = "watervolume_reservoir"
MAX_TOPOFF_VOLUME = 2
VOLUME_PM_20 = 1
VOLUME_PM_10 = 0.8

utils.setup_logging(CONTEXT)
device_repo = dr.device_repo()
sensor_repo = sr.sensor_repo()
setting_repo = setr.setting_repo()

old = dt.datetime.now().time()

try:
    while True:
        water_topoff_at = utils.parse_string_to_time(CONTEXT, setting_repo.get_value(WATER_TOPOFF_AT))
        now = dt.datetime.now().time()
        
        if True:
            watervolume_target = float(setting_repo.get_value(WATERVOLUME_TARGET))
            watervolume_current = float(sensor_repo.get_value(WATERVOLUME_AVG, 3600))
            watervolume_reservoir = float(sensor_repo.get_value(WATERVOLUME_RESERVOIR, 3600))
            
            if not watervolume_target or not watervolume_current:
                continue
            
            watervolume_topoff = min(2, watervolume_target - watervolume_current)
            
            if watervolume_topoff <= 0 or watervolume_reservoir < 2 or watervolume > 22:
                continue
            
            time_topoff = 60 * watervolume_topoff / (watervolume_reservoir * (VOLUME_PM_20 - VOLUME_PM_10) / 10 + 2 * VOLUME_PM_10 - VOLUME_PM_20)
            
            device_repo.set_value(ATO, True)            
            time.sleep(time_topoff)
            device_repo.set_value(ATO, False)
        
        old = now
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    logging.error(f"[{CONTEXT}] unknown error")
finally:
    device_repo.set_value(ATO, False)
    device_repo.close_connection()
    setting_repo.close_connection()
