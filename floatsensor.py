from ADS1115 import ADS1115
import logging
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
adc = ADS1115()
token = None

try:    
    while True:
        measurement_ids = utils.retry_if_none(lambda: repo.get_sensor_measurement_ids())
        measurements = []
        while len(measurements) < 600:
            value = adc.read( channel = CHANNEL )
            measurements.append(value)
            time.sleep(0.1)
            
        measurements.sort()
        avg = round(sum(measurements[150:450]) / 300, 2)
            
        if avg < THRESHOLD:
            high_level = 1. 
        else:
            high_level = 0.
            
        utils.retry_if_none(lambda : repo.set_value(CONTEXT, high_level))
            
        if token == None or parser.parse(token['expiresAt']) < datetime.now(timezone.utc) + timedelta(hours = 1):
            token = utils.retry_if_none(lambda : utils.get_token_client_credentials(CONTEXT))
        print(high_level)
        now = datetime.utcnow().isoformat()
        utils.post_measurement(CONTEXT, token["accessToken"], USER_ID, REEF_ID, measurement_ids[CONTEXT], now, high_level)
        
        time.sleep(0.1)    
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()
    