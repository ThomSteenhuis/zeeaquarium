import logging
import requests
import threading
import time

import utils

class connect_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        try:
            token = utils.login()
            
            url = utils.read_secret("connection_url")
            
            r = requests.post(url, headers = {'Authorization': 'Bearer ' + token}, timeout = 3)
            
            if r.status_code != 200:
                logging.warning(f"{CONTEXT} cannot connect via http")
        except requests.exceptions.RequestException:
            logging.warning(f"[{CONTEXT}] connection error")

CONTEXT = "connect"
