import time
import device_repo as dr
import utils

device_repo = dr.device_repo()

pump_name = "doseerpomp_4"
time_dose = 60
    
utils.retry_if_none(lambda: device_repo.set_value(pump_name, True))

time.sleep(time_dose)

utils.retry_if_none(lambda: device_repo.set_value(pump_name, False))
