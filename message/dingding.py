#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import configparser


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


##https://open.dingtalk.com/document/robots/customize-robot-security-settings

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('../config/dingding.cfg')
    access_token = config['ops']['access_token']
    secret = config['ops']['secret']
    url = "https://oapi.dingtalk.com/robot/send"
    print(access_token)
    text = "are  you ok"
    mobile = ['13402891988']
    send_msg(mobile, text)


