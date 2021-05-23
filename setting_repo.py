import logging
import sqlite3

import utils

DB_NAME = "/home/pi/zeeaquarium"
DB_SETTINGS = "settings"
DB_SETTING_VALUES = "setting_values"
CONTEXT = "setting_repo"

class setting_repo:
    def __init__(self):
        self.conn = utils.create_sql_connection(DB_NAME, f"[{CONTEXT}]")
        
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            logging.warning(f"[{CONTEXT}] db connection cannot be made")
    
    def get_setting_names(self):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        
        try:
            self.cursor.execute(f"select name from {DB_SETTINGS};")
            setting_names = self.cursor.fetchall()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            setting_names = None
        
        if setting_names:
            names = []
            for name in setting_names:
                names.append(name[0])
                
            return names
        else:
            logging.warning(f"[{CONTEXT}] setting names cannot be found in db")
            
    def get_value(self, name):
        if not self.cursor:
            logging.warning(f"[{CONTEXT}] cursor not set")
            return
        if not name:
            logging.warning(f"[{CONTEXT}] illegal name")
            return
        
        try:
            self.cursor.execute(f"select value from {DB_SETTINGS} left join {DB_SETTING_VALUES} on {DB_SETTINGS}.id = {DB_SETTING_VALUES}.id where name = '{name}';")
            setting_value_row = self.cursor.fetchone()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            setting_value_row = None
        
        if setting_value_row and len(setting_value_row) == 1:
            return setting_value_row[0]            
        else:
            logging.warning(f"[{CONTEXT}] setting value of {name} could not be found in db")
    
    def set_value(self, name, value):
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
            self.cursor.execute(f"select id from {DB_SETTINGS} where name = '{name}';")
            setting_id = self.cursor.fetchone()
        except:
            logging.warning(f"[{CONTEXT}] db query failed")
            setting_id = None
        
        if not setting_id or not len(setting_id) == 1:
            logging.warning(f"[{CONTEXT}] setting {name} could not be found in db")
            return
        
        try:
            self.cursor.execute(f"update {DB_SETTING_VALUES} set value = \"{str(value)}\" where id = {setting_id[0]}")
            self.conn.commit()
            return True
        except:
            logging.warning(f"[{CONTEXT}] cannot insert measurement in db")

    def close_connection(self):
        self.conn.close()
