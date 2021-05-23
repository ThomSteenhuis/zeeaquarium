import logging
import os
import threading
import time

import device_repo as dr
import utils

class command_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
      
    def run(self):
        repo = dr.device_repo()
        
        while is_streaming:
            if reboot_triggered:
                os.system("sudo reboot")
            
            global feeding_mode_triggered
            if feeding_mode_triggered:
                feeding_mode_triggered = False
                
                utils.retry_if_none(lambda : repo.set_value("pomp_rechts", False))
                time.sleep(0.5)
                utils.retry_if_none(lambda : repo.set_value("pomp_links", False))
                
                time.sleep(120)
                
                utils.retry_if_none(lambda : repo.set_value("pomp_rechts", True))
                time.sleep(0.5)
                utils.retry_if_none(lambda : repo.set_value("pomp_links", True))
                break
            
            time.sleep(1)

        repo.close_connection()
        
CONTEXT = "command"

hub_connection = None
is_streaming = False
reboot_triggered = False
feeding_mode_triggered = False

def start_thread(connection):
    global hub_connection, is_streaming, reboot
    hub_connection = connection
    is_streaming = True
    
    r = command_thread()
    r.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
    
def reboot():
    logging.info(f"[{CONTEXT}] reboot triggered")
    global reboot_triggered
    reboot_triggered = True

def trigger_feeding_mode():
    logging.info(f"[{CONTEXT}] feeding mode triggered")
    global feeding_mode_triggered
    feeding_mode_triggered = True
