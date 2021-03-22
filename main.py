import logging
import os
import time

import ambienttemperature
import relay
import watertemperature
import watervolume
import utils

def adjust_last_message(data):
    logging.info(f"{CONTEXT} ping received")
    global last_message
    last_message = time.time()
        
def joined_group(data):    
    if data[1] == "viewers" and not is_streaming:
        start_threads()
        logging.info(f"{CONTEXT} joined group: {data}")
        
def left_group(data):    
    if data[1] == "viewers":
        stop_threads()
        logging.info(f"{CONTEXT} left group: {data}")

def start_threads():
    set_streaming(True) 
    relay.start_thread(hub_connection)
    ambienttemperature.start_thread(hub_connection)
    watertemperature.start_thread(hub_connection)
    watervolume.start_thread(hub_connection)

def stop_threads():
    set_streaming(False)
    relay.stop_thread()
    ambienttemperature.stop_thread()
    watertemperature.stop_thread()
    watervolume.stop_thread()

def set_streaming(on):
    global is_streaming, start_streaming
    is_streaming = on
    if on:
        start_streaming = time.time()
    else:
        start_streaming = None

CONTEXT = "[main]"
REBOOT_AFTER_TIME_WITHOUT_CONNECTION = 900
STARTUP_TIME = 30
MAX_STREAMING_TIME = 180
PING_INTERVAL = 10

hub_connection = utils.create_hub_connection(CONTEXT)
last_message = time.time()
start_streaming = None
is_streaming = False

time.sleep(STARTUP_TIME)

utils.setup_logging("main")

try:    
    while utils.time_diff(last_message, time.time()) < REBOOT_AFTER_TIME_WITHOUT_CONNECTION:
               
        if is_streaming and utils.time_diff(start_streaming, time.time()) > MAX_STREAMING_TIME:
            stop_threads()
            
        try:
            hub_connection.send("ping", ["pong"])             
        except:
            logging.warning(f"{CONTEXT} cannot send signalR message")
            try:
                stop_threads()
                hub_connection.stop()
                hub_connection = utils.create_hub_connection(CONTEXT)
                hub_connection.on("ping", adjust_last_message)
                hub_connection.on("joinedGroup", joined_group)
                hub_connection.on("leftGroup", left_group)
                hub_connection.on("switchDevice", relay.add_switch_device)
                hub_connection.on("requestDeviceStatus", relay.add_device_status_request)
                hub_connection.start()
            except:
                logging.warning(f"{CONTEXT} signalR connection problem")
            
        time.sleep(PING_INTERVAL)
            
    logging.info(f"{CONTEXT} no messages received for {REBOOT_AFTER_TIME_WITHOUT_CONNECTION} seconds")
    logging.info(f"{CONTEXT} rebooting")
    
    os.system("sudo reboot")
except KeyboardInterrupt:
    pass
finally:
    hub_connection.stop()