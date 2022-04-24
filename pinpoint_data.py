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


# 根据agentid，查询应用制定时间范围内的gc,mem使用
def get_mem_gc(agentid, ip, start, end):
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
    jvm_heap_used = 0
    jvm_noheap_used = 0
    direct_mem_used = 0
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
        # 总old gc 次数
        my_list = list()
        gc_count = 0
        for i in jvm_gc_old_count:
            if i[1] > 0:
                gc_count = gc_count + 1
        # 总old gc time
        gc_time = 0
        for i in jvm_gc_old_time:
            if i[1] > 0:
                gc_time = gc_time + i[1]
        # 输出json
        insert_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000+0800')
        result["@timestamp"] = insert_time
        result["source"] = 'pinpoint'
        result["app_name"] = app_name
        result["agentid"] = agentid
        result["jvm_heap_used"] = int(jvm_heap_used)
        result["jvm_noheap_used"] = int(jvm_noheap_used)
        result["jvm_gc_old_count"] = gc_count
        result["jvm_gc_old_time"] = gc_time
        result["node_ip"] = ip
    # 获取buffer内存
    url = http_host + '/getAgentStat/directBuffer/chart.pinpoint'
    param = {
        "agentId": agentid,
        "from": start,
        "to": end,
        "sampleRate": "NaN"}
    res = requests.get(url, param)
    # 获取y轴数据
    data = res.json()['charts']['y']
    my_list = list()
    if data['DIRECT_MEMORY_USED']:
        # 数据间隔5秒一次
        direct_mem_used = data['DIRECT_MEMORY_USED']
        # 最大堆内存
        for i in direct_mem_used:
            my_list.append(i[2] / 1000 / 1000)
        direct_mem_used = max(set(my_list))
    all_mem = int(jvm_heap_used) + int(jvm_noheap_used) + int(direct_mem_used)
    if all_mem < 0:
        # all = "{},{},{}".format(app_name,mem,ip)
        all_mem = 0
    result['sum_mem'] = all_mem
    result["direct_mem_used"] = int(direct_mem_used)
    return result


# 获取agentid 和 IP对应关系（agentid全局唯一）
def getAgentList(appname):
    data = dict()
    agent_list = list()
    agentid_ip = dict()
    AgentListUrl = http_host + '/getAgentList.pinpoint'
    param = {
        "application": appname
    }
    res = requests.get(AgentListUrl, params=param)
    if res.status_code != 200:
        print("请求异常,请检查")
        return
    data = dict(res.json())
    for k1, v1 in data.items():
        '''{"bj-ucloudu-10-10-10102": "10.9.10.10"}'''
        agent_list.append(v1[0]['agentId'])
        agentid_ip[v1[0]['agentId']] = v1[0]['ip']
    # print(agentid_ip)
    return agentid_ip


if __name__ == "__main__":
    http_host = 'http://fizz-p.h.highso.com.cn'

    # 查询间隔单位秒
    # interval = int(sys.argv[1])
    interval = 86400
    end_time = int(time.time() * 1000)
    start_time = end_time - interval * 1000
    app_name = "api-gateway"
    agent_res = get_mem_gc('bj-ucloud-117-252-c-15410', '10.9.117.252', start_time, end_time)
    print(agent_res)
    '''获取app名和服务类型，并存到字典中'''
    # try:
    #     applicationLists = get_applications(http_host)
    #     for n in applicationLists:
    #         # time.sleep(1)
    #         app_name = n['applicationName']
    #         # 查询结束时间
    #         agent_list = list(getAgentList(app_name))
    #         insert_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000+0800')
    #         '''通过服务名获取服实例内存和部署节点IP'''
    #         for k, v in getAgentList(app_name).items():
    #             agent_res = get_mem_gc(k, v, start_time, end_time)
    #             if agent_res:
    #                 if agent_res:
    #                     print(agent_res)
    #                     # with open('tmp/pinpoint-mem-gc.log', 'a') as f:
    #                     #     f.write(json.dumps(agent_res) + '\n')
    # except e:
    #     print(e)

    # with open('s.txt','r') as t:
    #
    #     for r in t.readlines():
    #         time.sleep(1)
    #         app_name = r.strip()
    #         print(app_name)
    #     # 查询结束时间
    #         agent_list = list(getAgentList(app_name))
    #         start_time = end_time - interval * 1000
    #         for a in agent_list:
    #             for k, v in getAgentList(app_name).items():
    #                 agent_res = get_mem_gc(k, v, start_time, end_time)
    #                 if agent_res:
    #                     # if agent_res:
    #                     #     with open('tmp/pinpoint-mem-gc.log', 'a') as f:
    #                     #         f.write(json.dumps(agent_res) + '\n')
    #                     #print(agent_res)
