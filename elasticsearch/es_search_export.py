import datetime
import time
import elasticsearch7
import json
import sys
import os
import requests
from elasticsearch7 import Elasticsearch


def get_doc_filed(query_text, json_body, page_num):
    for d in json_body:
        if 'forwarded_for' not in d['_source']:
            d['_source']['forwarded_for'] = 'null'

        fd = datetime.datetime.strptime(d['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.000Z")
        # 加8后的时间
        eta = (fd + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        res = "{}|{}|{}|{}|{}|{}|{}".format(query_text, eta, d['_source']['http_host'],
                                            d['_source']['request_uri'], d['_source']['referer'],
                                            d['_source']['remote_addr'], d['_source']['forwarded_for'])

        with open('es_doc_all2.txt', 'a+') as f:
            f.write(res + '\n')


def es_query_export(index_name, query_text, fetch_size):
    es = Elasticsearch(url, timeout=120)
    data = {
        "size": fetch_size,
        "_source": ["@timestamp", "http_host", "request_uri", "referer", "forwarded_for", "remote_addr"],

        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "@timestamp": {
                            "gte": "2021-07-12T14:00:00.000Z",
                            "lte": "2021-07-14T15:59:59.000Z"
                        }
                    }
                },
                "should": [
                    {
                        "match_phrase": {
                            "referer": query_text
                        }
                    },
                    {
                        "match_phrase": {
                            "request_uri": query_text
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {
                "@timestamp": {
                    "order": "asc"
                }
            }
        ]
    }

    res = es.search(index=index_name, body=data, scroll='5m')
    first_page = res['hits']['hits']
    scroll_size = res['hits']['hits']
    sid = res['_scroll_id']
    i = index_name
    page_num = 1
    get_doc_filed(str.strip(i), first_page, page_num)
    # print(scroll_size, sid)
    # scroll_size = []
    while len(scroll_size) > 0:
        page_num = page_num + 1
        page = es.scroll(scroll_id=sid, scroll='5m')
        sid = page['_scroll_id']
        data = page['hits']['hits']
        get_doc_filed(str.strip(i), data, page_num)
        scroll_size = page['hits']['hits']
    return 1


#
if __name__ == '__main__':
    workPath = os.getcwd()
    os.chdir(workPath)
    url = "http://192.168.16.213:9205/"
    url = "http://log-t.b.highso.com.cn"
    resp = requests.get(url + '/_ccr/stats')

    s = resp.content.decode()
    resul = json.loads(s)
    print(resul)
    # n = 0
    # for i in range(0, len(resul['follow_stats']['indices'])):
    #     index_name = resul['follow_stats']['indices'][i]['index']
    #     index_shards = resul['follow_stats']['indices'][i]['shards']
    #     for s in range(0, len(index_shards)):
    #         if len(index_shards[s]['read_exceptions']) > 0:
    #             # print('{} {}'.format(index_name,index_shards[s]['shard_id']))
    #             n = n + 1
    #             print(index_name)
    #             break
    #
    # print(n)




        # print(err_index)


