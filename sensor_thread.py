import logging
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
        
        while is_streaming:
            sensor_names = repo.get_sensor_names()
            
            for name in sensor_names:
                value = repo.get_value(name)
        
                if value:                    
                    try:
                        hub_connection.send("broadcastMeasurement", [name, str(value)])
                    except:
                        logging.warning(f"[{CONTEXT}] cannot send signalR message")
                else:
                    logging.warning(f"[{CONTEXT}] measurement {name} could not be retrieved from repo")
            
            time.sleep(3)
        
        repo.close_connection()
        thread = None
        
CONTEXT = "sensor_repo"
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
        thread = sensor_thread()
        thread.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
