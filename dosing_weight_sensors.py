import RPi.GPIO as GPIO
from hx711 import HX711
import logging
import time
import sys

import sensor_repo as sr
import setting_repo as setr
import utils

CONTEXT = "dosing_weight_sensors"

utils.setup_logging(CONTEXT)
sensor_repo = sr.sensor_repo()
setting_repo = setr.setting_repo()

try:
    sensor_defs = utils.retry_if_none(lambda : sensor_repo.get_weight_sensors())
    
    if sensor_defs is None:
        logging.warning(f"[{CONTEXT}] weight sensors could not be retrieved from repo")
    
    weight_sensors = {}
    for sensor in sensor_defs.items():    
        hx = HX711(sensor[1].get("pin_dout"), sensor[1].get("pin_sck"))

        hx.set_reading_format("MSB", "MSB")
        hx.set_reference_unit(sensor[1].get("ref"))

        hx.reset()
        hx.tare_A()
        hx.tare_B()
        
        weight_sensors[sensor[0]] = { "hx": hx, "restarted": True }

    while True:
        for sensor in weight_sensors.items():   
            measurements = []
            while len(measurements) < 100:
                measurements.append(sensor[1].get("hx").get_weight_A(5))
                
                sensor[1].get("hx").power_down()
                sensor[1].get("hx").power_up()
                time.sleep(0.1)
            
            if len(measurements) == 100:
                measurements.sort()
                if abs(measurements[30] - measurements[69]) > 1:
                    continue
                
                value = sum(measurements[30:70]) / len(measurements[30:70])
                
                cur_raw_value = utils.retry_if_none(lambda : sensor_repo.get_value(f"dosing_pump_{sensor[0]}_weight_raw", 3600)) or "0.0"
                cur_value = utils.retry_if_none(lambda : sensor_repo.get_value(f"dosing_pump_{sensor[0]}_weight", 3600)) or "0.0"
                
                utils.retry_if_none(lambda : sensor_repo.set_value(f"dosing_pump_{sensor[0]}_weight_raw", str(value)))
                
                if not sensor[1].get("restarted"):
                    diff = value - float(cur_raw_value)
                    if diff > 50:
                        initial_value = utils.retry_if_none(lambda : setting_repo.get_value(f"dosing_pump_{sensor[0]}_initial_weight")) or "0.0"
                        utils.retry_if_none(lambda : sensor_repo.set_value(f"dosing_pump_{sensor[0]}_weight", initial_value))
                    else:
                        utils.retry_if_none(lambda : sensor_repo.set_value(f"dosing_pump_{sensor[0]}_weight", str(float(cur_value) + diff)))
                
                sensor[1]["restarted"] = False
        
            time.sleep(0.1)

except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    sensor_repo.close_connection()
    setting_repo.close_connection()
