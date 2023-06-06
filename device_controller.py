import RPi.GPIO as GPIO
import logging
import smbus
import time

import device_repo as dr
import utils

CONTEXT = "device_controller"

utils.setup_logging(CONTEXT)

repo = dr.device_repo()

bus = smbus.SMBus(1) # Rev 2 Pi uses 1
 
DEVICE = 0x20 # Device address (A0-A2)
IODIRA = 0x00 # Pin direction register
OLATA  = 0x14 # Register for outputs
GPIOA  = 0x12 # Register for inputs

def to_hexa_decimal(val1 = 0, val2 = 0, val3 = 0, val4 = 0, val5 = 0, val6 = 0, val7 = 0, val8 = 0):
    return val1 + (2 * val2) + (4 * val3) + (8 * val4) + (16 * val5) + (32 * val6) + (64 * val7) + (128 * val8)

def write_byte_data_to_bus(device, address, value, max_retries = 10):
    retry = True
    retryCount = 0
    while retry and retryCount <= max_retries:
        try:
            retry = False
            bus.write_byte_data(device, address, value)   
        except OSError:
            retry = True
            retryCount = retryCount + 1

pins = []
device_relays = utils.retry_if_none(lambda : repo.get_device_relays())
for device_relay in device_relays:
    name = utils.retry_if_none(lambda : repo.get_device_name(device_relay['device']))
    pins.append({ "name": name, "pin": utils.retry_if_none(lambda : repo.get_pin(name)), "default": utils.retry_if_none(lambda : repo.get_default(name)) })

bus_pins = [x for x in pins if x["pin"] > 100]
pins = [x for x in pins if x["pin"] <= 100]

try:
    bus_pin_defaults = {}
    for x in bus_pins:
        bus_pin_defaults[str(x["pin"] - 100)] = x["default"]
        
    default_hexa_decimal = to_hexa_decimal(bus_pin_defaults.get("1") or 0, bus_pin_defaults.get("2") or 0, bus_pin_defaults.get("3") or 0, bus_pin_defaults.get("4") or 0, bus_pin_defaults.get("5") or 0, bus_pin_defaults.get("6") or 0, bus_pin_defaults.get("7") or 0, bus_pin_defaults.get("8") or 0)

    # Set all GPA pins as outputs by setting all bits of IODIRA register to 0
    write_byte_data_to_bus(DEVICE, IODIRA, 0x00, 100)
    time.sleep(0.2)
    write_byte_data_to_bus(DEVICE, OLATA, 255 - default_hexa_decimal, 100)
    time.sleep(0.2)
    write_byte_data_to_bus(DEVICE, OLATA, default_hexa_decimal, 100)        
    
    GPIO.setmode(GPIO.BOARD)
    for p in pins:
        GPIO.setup(p["pin"], GPIO.OUT)
        time.sleep(0.2)
        if p["default"]:
            GPIO.output(p["pin"], GPIO.LOW)
            time.sleep(0.2)
            GPIO.output(p["pin"], GPIO.HIGH)
        else:
            GPIO.output(p["pin"], GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(p["pin"], GPIO.LOW)
        
    time.sleep(0.2)
    
    while True:
        for p in pins:
            value = utils.retry_if_none(lambda : repo.get_value(p["name"]))
        
            if value is None or not isinstance(value, bool):
                logging.warning(f"[{CONTEXT}] illegal value")
            else:
                if value and p["default"]:
                    GPIO.output(p["pin"], GPIO.LOW) # On:
                elif value and not p["default"]:
                    GPIO.output(p["pin"], GPIO.HIGH) # On
                elif not value and p["default"]:
                    GPIO.output(p["pin"], GPIO.HIGH) # Off
                else:
                    GPIO.output(p["pin"], GPIO.LOW) # Off
        
        # Set all GPA pins as outputs by setting all bits of IODIRA register to 0
        write_byte_data_to_bus(DEVICE, IODIRA, 0x00)
        
        bus_pin_outputs = {}
        for x in bus_pins:
            value = utils.retry_if_none(lambda : repo.get_value(x["name"]))
        
            if value is None or not isinstance(value, bool):
                logging.warning(f"[{CONTEXT}] illegal value")
            else:
                if value and x["default"]:
                    bus_pin_outputs[str(x["pin"] - 100)] = 0 # On
                elif value and not x["default"]:
                    bus_pin_outputs[str(x["pin"] - 100)] = 1 # On
                elif not value and x["default"]:
                    bus_pin_outputs[str(x["pin"] - 100)] = 1 # Off
                else:
                    bus_pin_outputs[str(x["pin"] - 100)] = 0 # Off
        
        value_hexa_decimal = to_hexa_decimal(bus_pin_outputs.get("1") or 0, bus_pin_outputs.get("2") or 0, bus_pin_outputs.get("3") or 0, bus_pin_outputs.get("4") or 0, bus_pin_outputs.get("5") or 0, bus_pin_outputs.get("6") or 0, bus_pin_outputs.get("7") or 0, bus_pin_outputs.get("8") or 0)
        write_byte_data_to_bus(DEVICE, OLATA, value_hexa_decimal)
        
        time.sleep(0.2)          
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
finally:
    repo.close_connection()
    for p in pins:
        GPIO.cleanup(p["pin"])
