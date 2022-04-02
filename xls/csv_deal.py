#!/usr/bin/python
# -*-coding:UTF-8-*-
import json
import sys
import csv
import os
import datetime
mylist = list()
header = ['service_name', 'service_type', 'approve_time', 'team_name','name']
with open(r'/tmp/export_result.csv', 'r', encoding='utf-8') as myFile:
    lines = csv.reader(myFile)
    for r in lines:
        t = datetime.datetime.strptime(r[2],"%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%dT%H:%M:%S+08:00")
        m = datetime.datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m")
        r[2] = t
        r.append(m)
        mylist.append(r)

with open("../tmp/out.csv", 'w', encoding='UTF8', newline='') as w:
    #newline=''避免写入空行
    #创建CSV写入器
    writer = csv.writer(w)
    writer.writerow(header)
    writer.writerows(mylist)

# with open('3.csv', 'w') as myCSV:
#     lall = list()
#     cr = csv.writer(myCSV)
#     with open('1.txt', 'rt', encoding='utf-8') as f:
#         for r in f.readlines():
#
#             l = r.strip('\n').split(',')
#
#             if 'mb' in l[4]:
#                 l[4] = l[4].split('mb')[0]
#             if 'gb' in l[4]:
#                 l[4] = float(l[4].split('gb')[0]) * 1024
#             lall.append(l[2])
#             lall.append(l[3])
#             lall.append(l[3])
#     print(lall)
