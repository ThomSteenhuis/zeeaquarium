from MCP3008 import MCP3008
import logging
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser

import sensor_repo as sr
import utils

CONTEXT = "light"
LIGHT_CHANNEL = 7
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
        while len(measurements) < 300:
            value = adc.read( channel = LIGHT_CHANNEL )
            measurements.append(value)
            time.sleep(0.01)
    
        measurements.sort()
        light = round(sum(measurements[75:225]) / (150 * 10.23), 2)
        
        if not light is None:
            utils.retry_if_none(lambda : repo.set_value(CONTEXT, light))
            
            if token == None or parser.parse(token['expiresAt']) < datetime.now(timezone.utc) + timedelta(hours = 1):
                token = utils.retry_if_none(lambda : utils.get_token_client_credentials(CONTEXT))
            
            now = datetime.utcnow().isoformat()
            utils.post_measurement(CONTEXT, token["accessToken"], USER_ID, REEF_ID, measurement_ids[CONTEXT], now, light)
        else:
            logging.warning(f"[{CONTEXT}] invalid measurement")
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    adc.close()
    repo.close_connection()
    