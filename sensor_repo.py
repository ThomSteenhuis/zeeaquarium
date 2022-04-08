import datetime as dt
import logging
import pytz
import sqlite3

import utils

DB_NAME = "/home/pi/zeeaquarium"
DB_SENSORS = "sensors"
DB_SENSOR_VALUES = "sensor_values"
DB_SENSOR_RAW_VALUES = "sensor_raw_values"
DB_TEMP_SENSORS = "temp_sensors"
CONTEXT = "sensor_repo"

MAX_SECONDS_OUTDATED = 60

class sensor_repo:
    def __init__(self):
        self.conn = utils.create_sql_connection(DB_NAME, f"[{CONTEXT}]")
        
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            logging.warning(f"[{CONTEXT}] db connection cannot be made")
    
    def get_sensor_names(self):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        
        try:
            self.cursor.execute(f"select name from {DB_SENSORS};")
            sensor_names = self.cursor.fetchall()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            sensor_names = None
        
        if sensor_names:
            names = []
            for name in sensor_names:
                names.append(name[0])
                
            return names
        else:
            logging.warning(f"[{CONTEXT}] sensor names cannot be found in db")
            
    def get_temp_sensors(self):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        
        try:
            self.cursor.execute(f"select id, type from {DB_TEMP_SENSORS};")
            temp_sensors = self.cursor.fetchall()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            temp_sensors = None
        
        if temp_sensors:
            sensors = {}
            for sensor in temp_sensors:
                if len(sensor) == 2:
                    sensors[sensor[0]] = sensor[1]
                
            return sensors
        else:
            logging.warning(f"[{CONTEXT}] temp sensors cannot be found in db")
    
    def get_value(self, name, max_seconds_outdated = MAX_SECONDS_OUTDATED):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        
        try:
            self.cursor.execute(f"select value, datetime from {DB_SENSORS} left join {DB_SENSOR_VALUES} on {DB_SENSORS}.id = {DB_SENSOR_VALUES}.id where name = '{name}';")
            sensor_value_row = self.cursor.fetchone()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            sensor_value_row = None
        
        if not sensor_value_row or not len(sensor_value_row) == 2:
            logging.warning(f"[{CONTEXT}] sensor value of {name} could not be found in db")
            return        
        
        utc_timezone = pytz.timezone('Utc')
        try:
            value_datetime = utc_timezone.localize(dt.datetime.strptime(sensor_value_row[1], '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            logging.warning(f"[{CONTEXT}] sensor value datetime of {name} in db does not have correct format")
            return
        
        now = dt.datetime.now(pytz.utc)
        diff = now - value_datetime
        diff_in_s = diff.total_seconds()
        
        if max_seconds_outdated == 0 or diff_in_s < max_seconds_outdated:
            return sensor_value_row[0]
        else:
            logging.warning(f"[{CONTEXT}] sensor value of {name} in db is outdated")
    
    def get_raw_value(self, name, max_seconds_outdated = MAX_SECONDS_OUTDATED):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        
        try:
            self.cursor.execute(f"select value, datetime from {DB_SENSORS} left join {DB_SENSOR_RAW_VALUES} on {DB_SENSORS}.id = {DB_SENSOR_RAW_VALUES}.id where name = '{name}';")
            sensor_value_row = self.cursor.fetchone()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            sensor_value_row = None
        
        if not sensor_value_row or not len(sensor_value_row) == 2:
            logging.warning(f"[{CONTEXT}] sensor raw value of {name} could not be found in db")
            return        
        
        utc_timezone = pytz.timezone('Utc')
        try:
            value_datetime = utc_timezone.localize(dt.datetime.strptime(sensor_value_row[1], '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            logging.warning(f"[{CONTEXT}] sensor raw value datetime of {name} in db does not have correct format")
            return
        
        now = dt.datetime.now(pytz.utc)
        diff = now - value_datetime
        diff_in_s = diff.total_seconds()
        
        if max_seconds_outdated == 0 or diff_in_s < max_seconds_outdated:
            return sensor_value_row[0]
        else:
            logging.warning(f"[{CONTEXT}] sensor raw value of {name} in db is outdated")
    
    def set_value(self, name, value):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:            
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        if value is None:            
            logging.warning(f"[{CONTEXT}] illegal value")
            return
        
        try:
            self.cursor.execute(f"select id from {DB_SENSORS} where name = '{name}';")
            sensor_id = self.cursor.fetchone()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            sensor_id = None
        
        if not sensor_id or not len(sensor_id) == 1:
            logging.warning(f"[{CONTEXT}] sensor {name} could not be found in db")
            return
        
        try:
            self.cursor.execute(f"update {DB_SENSOR_VALUES} set value = {str(value)}, datetime = datetime('now') where id = {sensor_id[0]}")
            self.conn.commit()
            return True
        except:
            logging.warning(f"[{CONTEXT}] cannot insert measurement in db")

    def set_raw_value(self, name, value):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:            
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        if not value:            
            logging.warning(f"[{CONTEXT}] illegal value")
            return
        
        try:
            self.cursor.execute(f"select id from {DB_SENSORS} where name = '{name}';")
            sensor_id = self.cursor.fetchone()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            sensor_id = None
        
        if not sensor_id or not len(sensor_id) == 1:
            logging.warning(f"[{CONTEXT}] sensor {name} could not be found in db")
            return
        
        try:
            self.cursor.execute(f"update {DB_SENSOR_RAW_VALUES} set value = {str(value)}, datetime = datetime('now') where id = {sensor_id[0]}")
            self.conn.commit()
            return True
        except:
            logging.warning(f"[{CONTEXT}] cannot insert raw measurement in db")
            
    def close_connection(self):
        self.conn.close()
