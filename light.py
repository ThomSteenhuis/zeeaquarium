from MCP3008 import MCP3008
import threading
import time

class light_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global thread
        adc = MCP3008()

        while is_streaming:
            measurements = []
            while is_streaming and len(measurements) < 300:
                value = adc.read( channel = LIGHT_CHANNEL )
                measurements.append(value)
                time.sleep(0.01)
        
            measurements.sort()
            light = round(sum(measurements[75:225]) / (150 * 10.23), 2)
            
            if not light is None:
                try:
                    hub_connection.send("broadcastMeasurement", ["light", str(light)])
                except:
                    logging.warning(f"{CONTEXT} cannot send signalR message")
        
        adc.close()
        thread = None

CONTEXT = "[light]"
LIGHT_CHANNEL = 7

hub_connection = None
is_streaming = False
thread = None

def start_thread(connection):
    global hub_connection, is_streaming, thread
    hub_connection = connection
    is_streaming = True
    
    if thread is None:
        thread = light_thread()
        thread.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
