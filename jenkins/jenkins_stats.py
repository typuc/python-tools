#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
import sys
import io
import os
import jenkins
from datetime import datetime
import re
from elasticsearch7 import Elasticsearch, ConnectionError
import logging, logging.config
import configparser
from logging.handlers import RotatingFileHandler


def job_list():
    #获取job和url对应关系
    project_url = dict()
    all_jobs = server.get_jobs()
    project_list = list()
    for p in range(0, len(all_jobs)):
        project_url[all_jobs[p]['fullname']] = all_jobs[p]['url']

    return project_url


def job_status(project):
    job = dict()
    try:
        #获取最后一次构建状态
        job_info = server.get_job_info(project)['lastCompletedBuild']
        #获取构建任务信息
        if job_info is not None:
            last_num = server.get_job_info(project)['lastCompletedBuild']['number']
            build_datetime = datetime.fromtimestamp(int(server.get_build_info(project, last_num)['timestamp'] / 1000))
            job['@timestamp'] = build_datetime.strftime('%Y-%m-%dT%H:%M:%S+08:00')
            job['project'] = project
            job['duration'] = int(server.get_build_info(project, last_num)['duration'] / 1000)
            job['result'] = server.get_build_info(project, last_num)['result']
            #判断状态，避免状态和结果不一致（jenkins bug,部分服务实际打包成功，但是状态red)
            if job['result'] != 'SUCCESS':
                #读取console数据
                console_result = server.get_build_console_output(project,last_num)
                buf = io.StringIO(console_result)
                pattern = r'SUCCESS'
                res = buf.readlines()[-1:][0]
                #匹配是否有SUCCESS，如果有则修改状态为实际状体
                if re.search(pattern, res):
                    job['result'] = 'SUCCESS'

            job['number'] = server.get_job_info(project)['lastCompletedBuild']['number']
            logging.error("获取 {} 构建结果{} status {}".format(project,job['result'],job['number']))
    except Exception as e:
        print(e)
    return job


def write_es(es_restful, json_data):
    err_msg = ''
    try:
        es = Elasticsearch(es_restful, timeout=3)
        query_dsl = {"query": {
            "bool": {
                "must": [
                    {"term": {"number": {"value": json_data["number"]}}},
                    {"term": {"project.keyword": {"value": json_data["project"]}}}
                ]
            }
        }
        }

        es_res = es.search(index="jenkins_build_result", body=query_dsl)

        if es_res['hits']['total']['value'] == 0:
            es.index(index="jenkins_build_result", body=json_data)

    except ConnectionError as e:
        err_msg = ("连接es集群地址：{} 超时".format(es_restful))
    except:
        err_msg = ('Unexpected error:', sys.exc_info())
    finally:
        print(err_msg)
        # print(check_value)


if __name__ == '__main__':
    os.makedirs("../logs", exist_ok=True)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='../logs/jenkins.log',
                        filemode='w')
    config = configparser.ConfigParser()
    config.read('../config/jenkins.cfg')
    username = config['test']['username']
    password =  config['test']['password']
    jenkins_url =  config['test']['jenkins_url']
    project = 'merchant-test0-goods-mgt'
    server = jenkins.Jenkins(jenkins_url, username=username, password=password)
    # json_data = job_status('auto-infra-apihome-service')
    # write_es("192.168.16.172:9200", json_data)
    for k, v in job_list().items():
        print("****" + k)
        es_json = job_status(k)
        if es_json:
            write_es("192.168.16.172:9200", es_json)
    # #print(job_list())
    # print(job_status("api-reg-jjxt-app-api"))

