import os
import logging
import time
import threading

import utils

os.system("modprobe w1_gpio")
os.system("modprobe w1_therm")

class watervolume_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        
    def run(self):
        global thread
        
        while is_streaming:
            temp = utils.read_temp(0, CONTEXT)
        
            if not temp is None:
                try:
                    hub_connection.send("broadcastMeasurement", ["watertemperature", str(temp)])
                except:
                    logging.warning(f"{CONTEXT} cannot send signalR message")
            
            time.sleep(3)
        
        thread = None
        
CONTEXT = "[watertemperature]"

hub_connection = None
is_streaming = False
thread = None

def start_thread(connection):
    global hub_connection, is_streaming, thread
    hub_connection = connection
    is_streaming = True
    
    if thread is None:
        thread = watervolume_thread()
        thread.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
