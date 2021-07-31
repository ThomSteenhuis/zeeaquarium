import logging
import requests
import threading
import time

import device_repo as dr
import utils

class relay_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
      
    def run(self):
        url = utils.read_secret("switch_url")
        token = utils.get_token(CONTEXT)
        repo = dr.device_repo()
        
        switch_names = []
        switch_statuses = {}
        
        for name in utils.retry_if_none(lambda : repo.get_device_names()):
            switch_names.append(name)
            
        while is_streaming:
            for name in switch_names:
                value = utils.retry_if_none(lambda : repo.get_value(name))
                if not value is None and value != switch_statuses.get(name):
                    post_switch_status(url, token, name, value)
                    switch_statuses[name] = value                
                
                switch_status = get_switch_status(url, token, name)
                if not switch_status is None and switch_status["value"] != switch_statuses.get(name):
                    utils.retry_if_none(lambda : repo.set_value(name, switch_status["value"]))
                    switch_statuses[name] = value
                
            time.sleep(1)
        
        repo.close_connection()

CONTEXT = "relay"

is_streaming = False

def start_thread():
    global is_streaming
    is_streaming = True
    
    r = relay_thread()
    r.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False

def get_switch_status(url, token, name):
    try:
        r = requests.get(f"{url}?deviceSwitch={name}", headers = {'Authorization': 'Bearer ' + token}, timeout = 3)
        if r.status_code == 200:
            return r.json()
        
        logging.warning(f"[{CONTEXT}] could not get {name} switch status via http")
    except requests.exceptions.RequestException:
        logging.warning(f"[{CONTEXT}] connection error while getting switch status")

def post_switch_status(url, token, name, value):    
    try:
        r = requests.post(url, json = {"switch": name, "value": value}, headers = {'Authorization': 'Bearer ' + token}, timeout = 3) 
        
        if r.status_code != 200:
            logging.warning(f"[{CONTEXT}] could not post {name} switch status via http")
    except requests.exceptions.RequestException:
        logging.warning(f"[{CONTEXT}] connection error while posting switch status")    
