import RPi.GPIO as GPIO
from hx711 import HX711
import logging
import time
import sys

import sensor_repo as sr
import utils

CONTEXT = "dosing_weight_sensors"
PIN_DOUT = 38
PIN_PD_SCK = 40
REF_UNIT = -1938

utils.setup_logging(CONTEXT)
sensor_repo = sr.sensor_repo()

try:
    hx = HX711(PIN_DOUT, PIN_PD_SCK)

    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(REF_UNIT)

    hx.reset()
    hx.tare_A()
    hx.tare_B()

    while True:        
        measurements = []
        while len(measurements) < 100:

            measurements.append(hx.get_weight_A(5))
            
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)
        
        if len(measurements) == 100:
            measurements.sort()
            if abs(measurements[20] - measurements[79]) > 1:
                continue
            
            value = sum(measurements[20:80]) / len(measurements[20:80])
            
            cur_raw_value = utils.retry_if_none(lambda : sensor_repo.get_value(f"dosing_pump_1_weight_raw")) or 0
            cur_value = utils.retry_if_none(lambda : sensor_repo.get_value(f"dosing_pump_1_weight")) or 0
            
            utils.retry_if_none(lambda : sensor_repo.set_value(f"dosing_pump_1_weight_raw", str(value)))
            
            diff = value - float(cur_raw_value)
            if diff > 50:
                utils.retry_if_none(lambda : sensor_repo.set_value(f"dosing_pump_1_weight", str(diff)))
            else:
                utils.retry_if_none(lambda : sensor_repo.set_value(f"dosing_pump_1_weight", str(float(cur_value) + diff)))
        
        time.sleep(0.1)

except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    sensor_repo.close_connection()    
