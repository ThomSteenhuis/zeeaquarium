import datetime as dt
import logging
import requests
import os
import time

import camera_thread
import command_thread
import relay_thread
import sensor_thread
import setting_thread
import utils

def start_threads():
    set_streaming(True)
    camera_thread.start_thread()
    command_thread.start_thread()
    #relay_thread.start_thread()
    sensor_thread.start_thread()
    setting_thread.start_thread()

def stop_threads():
    set_streaming(False)
    camera_thread.stop_thread()
    command_thread.stop_thread()
    #relay_thread.stop_thread()
    sensor_thread.stop_thread()
    setting_thread.stop_thread()

def set_streaming(on):
    global is_streaming, start_streaming
    is_streaming = on
    if on:
        start_streaming = time.time()
    else:
        start_streaming = None

CONTEXT = "main"
STARTUP_TIME = 30
PAUZE_BEFORE_REBOOT = 30
MAX_STREAMING_TIME = 60
COMMAND_OUTDATED_AFTER = 60
CONNECT_INTERVAL = 1

try:
    start_streaming = None
    is_streaming = False

    time.sleep(STARTUP_TIME)

    utils.setup_logging("main")
    
    time.sleep(MAX_STREAMING_TIME)
    
    while True:
        utils.connect()
        
        if not is_streaming and utils.command_sent(CONTEXT, "stream", COMMAND_OUTDATED_AFTER):
            start_threads()
            
        if is_streaming and utils.time_diff(start_streaming, time.time()) > MAX_STREAMING_TIME:
            stop_threads()
        
        time.sleep(CONNECT_INTERVAL)
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"[{CONTEXT}] general error")
    
    time.sleep(PAUZE_BEFORE_REBOOT)
    
    logging.info(f"[{CONTEXT}] rebooting")
    os.system("sudo reboot")
finally:
    stop_threads()
    