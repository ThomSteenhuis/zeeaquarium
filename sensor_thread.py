import logging
import requests
import time
import threading

import sensor_repo as sr
import utils

class sensor_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global thread
        
        repo = sr.sensor_repo()
        
        token = utils.get_token(CONTEXT)
        url = utils.read_secret("measurement_url")
        
        while is_streaming:
            sensor_names = utils.retry_if_none(lambda : repo.get_sensor_names())
            
            for name in sensor_names:
                value = utils.retry_if_none(lambda : repo.get_value(name))
        
                if value:
                    try:
                        r = requests.post(url, json = {"measurement": name, "value": value}, headers = {'Authorization': 'Bearer ' + token} ) 
                        
                        if r.status_code != 200:
                            logging.warning(f"[{CONTEXT}] cannot post screenshot via http")
                    except requests.exceptions.RequestException:
                        logging.warning(f"[{CONTEXT}] connection error while posting screenshot")
                else:
                    logging.warning(f"[{CONTEXT}] measurement {name} could not be retrieved from repo")
            
            time.sleep(3)
        
        repo.close_connection()
        thread = None
        
CONTEXT = "sensor"

is_streaming = False
thread = None

def start_thread():
    global is_streaming, thread
    is_streaming = True
    
    if thread is None:
        thread = sensor_thread()
        thread.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
