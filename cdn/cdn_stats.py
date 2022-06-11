# -*- coding: UTF-8 -*-
import datetime
import json
import time
import logging
import os
from elasticsearch7 import Elasticsearch
import sys
import configparser


def cdn_stats_res(es, cdn, http_host, start_time, end_time):
    es = Elasticsearch(es, timeout=120)
    # 按照时间，服务商，加速域名统计 URI 访问量，发送流量

    data = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "http_host": http_host
                        }
                    },
                    {
                        "term": {
                            "cdn_name": cdn
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time,
                                "lt": end_time
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "res_group": {
                "terms": {
                    "field": "res_group",
                    "order": {
                        "sum_bytes": "desc"
                    },
                    "size": 100
                },
                "aggs": {
                    "sum_bytes": {
                        "sum": {
                            "field": "body_bytes_sent"
                        }
                    },
                    "res_type": {
                        "terms": {
                            "field": "res_type",
                            "order": {
                                "sum_bytes": "desc"
                            },
                            "size": 100
                        },
                        "aggs": {
                            "sum_bytes": {
                                "sum": {
                                    "field": "body_bytes_sent"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    res = es.search(index="cdn_log", body=data)
    sum_page = sum_all = 0
    result = res["aggregations"]["res_group"]["buckets"]
    for i in range(len(result)):
        res_group = result[i]['key']
        res_type_buckets = result[i]['res_type']['buckets']
        for t in range(len(res_type_buckets)):
            data_json = dict()
            data_json['@timestamp'] = start_time
            data_json['cdn_name'] = cdn
            data_json['http_host'] = http_host
            data_json['res_group'] = res_group
            data_json['res_type'] = res_type_buckets[t]['key']
            data_json['page_count'] = res_type_buckets[t]['doc_count']
            data_json['sum_bytes'] = res_type_buckets[t]['sum_bytes']['value']
            es.index(index='app_resource_cdn_res', body=data_json)
            with open(result_file, 'a+') as r:
                r.writelines(json.dumps(data_json, ensure_ascii=False) + "\n")

def cdn_stats_uri(es, cdn, http_host, start_time, end_time):
    es = Elasticsearch(es, timeout=120)
    # 按照时间，服务商，加速域名统计 URI 访问量，发送流量
    data = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "cdn_name": cdn
                        }
                    },
                    {
                        "term": {
                            "http_host": http_host
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time,
                                "lt": end_time
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "uri": {
                "terms": {
                    "field": "uri",
                    "order": {
                        "sum_bytes": "desc"
                    },
                    "size": 100
                },
                "aggs": {
                    "sum_bytes": {
                        "sum": {
                            "field": "body_bytes_sent"
                        }
                    }
                }
            }
        }
    }
    res = es.search(index="cdn_log", body=data)
    sum_page = sum_all = 0
    result = res["aggregations"]["uri"]["buckets"]
    for i in range(len(result)):
        data_json = dict()
        data_json['@timestamp'] = start_time
        data_json['cdn_name'] = cdn
        data_json['http_host'] = http_host
        data_json['uri'] = result[i]['key']
        data_json['page_count'] = result[i]['doc_count']
        data_json['sum_bytes'] = result[i]['sum_bytes']['value']
        es.index(index='app_resource_cdn_uri', body=data_json)
        with open(result_file, 'a+') as r:
            r.writelines(json.dumps(data_json, ensure_ascii=False) + "\n")

def cdn_stats_status(es, cdn, http_host, start_time, end_time):
    es = Elasticsearch(es, timeout=120)
    # 按照时间，服务商，加速域名统计 URI 访问量，发送流量
    data = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "cdn_name": cdn
                        }
                    },
                    {
                        "term": {
                            "http_host": http_host
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time,
                                "lt": end_time
                            }
                        }
                    },
                    {
                        "range": {
                            "status": {
                                "gte": 404,
                                "lte": 405
                            }
                        }
                    }
                ],
                "must_not": [
                    {
                        "term": {
                            "uri": "/favicon.ico"

                        }
                    }
                ]
            }
        },
        "aggs": {
            "status": {
                "terms": {
                    "field": "status",
                    "order": {
                        "_count": "desc"
                    },
                    "size": 5
                },
                "aggs": {
                    "uri": {
                        "terms": {
                            "field": "uri",
                            "min_doc_count": 3,
                            "order": {
                                "_count": "desc"
                            },
                            "size": 100
                        }
                    }
                }
            }
        }
    }
    #
    res = es.search(index="cdn_log", body=data)
    if len(res["aggregations"]["status"]["buckets"]) > 0:
        result = res["aggregations"]["status"]["buckets"][0]['uri']["buckets"]

        for i in range(len(result)):
            data_json = dict()
            data_json['@timestamp'] = start_time
            data_json['cdn_name'] = cdn
            data_json['http_host'] = http_host
            data_json['uri'] = result[i]['key']
            data_json['status'] = 404
            data_json['page_count'] = result[i]['doc_count']
            es.index(index='app_resource_cdn_status', body=data_json)
            with open(result_file, 'a+') as r:
                r.writelines(json.dumps(data_json, ensure_ascii=False) + "\n")

if __name__ == '__main__':
    work_path = os.getcwd()
    os.chdir(work_path)
    config = configparser
    config = configparser.ConfigParser()
    os.chdir(work_path)
    config.read('config/cdn.cfg', encoding='UTF-8')
    # env dev, prod
    env = "dev"
    app_log_path = config[env]['app_log_path']
    result_path = config[env]['result_path']
    url = config[env]['url']
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='{}/cdn_info_{}.log'.format(app_log_path,
                                                             datetime.datetime.strftime(datetime.datetime.now(),
                                                                                        '%Y-%m-%d')),
                        filemode='w')

    cdn_domain_name = {'阿里云': 'config/aliyun.txt', '腾讯云': 'config/tencent.txt', '七牛云': 'config/qiniu.txt'}
    try:
        for k, v in cdn_domain_name.items():
            cdn_name = k
            with open(v, 'r') as f:
                for n in f.readlines():
                    domain_name = n.strip()
                    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    yesterday_datetime_00 = '{}T00:00:00:000Z'.format(yesterday)
                    result_file = "{}/cdn_stats_{}.log".format(result_path, datetime.datetime.now().strftime('%Y-%m'))

                    # 转化UTC时间减去8小时
                    es_query_start_datetime = (
                            datetime.datetime.strptime(yesterday_datetime_00, '%Y-%m-%dT%H:%M:%S:000Z')
                            - datetime.timedelta(hours=8))
                    es_query_start_str = es_query_start_datetime.strftime('%Y-%m-%dT%H:%M:%S:000Z')
                    # 统计间隔
                    hour_interval = 24
                    for i in range(int(24 / hour_interval)):
                        es_query_end_datetime = es_query_start_datetime + datetime.timedelta(hours=hour_interval)
                        # 转化为查询时间UTC字符串
                        es_query_start_str = datetime.datetime.strftime(es_query_start_datetime,
                                                                        "%Y-%m-%dT%H:%M:%S.000Z")
                        es_query_end_str = datetime.datetime.strftime(es_query_end_datetime, "%Y-%m-%dT%H:%M:%S.000Z")
                        # 调用查询

                        cdn_stats_res(url, cdn_name, domain_name, es_query_start_str, es_query_end_str)
                        cdn_stats_uri(url, cdn_name, domain_name, es_query_start_str, es_query_end_str)
                        cdn_stats_status(url, cdn_name, domain_name, es_query_start_str, es_query_end_str)
                        # 当前结束时间作为下一次开始时间
                        es_query_start_datetime = es_query_end_datetime

                    # time.sleep(1)

    except ConnectionError as e:
        err_msg = ("连接es集群地址：{} 超时".format(url))
    except:
        err_msg = ('Unexpected error:', sys.exc_info())
        logging(err_msg)
