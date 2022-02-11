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
            if utils.command_sent(CONTEXT, "reboot", COMMAND_OUTDATED_AFTER):
                logging.info(f"[{CONTEXT}] reboot triggered")
                os.system("sudo reboot")
            
            time.sleep(1)

        repo.close_connection()
        
CONTEXT = "command"
COMMAND_OUTDATED_AFTER = 60

is_streaming = False

def start_thread():
    global is_streaming, reboot
    is_streaming = True
    
    r = command_thread()
    r.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
