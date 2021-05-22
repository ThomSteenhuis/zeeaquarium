import logging
import threading
import time

import setting_repo as setr

class setting_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
      
    def run(self):
        repo = setr.setting_repo()
        
        setting_names = []
        setting_values = {}
        for name in repo.get_setting_names():
            setting_names.append(name)
            
        while is_streaming:
            for name in setting_names:
                value = repo.get_value(name)
                
                if not value is None and value != setting_values.get(name):
                    add_setting_request([name])
                    setting_values[name] = value
                    
            if len(pending_setting_requests) > 0:
                setting = pending_setting_requests.pop(0)
                value = repo.get_value(setting)
                
                if value is None:
                    logging.warning(f"[{CONTEXT}] setting status of {setting} could not be retrieved from repository")
                else:
                    send_setting_value(setting, value)
            
            if len(pending_setting_changes) > 0:
                setting_data = pending_setting_changes.pop(0)
                
                repo.set_value(setting_data["setting"], setting_data["value"])
                    
                add_setting_request([setting_data["setting"]])
            
            time.sleep(0.1)
        
        repo.close_connection()

CONTEXT = "setting"

hub_connection = None
is_streaming = False
pending_setting_requests = []
pending_setting_changes = []

def start_thread(connection):
    global hub_connection, is_streaming
    hub_connection = connection
    is_streaming = True
    
    t = setting_thread()
    t.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False

def add_setting_change(data):
    pending_setting_changes.append({ "setting": data[0], "value": data[1] })
    
def add_setting_request(data):
    pending_setting_requests.append(data[0])
        
def send_setting_value(setting, value):
    try:
        hub_connection.send("setting", [setting, str(value)])
    except ValueError:
        logging.warning(f"[{CONTEXT}] cannot send signalr message")        
