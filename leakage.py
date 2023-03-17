from MCP3008 import MCP3008
import logging
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser

import sensor_repo as sr
import utils

CONTEXT = "leakage"
LEAKAGE_CHANNEL = 6
USER_ID = utils.read_secret("user_id")
REEF_ID = utils.read_secret("reef_id")

utils.setup_logging(CONTEXT)
repo = sr.sensor_repo()
adc = MCP3008()
token = None

try:    
    while True:
        measurement_ids = utils.retry_if_none(lambda: repo.get_sensor_measurement_ids())
        measurements = []
        while len(measurements) < 50:
            value = adc.read( channel = LEAKAGE_CHANNEL )
            measurements.append(value)
            time.sleep(0.1)
    
        measurements.sort()
        leakage = 100 - round(sum(measurements[10:40]) / (30 * 10.23), 2)
        
        if not leakage is None:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, leakage))
            
            if token == None or parser.parse(token['expiresAt']) < datetime.now(timezone.utc) + timedelta(hours = 1):
                token = utils.retry_if_none(lambda : utils.get_token_client_credentials(CONTEXT))
            
            now = datetime.utcnow().isoformat()
            utils.post_measurement(CONTEXT, token["accessToken"], USER_ID, REEF_ID, measurement_ids[CONTEXT], now, leakage)
        else:
            logging.warning(f"[{CONTEXT}] invalid measurement")
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    adc.close()
    repo.close_connection()
    
