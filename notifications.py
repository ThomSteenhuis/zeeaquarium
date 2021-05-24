import datetime as dt
import json
import logging
import requests
import time

import sensor_repo as sr
import setting_repo as setr
import utils

CONTEXT = "notifications"
NOTIFICATION_FILENAME = '/home/pi/Desktop/zeeaquarium/notifications/notification_rules.txt'

def parse_rules(rules):
    parsed_rules = {}
    
    for rule in rules.get('rules'):
        if not parsed_rules.get(rule.get('check_interval')):
            parsed_rules[rule.get('check_interval')] = { 'rules': [{ 'checks': rule.get('checks'), 'message_title': rule.get('message_title'), 'message_body': rule.get('message_body') }] }
        else:
            parsed_rules[rule.get('check_interval')].get('rules').append({ 'checks': rule.get('checks'), 'message_title': rule.get('message_title'), 'message_body': rule.get('message_body') })
    
    return parsed_rules

def check_rules(rules):
    for rule in rules:
        is_rule = True
        for check in rule.get('checks'):
            if not do_check(check):
                is_rule = False
                break
            
        if is_rule:
            send_notification(rule.get('message_title'), rule.get('message_body'))

def do_check(check):
    try:
        lhs = get_variable(check.get('lhs'))
        rhs = get_variable(check.get('rhs'))
        operator = check.get('operator')
        
        if operator == '=':
            return lhs == rhs
        if lhs is None or rhs is None:
            return False
        if operator == '<':
            return lhs < rhs
        if operator == '<=':
            return lhs <= rhs
        if operator == '>':
            return lhs > rhs
        if operator == '>=':
            return lhs >= rhs
        
    except ValueError:
        logging.warning(f"[{CONTEXT}] variable cannot be parsed to floating point number")
        
    return False

def get_variable(variable):
    if variable.get('type') == 'constant':
        return float(variable.get('value'))
    
    if variable.get('type') == 'unknown':
        return None
    
    if variable.get('type') == 'current_time':
        now = dt.datetime.now()
        
        return float(str(now.hour) + str(now.minute))
    
    if variable.get('type') == 'sensor':
        value = utils.retry_if_none(lambda: sensor_repo.get_value(variable.get('value')))
        
        if value is None:
            return None
        
        addition = variable.get('addition')
        
        if addition is None:
            return float(value)
        else:
            return float(value) + float(addition)
        
    if variable.get('type') == 'setting':
        value = utils.retry_if_none(lambda: setting_repo.get_value(variable.get('value')))        
        addition = variable.get('addition')        
        
        if addition is None:
            return float(value)
        else:
            return float(value) + float(addition)

def send_notification(title, body):
    r = requests.post(url, data = {'title': title, 'body': body}, headers = {'Authorization': 'Bearer ' + token} )
    logging.info(f"[{CONTEXT}] notification sent (title: {title}, body: {body})")
    
    if r.status_code != 200:
        logging.warning(f"[{CONTEXT}] cannot post notification via http")

time.sleep(30)

utils.setup_logging(CONTEXT)
sensor_repo = sr.sensor_repo()
setting_repo = setr.setting_repo()

token = None
while token is None:
    try:
        token = utils.login()
    except ConnectionError:
        logging.warning(f"[{CONTEXT}] connection error while logging in")
    time.sleep(1)

url = utils.read_secret("notifications_url")

with open(NOTIFICATION_FILENAME) as notification_rules_file:
    try:
        rules = parse_rules(json.load(notification_rules_file))
        
        last_checked = []
        for check_interval in rules.keys():
            try:
                last_checked.append({'check_interval': int(check_interval), 'last_checked': 0})
            except ValueError:
                logging.warning(f"[{CONTEXT}] invalid check interval")
        
        while True:
            now = time.time()
            for check_interval in last_checked:
                if now - check_interval.get('last_checked') > check_interval.get('check_interval'):
                    check_rules(rules[str(check_interval.get('check_interval'))].get('rules'))
                    check_interval['last_checked'] = now
            
            time.sleep(5)
        
    except json.decoder.JSONDecodeError:
        logging.exception(f"[{CONTEXT}] notification rules could not be opened")
    except KeyboardInterrupt:
        pass
    except:
        logging.exception(f"[{CONTEXT}] general error")
    finally:
        sensor_repo.close_connection()    
        setting_repo.close_connection()
