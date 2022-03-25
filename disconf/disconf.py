#/bin/env python
#-*- coding: UTF-8 -*-
#pip install MySQL-python
#written by xieronfei 20190226
import MySQLdb
import sys
import time
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
addEnv = sys.argv[1]
appName = sys.argv[2]
envDomain = {'w0': 'test0', 'w1': 'reg'}
d_create_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
d_update_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
# Open database connection
if addEnv == 'w2':
    db = MySQLdb.connect(host='xxxxx', port=3306, user='disconf', passwd='xxxx', db='disconf_stage')
elif addEnv == 'production':
    db = MySQLdb.connect(host='xxxxx', port=3306, user='disconf', passwd='xxxx', db='disconf', connect_timeout=2, read_timeout=5)
else:
    db = MySQLdb.connect(host='xxxx', port=3306, user='disconf', passwd='xxxx', db='disconf')

cursor = db.cursor()
#查询对应环境id
sql="select env_id from env where name='%s'" % (addEnv)
cursor.execute(sql)
results = cursor.fetchone()
d_env_id = results[0]
#查看服务是否存在
sql="select app_id from app where name='%s'" % (appName)
cursor.execute(sql)
results = cursor.fetchone()
if results is None:
    print("插入新服务： " + appName)
    sql="INSERT INTO app(app_id, name, description, create_time, update_time, emails) \
    VALUES (null,'%s', '%s', '%s', '%s','ops@haixue.com')" \
    % (str(appName), str(appName),str(d_create_time),str(d_update_time))
    cursor.execute(sql)
    results = cursor.fetchone()
    sql="select app_id from app where name='%s'" % (appName)
    cursor.execute(sql)
    results = cursor.fetchone()
    d_app_id = results[0]
else:
    d_app_id = results[0]

#查询应用对应的环境是否有配置记录
sql="select * from config where version='1.0.0' and app_id='%s' and env_id='%s'" % (d_app_id,d_env_id)
cursor.execute(sql)
results = cursor.fetchone()
d_value = ''
if results:
    print("服务名: "+ appName + ", 服务id: " + str(d_app_id) + " env: " + addEnv + "is exit!")
else:
    sql="INSERT INTO config(config_id, type, status, name, value, app_id, version, env_id, create_time, update_time) \
    VALUES (null,'0', '1', 'application.properties', '%s', '%d', '%s', '%d', '%s', '%s')" \
    % ( str(d_value), d_app_id,str('1.0.0'), int(d_env_id), str(d_create_time),str(d_update_time))
    #try:
    cursor.execute(sql)
    db.commit()
    print("服务名: "+ appName + ", 服务id: " + str(d_app_id) + " is insert to " + addEnv + " !")
    #except:
    #db.rollback()
cursor.close()
db.close()