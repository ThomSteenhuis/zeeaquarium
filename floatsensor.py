from ADS1115 import ADS1115
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser

import sensor_repo as sr
import utils

CONTEXT = "vlotter"
CHANNEL = 8
THRESHOLD = 25000
USER_ID = utils.read_secret("user_id")
REEF_ID = utils.read_secret("reef_id")

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()
ads = ADS1115()
token = None

try:
    high_level_cnt = 0;
    
    while True:
        measurement_ids = utils.retry_if_none(lambda: repo.get_sensor_measurement_ids())
        value = ads.read( channel = CHANNEL )
        if value < THRESHOLD:
            high_level_cnt += 1
        else:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, "0"))                
            high_level_cnt = 0
            
            if token == None or parser.parse(token['expiresAt']) < datetime.now(timezone.utc) + timedelta(hours = 1):
                token = utils.retry_if_none(lambda : utils.get_token_client_credentials(CONTEXT))
            
            now = datetime.utcnow().isoformat()
            utils.retry_if_none(lambda : utils.post_measurement(token["accessToken"], USER_ID, REEF_ID, measurement_ids[CONTEXT], now, 0))
            
            time.sleep(5)
        
        if high_level_cnt > 100:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, "1"))             
            high_level_cnt = 0
            
            if token == None or parser.parse(token['expiresAt']) < datetime.now(timezone.utc) + timedelta(hours = 1):
                token = utils.retry_if_none(lambda : utils.get_token_client_credentials(CONTEXT))
            
            now = datetime.utcnow().isoformat()
            utils.post_measurement(CONTEXT, token["accessToken"], USER_ID, REEF_ID, measurement_ids[CONTEXT], now, 1)
        
        time.sleep(0.1)    
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()
    