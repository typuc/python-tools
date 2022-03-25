#!/usr/bin/python
# -*-coding:UTF-8-*-
import datetime
import sys
import time

from elasticsearch7 import Elasticsearch, ConnectionError
from prometheus_client import start_http_server, Gauge

def es_write_query(es_cluster, es_restful, json_data):
    err_msg = ''
    try:
        es = Elasticsearch(es_restful, timeout=3)
        if es_cluster == 'crm' or es_cluster == 'grt_old':
            es.index(index="ops_es_check", doc_type='es', body=json_data)
        else:
            es.index(index="ops_es_check", body=json_data)

        time.sleep(1)
        query_dsl = {"size": 0,
                     "query": {
                         "term": {
                             "check_value.keyword": {
                                 "value": json_data['check_value']
                             }
                         }
                     }
                     }
        # time.sleep(90)

        es_res = es.search(index="ops_es_check", body=query_dsl)
        print('*' * 60)
        if es_cluster == 'crm' or es_cluster == 'grt_old':
            if es_res['hits']['total'] == 0:
                err_msg = ("es cluster: {} query error".format(es_cluster))

        else:
            if es_res['hits']['total']['value'] == 0 :
                err_msg = ("es cluster: {} query error".format(es_cluster))

    except ConnectionError as e:
        err_msg = ("连接es集群:{} 地址：{} 超时".format(es_cluster, es_restful))
    except:
        err_msg = ('Unexpected error:', sys.exc_info())
    finally:
        print(err_msg)
        #print(check_value)


if __name__ == '__main__':
    es_list = {"crm": "http://192.168.16.211:9202", "common": "http://192.168.16.211:9206"}
    #es_list = {"common": "http://192.168.16.211:9206"}

    es_5 = ('crm', 'grt_old')
    for c in es_list:
        cluster_name = c
        restful = es_list[c]
        check_time = datetime.datetime.now().replace(microsecond=0).isoformat()
        check_value = datetime.datetime.strptime(check_time, "%Y-%m-%dT%H:%M:%S").strftime('%Y%m%d%H%M')
        ##s_time = datetime.datetime.strptime(check_time, "%Y-%m-%dT%H:%M:%S").timestamp()
        check_value = c + str(check_value)
        data = {"@timestamp": check_time, "check_value": check_value}
        es_write_query(cluster_name, restful, data)
