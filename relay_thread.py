import logging
import threading
import time

import device_repo as dr

class relay_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
      
    def run(self):
        repo = dr.device_repo()
        
        device_names = []
        device_statuses = {}
        for name in repo.get_device_names():
            device_names.append(name)
            
        while is_streaming:
            for name in device_names:
                value = repo.get_value(name)
                
                if not value is None and value != device_statuses.get(name):
                    add_device_status_request([name])
                    device_statuses[name] = value
                    
            if len(pending_device_status_requests) > 0:
                device = pending_device_status_requests.pop(0)
                status = repo.get_value(device)
                
                if status is None:
                    logging.warning(f"[{CONTEXT}] device status of {device} could not be retrieved from controller")
                else:
                    send_device_status(device, status)
            
            if len(pending_switch_devices) > 0:
                switch_data = pending_switch_devices.pop(0)
                
                on = switch_data["on"] != "False"
                repo.set_value(switch_data["device"], on)
                    
                add_device_status_request([switch_data["device"]])
            
            time.sleep(0.1)
        
        repo.close_connection()

CONTEXT = "relay"

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
        
def send_device_status(device, status):
    try:
        hub_connection.send("deviceStatus", [device, str(status)])
    except ValueError:
        logging.warning(f"[{CONTEXT}] cannot send signalr message")        
