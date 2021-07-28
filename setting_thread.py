import logging
import requests
import threading
import time

import setting_repo as setr
import utils

class setting_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
      
    def run(self):
        token = utils.get_token(CONTEXT)
        repo = setr.setting_repo()
        
        setting_names = []
        setting_values = {}
        
        for name in utils.retry_if_none(lambda : repo.get_setting_names()):
            setting_names.append(name)
            value = utils.retry_if_none(lambda : repo.get_value(name))
            setting_values[name] = value
            post_setting(token, name, value)
            
        while is_streaming:
            for name in setting_names:
                setting = get_setting(token, name)
                if not setting is None and setting.get("value") != setting_values.get(name):
                    utils.retry_if_none(lambda : repo.set_value(name, setting["value"]))
                    setting_values[name] = value
            
            time.sleep(1)
        
        repo.close_connection()

CONTEXT = "setting"
SETTING_OUTDATED_AFTER = 60

is_streaming = False

def start_thread():
    global is_streaming
    is_streaming = True
    
    t = setting_thread()
    t.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False  

def get_setting(token, name):
    url = utils.read_secret("setting_url")
    
    try:
        r = requests.get(f"{url}?setting={name}", headers = {'Authorization': 'Bearer ' + token}, timeout = 3)
        if r.status_code == 200:
            return r.json()
        
        logging.warning(f"[{CONTEXT}] could not get {name} setting via http")
    except requests.exceptions.RequestException:
        logging.warning(f"[{CONTEXT}] connection error while getting setting")

def post_setting(token, name, value):
    url = utils.read_secret("setting_url")
    
    try:
        r = requests.post(url, json = {"setting": name, "value": value}, headers = {'Authorization': 'Bearer ' + token}, timeout = 3) 
        
        if r.status_code != 200:
            logging.warning(f"[{CONTEXT}] could not post {name} setting via http")
    except requests.exceptions.RequestException:
        logging.warning(f"[{CONTEXT}] connection error while posting setting")
