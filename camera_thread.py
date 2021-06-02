import datetime as dt
import io
import logging
import math
import picamera
import requests
import time
import threading

import utils

class camera_thread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global thread
        
        token = None
        while token is None:
            try:
                token = utils.login()
            except requests.exceptions.RequestException:
                logging.warning(f"[{CONTEXT}] connection error while logging in")
            time.sleep(1)
        
        url = utils.read_secret("screenshot_url")
        
        with picamera.PiCamera() as camera:
            camera.resolution = (320, 240)
            camera.vflip = True            
            camera.annotate_text_size = 6
            
            camera.start_preview()
            time.sleep(2) # Camera warm-up time
        
            while is_streaming:
                video_stream = io.BytesIO()
                camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                camera.capture(video_stream, format = 'jpeg')
                
                byte_array = list(video_stream.getvalue())
                
                try:
                    r = requests.post(url, json = {"screenshot": byte_array}, headers = {'Authorization': 'Bearer ' + token} ) 
                    
                    if r.status_code != 200:
                        logging.warning(f"[{CONTEXT}] cannot post screenshot via http")
                except requests.exceptions.RequestException:
                    logging.warning(f"[{CONTEXT}] connection error while posting screenshot")
        
            camera.stop_preview()
        
        thread = None
        
CONTEXT = "camera"

hub_connection = None
is_streaming = False
thread = None

def start_thread(connection):
    global hub_connection, is_streaming, thread
    hub_connection = connection
    is_streaming = True
    
    if thread is None:
        thread = camera_thread()
        thread.start()
    
def stop_thread():
    global is_streaming
    is_streaming = False
