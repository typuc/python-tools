from openpyxl import Workbook
import sys
import time
import datetime
import pymysql.cursors
from openpyxl import load_workbook
import json

def gtid_update(canal_name, port_gtid):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `PARAMETERS` FROM `canal` WHERE `NAME`='{}'".format(canal_name)
            #print(sql)
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql)
            result = cursor.fetchone()

            #print(result)
            if result is not None:
                dict_par = json.loads(result['PARAMETERS'])
                #print(canal_name, dict_par['groupDbAddresses'])
                # print(dict_par)
                #判断是否为gtid模式
                if len(dict_par['positions']) != 0:
                    ##获取slave端口
                    slave_port = dict_par['groupDbAddresses'][0][0]['dbAddress']['port']

                    #判断点位信息返回是否是字符串
                    if isinstance(dict_par['positions'][0], str):
                        pos_dict = json.loads(dict_par['positions'][0])
                    else:
                        pos_dict = dict_par['positions'][0]
                    #替换点位信息

                    pos_dict["gtid"] = port_gtid[str(slave_port)]
                    dict_par['positions'][0] = pos_dict
                    sql = "update canal set PARAMETERS='{}' where `NAME`='{}'".format(json.dumps(dict_par), canal_name)
                    print(sql)
                    #print(canal_name, slave_port)
                    #cursor.execute(sql)
                    connection.commit()
            else:
                print("没有找到")


    except Exception as e:
        print(e)

#common_canal = ('test0-3306_highso_merchant_aggregation')

#canal_gtid = '153f2d32-5481-11ea-8f3a-b95ca1147e3b:1-5,cf27e6e9-5311-11ea-85df-be66c3a1de73:1-2120,d2a2a109-1b3b-11e7-89c7-e0036d1c4608:1-535644907,f4432868-5258-11ea-812a-a80b3c0d8b93:1-5344'
if __name__ == '__main__':
    connection = pymysql.connect(host='111111',
                                 user='root', passwd='11111',
                                 db='otter', port=3308, charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    port_gtid = dict()
    #port gtid对应关系
    port_gtid = {"3306": "temp-3306-gtid",
                 "3307": "temp-3307-gtid",
                 "3351": "temp-3351-gtid",
                 }
    with connection.cursor() as cursor:
        sql_canal = "SELECT `NAME` FROM `canal`"
        cursor.execute(sql_canal)
        res = cursor.fetchall()
        if res is not None:
            for i in res:
                #print(i['NAME'], '111')
                gtid_update(i['NAME'], port_gtid)
    connection.close()