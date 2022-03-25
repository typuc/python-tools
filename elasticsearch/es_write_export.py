#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Flask, Response
from prometheus_client import Gauge, CollectorRegistry, generate_latest
from elasticsearch import Elasticsearch, ConnectionError
import datetime
import time

def es_check_write(es_cluster, es_restful, json_data):
    err_msg = ''
    try:
        es = Elasticsearch(es_restful, timeout=1)
        if es_cluster == 'crm' or es_cluster == 'grt_old':
            es.index(index="ops_es_check", doc_type='es', body=json_data)
        else:
            es.index(index="ops_es_check", body=json_data)
    finally:
        return 0

def es_check_searchable(es_cluster, es_restful, query_text):
    err_msg = ''
    try:
        query_dsl = {"size": 0,
                     "query": {
                         "term": {
                             "check_value.keyword": {
                                 "value": query_text
                             }
                         }
                     }
                     }
        es = Elasticsearch(es_restful, timeout=1)
        es_res = es.search(index="ops_es_check", body=query_dsl)
        if es_cluster == 'crm' or es_cluster == 'grt_old':
            if es_res['hits']['total'] == 0:
                res = 0
            else:
                res = 1
        else:
            if es_res['hits']['total']['value'] == 0:
                res = 0
            else:
                res = 1
    except ConnectionError as e:
        # err_msg = ("连接es集群:{} 地址：{} 超时".format(es_cluster, es_restful))
        res = 0
    except:
        # err_msg = ('Unexpected error:', sys.exc_info())
        res = 0
    finally:
        return res


app = Flask(__name__)


@app.route('/metrics')
def start_check():
    registry = CollectorRegistry()
    gauge = Gauge('es_write_searchable', "check es write and search", ['es_cluster'], registry=registry)
    check_time = datetime.datetime.now().replace(microsecond=0).isoformat()
    check_value = datetime.datetime.strptime(check_time, "%Y-%m-%dT%H:%M:%S").strftime('%Y%m%d%H%M')
    for c in es_list:
        cluster_name = c
        restful = es_list[c]
        field_value = c + str(check_value)
        data = {"@timestamp": check_time, "check_value": field_value}
        es_check_write(cluster_name, restful, data)
    time.sleep(1)
    for c in es_list:
        cluster_name = c
        restful = es_list[c]
        field_value = c + str(check_value)
        #print(field_value)
        es_res = es_check_searchable(cluster_name, restful, field_value)
        gauge.labels(cluster_name).set(es_res)
    return Response(generate_latest(gauge), mimetype='text/plain')

if __name__ == '__main__':
    es_list = {"elk": "http://1.1.1.1:9200"}
    app.run(host='0.0.0.0', port=5000)