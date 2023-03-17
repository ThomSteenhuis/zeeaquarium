from dateutil import parser
import datetime as dt
import glob
import logging
import pytz
import requests
import sqlite3
import time

from signalrcore.hub_connection_builder import HubConnectionBuilder

import connect_thread

BASE_DIR_TEMP = "/sys/bus/w1/devices"
SECRETS_DIR = "/home/pi/Desktop/zeeaquarium/secrets/"

def setup_logging(name):
    now = dt.datetime.now()
    logfile_name = "/home/pi/Desktop/zeeaquarium/logs/" + name + "/" + name + "_" + now.strftime("%d-%m-%Y %H:%M:%S") + ".log"
    logging.basicConfig(filename=logfile_name, filemode="w", level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def read_secret(filename):
    try:
        with open(SECRETS_DIR + filename + ".txt", "r") as f:
            lines = f.readlines()
            if not lines is None and isinstance(lines, list) and len(lines) == 1:
                return lines[0]
            
            logging.warning("[secrets] file corrupted")
    except IOError:
        logging.warning("[secrets] file not accessible")

def login_client_credentials():
    response = requests.post(
        read_secret("login_client_credentials_url"),
        json={
            "grantType": "client_credentials",
            "clientId": read_secret("login_client_id"),
            "clientSecret": read_secret("login_client_secret")
            }, timeout = 3)
    if response.status_code == 200:
        return response.json()
    raise requests.exceptions.ConnectionError()

def get_token_client_credentials(context):
    token = None
    while token is None:
        try:
            token = login_client_credentials()
        except requests.exceptions.RequestException:
            logging.warning(f"[{context}] connection error while logging in")
        time.sleep(1)
    
    return token

def post_measurement(token, userId, reefId, measurementId, timestamp, value):
    response = requests.post(
        "https://reef-tank-api.azurewebsites.net/measurement/value",
        json={
            "userId": userId,
            "reefId": reefId,
            "measurementId": measurementId,
            "timestamp": timestamp,
            "value": value
        }, headers = {'Authorization': 'Bearer ' + token})
    if response.status_code == 200:
        return "saved"
    return None

def login():
    response = requests.post(
        read_secret("login_url"),
        json={
            "username": read_secret("login_user"),
            "password": read_secret("login_password")
            }, timeout = 3)
    if response.status_code == 200:
        return response.json()["token"]
    raise requests.exceptions.ConnectionError()

def get_token(context):
    token = None
    while token is None:
        try:
            token = login()
        except requests.exceptions.RequestException:
            logging.warning(f"[{context}] connection error while logging in")
        time.sleep(1)
    
    return token

def get_command(context, command):
    url = read_secret("command_url")
    token = get_token(context)
    
    response = requests.get(f"{url}?command={command}", headers = {'Authorization': 'Bearer ' + token}, timeout = 3)
    if response.status_code == 200:
        return response.json()
    raise requests.exceptions.ConnectionError()

def command_sent(context, command_name, outdated_after):
    try:
        command = get_command(context, command_name)
        
        command_date = parser.parse(command["date"])
        outdated_after = dt.timedelta(seconds = outdated_after)
        now = pytz.utc.localize(dt.datetime.utcnow())
        
        return now - outdated_after < command_date
    except:
        logging.warning(f"[{context}] could not get {command_name} command via http")
        return False

def connect():
    thread = connect_thread.connect_thread()
    thread.start()

def print_measurement(data):
    print(f"{data}")
    
def empty_handler(data):
    pass

def create_hub_connection(context):
    hub_connection = HubConnectionBuilder()\
        .with_url(read_secret("hub_url"), options={ "access_token_factory": login })\
        .configure_logging(logging.DEBUG)\
        .build()
    
    hub_connection.on_open(lambda: logging.info(f"{context} signalR connection is now open"))
    hub_connection.on_close(lambda: logging.info(f"{context} signalR connection is now closed"))
    hub_connection.on_error(lambda data: logging.warning(f"{context} an exception was thrown: '{data.error}'"))
                               
    return hub_connection

def time_diff(start, end):
    return end - start

def parse_string_to_time(context, time_string):
    if time_string is None or not isinstance(time_string, str) or not len(time_string) == 4:
        logging.warning(f"[{context}] cannot parse {time_string} to time")
        return
    
    try:
        return dt.time(int(time_string[:2]), int(time_string[2:]))
    except ValueError:
        logging.warning(f"[{context}] cannot parse {time_string} to time")
        
def read_temp_raw(file, context):
    try:
        with open(file, "r") as f:
            return f.readlines()
    except IOError:
        logging.warning(f"{context} file not accessible")
        
def read_temp(index, context):
    try:
        device_folders = glob.glob(BASE_DIR_TEMP + "/28*")
        device_folders.sort()
        device_file = device_folders[index] + "/w1_slave"
        lines = read_temp_raw(device_file, context)
        if lines is None or not isinstance(lines, list) or len(lines) < 2 or lines[0].strip()[-3:] != "YES":
            logging.warning(f"{context} file is corrupted")
            return
        
        pos = lines[1].find("t=")
        if pos != -1:
            temp_string = lines[1][pos+2:]
            try:
                return float(temp_string) / 1000.0
            except ValueError:
                logging.warning(f"{context} not a floating point number")
                return
        
        logging.warning(f"{context} file is corrupted")
    except IndexError:
        logging.warning(f"{context} file does not exist")
        
def create_sql_connection(db_name, context):
    conn = None
    try:        
        conn = sqlite3.connect(db_name)
    except:
        logging.warning(f"{context} sql connection error")
    return conn

def get_db_row(cursor, table, column, value):
    cursor.execute("select * from " + table + " where " + column + " = '" + value + "'")
    return cursor.fetchone()

def insert_db_value(connection, table, id_column, id_value, column, value):
    cursor = connection.cursor()
    cursor.execute("update " + table + " set " + column + " = " + value + " where "+ id_column + " = " + id_value)
    connection.commit()
    
def retry_if_none(func, times = 3):
    outcome = None
    cnt = 0
    
    while outcome is None and cnt < times:
        outcome = func()
        cnt += 1
        time.sleep(0.1)
    
    return outcome
