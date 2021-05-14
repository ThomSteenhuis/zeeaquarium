import logging
import pytz
import sqlite3

import utils

DB_NAME = "/home/pi/zeeaquarium"
DB_DEVICES = "devices"
DB_DEVICE_RELAY = "device_relay"
DB_DEVICE_VALUES = "device_values"
DB_RELAY_DEFAULT = "relay_default"
DB_RELAY_PIN = "relay_pin"
DB_RELAY_SENSORS = "relay_sensor_channel"
CONTEXT = "device_repo"

class device_repo:
    def __init__(self):
        self.conn = utils.create_sql_connection(DB_NAME, f"[{CONTEXT}]")
        
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            logging.warning(f"[{CONTEXT}] db connection cannot be made")
    
    def get_device_name(self, device):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not device:
            logging.warning(f"[{CONTEXT}] illegal device")
            return
        
        self.cursor.execute(f"select name from {DB_DEVICES} where id = {device};")
        device_name = self.cursor.fetchone()
        
        if device_name and len(device_name) == 1:
            return device_name[0]
        else:
            logging.warning(f"[{CONTEXT}] device name cannot be found in db")  
    
    def get_device_names(self):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        
        self.cursor.execute(f"select name from {DB_DEVICES};")
        device_names = self.cursor.fetchall()
        
        if device_names:
            names = []
            for name in device_names:
                names.append(name[0])
                
            return names
        else:
            logging.warning(f"[{CONTEXT}] device names cannot be found in db")  
        
    def get_default(self, name):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        
        relay = self.get_relay(name)
        self.cursor.execute(f"select default_value from {DB_RELAY_DEFAULT} where relay = {relay};")
        pin = self.cursor.fetchone()
        
        if pin and len(pin) == 1:
            return pin[0]
        else:
            logging.warning(f"[{CONTEXT}] pin cannot be found in db")
        
    def get_pin(self, name):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        
        relay = self.get_relay(name)
        self.cursor.execute(f"select pin from {DB_RELAY_PIN} where relay = {relay};")
        pin = self.cursor.fetchone()
        
        if pin and len(pin) == 1:
            return pin[0]
        else:
            logging.warning(f"[{CONTEXT}] pin cannot be found in db")
            
    def get_relay(self, name):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        
        self.cursor.execute(f"select relay from {DB_DEVICES} left join {DB_DEVICE_RELAY} on {DB_DEVICES}.id = {DB_DEVICE_RELAY}.id where name = '{name}';")
        device_relay = self.cursor.fetchone()
        
        if device_relay and len(device_relay) == 1:
            return device_relay[0]
        else:
            logging.warning(f"[{CONTEXT}] device relay cannot be found in db")
            
    def get_device(self, relay):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not relay:
            logging.warning(f"[{CONTEXT}] illegal relay")
            return
        
        self.cursor.execute(f"select id from {DB_DEVICE_RELAY} where relay = {relay};")
        device = self.cursor.fetchone()
        
        if device and len(device) == 1:
            return device[0]
        else:
            logging.warning(f"[{CONTEXT}] device cannot be found in db")
            
    def get_relay_sensors(self):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        
        self.cursor.execute(f"select * from {DB_RELAY_SENSORS};")
        relay_sensors = self.cursor.fetchall()
        
        if relay_sensors:
            sensors = []
            for sensor in relay_sensors:
                if len(sensor) == 2:
                    sensors.append({ 'relay': sensor[0], 'channel': sensor[1] })
                else:
                    logging.warning(f"[{CONTEXT}] relay sensors have incorrect format in db") 
                
            return sensors
        else:
            logging.warning(f"[{CONTEXT}] relay sensors cannot be found in db") 
        
    def get_value(self, name):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        
        self.cursor.execute(f"select value from {DB_DEVICES} left join {DB_DEVICE_VALUES} on {DB_DEVICES}.id = {DB_DEVICE_VALUES}.id where name = '{name}';")
        device_value = self.cursor.fetchone()
        
        if device_value and len(device_value) == 1:
            if device_value[0] == 0:
                return False
            else:
                return True
        else:
            logging.warning(f"[{CONTEXT}] device value cannot be found in db")
            
    def set_value(self, name, value):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name or not isinstance(name, str):
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        if value is None or not isinstance(value, bool):            
            logging.warning(f"[{CONTEXT}] illegal value")
            return
        
        self.cursor.execute(f"select id from {DB_DEVICES} where name = '{name}';")
        device_id = self.cursor.fetchone()
        
        if not device_id or not len(device_id) == 1:
            logging.warning(f"[{CONTEXT}] device {name} could not be found in db")
            return            
        
        try:
            val = 0 if not value else 1
            
            self.cursor.execute(f"update {DB_DEVICE_VALUES} set value = {val} where id = '{device_id[0]}'")
            self.conn.commit()
        except:
            logging.warning(f"[{CONTEXT}] cannot insert device value in db")

    def close_connection(self):
        self.conn.close()
        