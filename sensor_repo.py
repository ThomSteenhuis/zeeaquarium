import datetime as dt
import logging
import pytz
import sqlite3

import utils

DB_NAME = "/home/pi/zeeaquarium"
DB_SENSORS = "sensors"
DB_SENSOR_VALUES = "sensor_values"
MAX_SECONDS_OUTDATED = 60

class sensor_repo:
    def __init__(self, sensor_name):
        self.conn = utils.create_sql_connection(DB_NAME, f"[{sensor_name}]")
        self.sensor_name = sensor_name
        
        if self.conn:
            self.cursor = self.conn.cursor()
            
            self.cursor.execute(f"select * from {DB_SENSORS} where name = '{self.sensor_name}'")
            sensor_id_row = self.cursor.fetchone()
                    
            if sensor_id_row and len(sensor_id_row) == 2:
                self.sensor_id = sensor_id_row[0]
            else:
                logging.warning(f"[{self.sensor_name}] sensor id cannot be found in db")
        else:
            logging.warning(f"[{self.sensor_name}] db connection cannot be made")
    
    def get_value(self):
        if not self.cursor:
            logging.warning(f"[{self.sensor_name}] cursor not set")
            return
        if not self.sensor_id:
            logging.warning(f"[{self.sensor_name}] sensor_id not set")
            return
            
        self.cursor.execute(f"select * from {DB_SENSOR_VALUES} where id = '{self.sensor_id}'")
        sensor_value_row = self.cursor.fetchone()
        
        if not sensor_value_row or not len(sensor_value_row) == 3:
            logging.warning(f"[{self.sensor_name}] sensor value could not be found in db")
            return
        
        
        utc_timezone = pytz.timezone('Utc')
        value_datetime = utc_timezone.localize(dt.datetime.strptime(sensor_value_row[2], '%Y-%m-%d %H:%M:%S'))
        now = dt.datetime.now(pytz.utc)
        diff = now - value_datetime
        diff_in_s = diff.total_seconds()
        
        if diff_in_s < MAX_SECONDS_OUTDATED:
            return sensor_value_row[1]
        else:
            logging.warning(f"[{self.sensor_name}] sensor value in db is outdated")
    
    def set_value(self, value):
        if not self.cursor:
            logging.warning(f"[{self.sensor_name}] cursor not set")
            return
        if not self.sensor_id:
            logging.warning(f"[{self.sensor_name}] sensor_id not set")
            return
        if not value:            
            logging.warning(f"[{self.sensor_name}] illegal value")
            return
            
        try:
            self.cursor.execute(f"update {DB_SENSOR_VALUES} set value = {str(value)}, datetime = datetime('now') where id = {self.sensor_id}")
            self.conn.commit()
        except:
            logging.warning(f"[{self.sensor_name}] cannot insert measurement in db")

    def close_connection(self):
        self.conn.close()
        