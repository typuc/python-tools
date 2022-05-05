#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
import datetime
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import configparser
from elasticsearch7 import Elasticsearch


def send_msg(contact, msg):
    timestamp = str(round(time.time() * 1000))
    headers = {"Content-Type": "application/json ;charset=utf-8 "}
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    parm = {
        "access_token": access_token,
        "timestamp": timestamp,
        "sign": sign
    }
    message = {
        "msgtype": "text",
        "text": {"content": msg},
        "at": {
            "atMobiles": contact,
            "isAtAll": False
        }
    }
    info = requests.post(url=url, headers=headers, params=parm, json=message)
    print(info.text)


def es_search():
    interval = 1
    end_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+0800')
    start_time = (datetime.datetime.now() - datetime.timedelta(minutes=interval)).strftime('%Y-%m-%dT%H:%M:%S+0800')
    query_text = '其它呼叫外线错误'
    error_word = ['其它呼叫外线错误', '中通连接失败']
    # 林晓东
    mobile = ['18683875959']
    es_host = '192.168.16.213:9205'
    es_index = "fe_log_20220429"
    es = Elasticsearch(es_host)
    for query_text in error_word:
        data = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [
                        {"range": {"@timestamp": {
                            "gte": start_time,
                            "lt": end_time
                        }}},
                        {"match_phrase": {"message": query_text}}
                    ]
                }
            }
        }
        rest = es.search(index=es_index, body=data)
        msg = '{} fe-call-server 日志 匹配关键词: "{}" 触发报警，请处理'.format(end_time, query_text)
        logging.info('开始查询索引:{} 关键词:"{}"'.format(es_index, query_text))
        if rest['hits']['total']['value'] > 0:
            send_msg(mobile, msg)
            logging.info(msg)

    return 0


##https://open.dingtalk.com/document/robots/customize-robot-security-settings

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s  %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='../logs/fe-call-server_es.log_{}'.format(
                            datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')),
                        filemode='w')
    group = 'fe'
    config = configparser.ConfigParser()
    config.read('../config/dingding.cfg')
    access_token = config[group]['access_token']
    secret = config[group]['secret']
    url = "https://oapi.dingtalk.com/robot/send"
    es_search()