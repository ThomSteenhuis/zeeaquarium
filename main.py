import logging
import os
import time

import camera_thread
import command_thread
import relay_thread
import sensor_thread
import setting_thread
import utils

def adjust_last_message(data):
    logging.info(f"{CONTEXT} ping received")
    global last_message
    last_message = time.time()
        
def joined_group(data):    
    if data[1] == "watchers" and not is_streaming:
        start_threads()
        logging.info(f"{CONTEXT} joined group: {data}")
        
def left_group(data):    
    if data[1] == "watchers":
        stop_threads()
        logging.info(f"{CONTEXT} left group: {data}")

def invoke_command(data):
    if data[0] == "reboot":
        command_thread.reboot()
    elif data[0] == "feeding_mode":
        command_thread.trigger_feeding_mode()

def start_threads():
    set_streaming(True)
    camera_thread.start_thread(hub_connection)
    command_thread.start_thread(hub_connection)
    relay_thread.start_thread(hub_connection)
    sensor_thread.start_thread(hub_connection)
    setting_thread.start_thread(hub_connection)

def stop_threads():
    set_streaming(False)
    camera_thread.stop_thread()
    command_thread.stop_thread()
    relay_thread.stop_thread()
    sensor_thread.stop_thread()
    setting_thread.stop_thread()

def set_streaming(on):
    global is_streaming, start_streaming
    is_streaming = on
    if on:
        start_streaming = time.time()
    else:
        start_streaming = None

CONTEXT = "[main]"
REBOOT_AFTER_TIME_WITHOUT_CONNECTION = 450
STARTUP_TIME = 30
PAUZE_BEFORE_REBOOT = 30
MAX_STREAMING_TIME = 30
PING_INTERVAL = 10

try:
    hub_connection = utils.create_hub_connection(CONTEXT)
    last_message = time.time()
    start_streaming = None
    is_streaming = False

    time.sleep(STARTUP_TIME)

    utils.setup_logging("main")

    while utils.time_diff(last_message, time.time()) < REBOOT_AFTER_TIME_WITHOUT_CONNECTION:
               
        if is_streaming and utils.time_diff(start_streaming, time.time()) > MAX_STREAMING_TIME:
            stop_threads()
        
        utils.connect()
        
        try:
            hub_connection.send("ping", ["pong"])             
        except:
            logging.warning(f"{CONTEXT} cannot send signalR message")
            try:
                stop_threads()
                hub_connection.stop()
                hub_connection = utils.create_hub_connection(CONTEXT)
                hub_connection.on("ping", adjust_last_message)
                hub_connection.on("command", invoke_command)
                hub_connection.on("joinedGroup", joined_group)
                hub_connection.on("leftGroup", left_group)
                hub_connection.on("switchDevice", relay_thread.add_switch_device)
                hub_connection.on("requestDeviceStatus", relay_thread.add_device_status_request)
                hub_connection.on("setSetting", setting_thread.add_setting_change)
                hub_connection.on("requestSetting", setting_thread.add_setting_request)
                hub_connection.start()
            except:
                logging.warning(f"{CONTEXT} signalR connection problem")
            
        time.sleep(PING_INTERVAL)
            
    logging.info(f"{CONTEXT} no messages received for {REBOOT_AFTER_TIME_WITHOUT_CONNECTION} seconds")
    
    time.sleep(PAUZE_BEFORE_REBOOT)
    
    logging.info(f"{CONTEXT} rebooting")
    os.system("sudo reboot")
except KeyboardInterrupt:
    pass
except:
    logging.exception(f"{CONTEXT} general error")
    
    time.sleep(PAUZE_BEFORE_REBOOT)
    
    logging.info(f"{CONTEXT} rebooting")
    os.system("sudo reboot")
finally:
    stop_threads()
    hub_connection.stop()
    