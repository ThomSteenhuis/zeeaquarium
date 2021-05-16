import os
import threading
import time

class reboot_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
      
    def run(self):
        while is_streaming:
            if reboot_triggered:
                os.system("sudo reboot")
            
            time.sleep(1)

CONTEXT = "reboot"

hub_connection = None
is_streaming = False
reboot_triggered = False

def start_thread(connection):
    global hub_connection, is_streaming, reboot
    hub_connection = connection
    is_streaming = True
    
    r = reboot_thread()
    r.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
    
def reboot():
    global reboot_triggered
    reboot_triggered = True
