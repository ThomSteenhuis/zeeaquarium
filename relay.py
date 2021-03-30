import RPi.GPIO as GPIO
import logging
import threading
import time

class relay_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        GPIO.setmode(GPIO.BOARD)
        
        GPIO.setup(PINS["relay2"]["pin"], GPIO.OUT)
        GPIO.setup(PINS["relay4"]["pin"], GPIO.OUT)
        GPIO.setup(PINS["relay6"]["pin"], GPIO.OUT)
        GPIO.setup(PINS["relay8"]["pin"], GPIO.OUT)
        
        for key in PINS:
            add_device_status_request([key])
      
    def run(self): 
        GPIO.setmode(GPIO.BOARD)
        
        while is_streaming:
            if len(pending_device_status_requests) > 0:
                send_device_status(pending_device_status_requests.pop(0))
            
            if len(pending_switch_devices) > 0:
                switch_data = pending_switch_devices.pop(0)
                switch_device(switch_data["device"], switch_data["on"])
                
            time.sleep(0.1)

CONTEXT = "[relay]"

PINS = {
    "relay2": { "pin": 33, "status": True },
    "relay4": { "pin": 31, "status": True },
    "relay6": { "pin": 29, "status": True },
    "relay8": { "pin": 15, "status": True },
}

hub_connection = None
is_streaming = False
pending_device_status_requests = []
pending_switch_devices = []

def start_thread(connection):
    global hub_connection, is_streaming
    hub_connection = connection
    is_streaming = True
    
    r = relay_thread()
    r.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False

def add_switch_device(data):
    pending_switch_devices.append({ "device": data[0], "on": data[1] })
    
def add_device_status_request(data):
    pending_device_status_requests.append(data[0])

def switch_device(device, on):
    if device in ["relay2", "relay4", "relay6", "relay8"]:
        switch(PINS[device], on)
        send_status(device, PINS[device])

def switch(pin, on):
    if on == "False":
        pin["status"] = False
        GPIO.output(pin["pin"], GPIO.LOW) # Off
    else:
        pin["status"] = True
        GPIO.output(pin["pin"], GPIO.HIGH) # On
        
def send_device_status(device):
    if device in ["relay2", "relay4", "relay6", "relay8"]:
        send_status(device, PINS[device])
        
def send_status(device, pin):
    try:
        hub_connection.send("deviceStatus", [device, str(pin["status"])])
    except ValueError:
        logging.warning(f"{CONTEXT} cannot send signalr message")
        
