import requests
import json
import os
import configparser
config = configparser.ConfigParser()
config = configparser.ConfigParser()
config.read("../config/salt-master.cfg", encoding='utf-8')

session = requests.Session()
print(config.sections())
resp = session.post('{}:1559/login'.format(config['test']['host']), json={
    'username': config['test']['username'],
    'password': config['test']['password'],
    'eauth': 'pam',
})
data = resp.json()['return'][0]
print(data)
target = '192.168.16.224'
resp = session.post('http://192.168.16.213:1559', json=[{
    'client': 'local',
    'tgt': target,
    'fun': 'cmd.run',
    'arg': 'ls',
    'full_return': "true"
}])
print(resp.status_code)
#print(resp.json()['return'][0][target]['retcode'])