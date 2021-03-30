import logging
import time
import threading

import sensor_repo as sr
import utils

class watervolume_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global thread
        repo = sr.sensor_repo(CONTEXT)
        
        while is_streaming:
            temp = repo.get_value()                                             
        
            if temp:                    
                try:
                    hub_connection.send("broadcastMeasurement", ["watertemperature", str(temp)])
                except:
                    logging.warning(f"[{CONTEXT}] cannot send signalR message")
            else:
                logging.warning(f"[{CONTEXT}] measurement could not be retrieved from repo")
            
            time.sleep(3)
        
        repo.close_connection()
        thread = None
        
CONTEXT = "watertemperature"
DB_NAME = "/home/pi/zeeaquarium"
DB_SENSORS = "sensors"
DB_SENSOR_VALUES = "sensor_values"

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
