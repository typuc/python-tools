#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
##调用pinpoint,获取jvm,mem内存使用
import json
import sys
import requests
import time
import datetime


# 获取所有应用列表
def get_applications(http_host):
    applicationListUrl = http_host + '/applications.pinpoint'
    res = requests.get(applicationListUrl)
    if res.status_code != 200:
        print("请求异常,请检查")
        return
    return res.json()
    # print(res.json()[0])


# 根据agentid，查询应用制定时间范围内的gc,mem使用
def get_mem_gc(agentid, start, end):
    url = http_host + '/getAgentStat/jvmGc/chart.pinpoint'
    result = dict()
    param = {
        "agentId": agentid,
        "from": start,
        "to": end,
        "sampleRate": 1}
    res = requests.get(url, param)
    # 获取y轴数据
    data = res.json()['charts']['y']
    # 判断是否为空
    if data['JVM_MEMORY_HEAP_USED']:
        # 数据间隔5秒一次
        jvm_heap_used = data['JVM_MEMORY_HEAP_USED']
        jvm_noheap_used = data['JVM_MEMORY_NON_HEAP_USED']
        jvm_gc_old_count = data['JVM_GC_OLD_COUNT']
        jvm_gc_old_time = data['JVM_GC_OLD_TIME']
        my_list = list()
        # 最大堆内存
        for i in jvm_heap_used:
            my_list.append(i[2] / 1000 / 1000)
        jvm_heap_used = max(set(my_list))
        # 最大非堆内存
        my_list = list()
        for i in jvm_noheap_used:
            my_list.append(i[2] / 1000 / 1000)
        jvm_noheap_used = max(set(my_list))
        # 总old gc time
        my_list = list()
        for i in jvm_gc_old_count:
            my_list.append(i[2])
        my_list = list()
        # 总old gc 次数
        jvm_gc_old_count = sum(set(my_list))
        for i in jvm_gc_old_time:
            my_list.append(i[2])
        jvm_gc_old_time = sum(set(my_list))
        # 输出json
        result["@timestamp"] = insert_time
        result["source"] = 'pinpoint'
        result["app_name"] = app_name
        result["agentid"] = agentid
        result["jvm_heap_used"] = int(jvm_heap_used)
        result["jvm_noheap_used"] = int(jvm_noheap_used)
        result["jvm_gc_old_count"] = jvm_gc_old_time
        result["jvm_gc_old_time"] = jvm_gc_old_time

        return result


# 获取所有应用列表
def getAgentList(appname):
    data = dict()
    agent_list = list()
    AgentListUrl = http_host + '/getAgentList.pinpoint'
    param = {
        "application": appname
    }
    res = requests.get(AgentListUrl, params=param)
    if res.status_code != 200:
        print("请求异常,请检查")
        return
    data = dict(res.json())
    for k, v in data.items():
        agent_list.append(v[0]['agentId'])
    return agent_list


if __name__ == "__main__":

    http_host = 'http://pinpoint.reg.highso.com.cn'
    end_time = int(time.time() * 1000)
    # 查询间隔单位秒
    interval = int(sys.argv[1])
    insert_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000+0800')
    '''获取所有服务的app名和服务类型，并存到字典中'''
    applicationLists = get_applications(http_host)
    for n in applicationLists:
        app_name = n['applicationName']
        # 查询结束时间
        agent_list = list(getAgentList(app_name))
        start_time = end_time - interval * 1000
        for a in agent_list:
            agent_res = get_mem_gc(a, start_time, end_time)
            if agent_res:
                with open('tmp/pinpoint-mem-gc.log', 'a') as f:
                    f.write(json.dumps(agent_res) + '\n')
