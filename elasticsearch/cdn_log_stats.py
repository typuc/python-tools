# -*- coding: UTF-8 -*-
import datetime
import json
import time
import logging
import os
from elasticsearch7 import Elasticsearch
import sys
import configparser


def es_search(es, cdn, http_host, start_time, end_time):
    es = Elasticsearch(es, timeout=120)
    # 按照时间，服务商，加速域名统计 URI 访问量，发送流量
    data = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time,
                                "lt": end_time
                            }
                        }
                    },
                    {
                        "term": {
                            "http_host": http_host
                        }
                    },
                    {
                        "term": {
                            "cdn_name": cdn
                        }
                    }
                ]
            }
        },
        "aggs": {
            "uri": {
                "terms": {
                    "field": "uri",
                    "size": 50000,
                    "min_doc_count": 3
                },
                "aggs": {
                    "sum": {
                        "sum": {
                            "field": "body_bytes_sent"
                        }
                    },
                    "max": {
                        "max": {
                            "field": "body_bytes_sent"
                        }
                    }
                }
            }
        }
    }
    res = es.search(index="cdn_log", body=data)
    result = res["aggregations"]["uri"]["buckets"]
    logging.info("开始统计 {} 加速域名 {} {}".format(cdn, http_host, start_time))
    print(".............{}........".format(len(result)))
    if len(result) > 0:
        for b in range(len(result)):
            uri = result[b]["key"]
            page_count = result[b]["doc_count"]
            sum_bytes = result[b]["sum"]["value"]
            max_bytes = result[b]["max"]["value"]
            # 根据uri查询资源类型
            data = {
                "size": 1,
                "_source": {
                    "includes": ["res_group", "res_type"]
                },
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "@timestamp": {
                                        "gte": start_time,
                                        "lt": end_time
                                    }
                                }
                            },
                            {
                                "term": {
                                    "http_host": http_host
                                }
                            },
                            {
                                "term": {
                                    "cdn_name": cdn_name
                                }
                            },
                            {
                                "term": {
                                    "uri": uri
                                }
                            }
                        ]
                    }
                }
            }
            res2 = es.search(index="cdn_log", body=data)

            res_type = res2["hits"]["hits"][0]["_source"]["res_type"]
            if 'res_group' in res2["hits"]["hits"][0]["_source"]:
                res_group = res2["hits"]["hits"][0]["_source"]["res_group"]
            else:
                res_group = 'other'
            t = {"@timestamp": start_time, "cdn_name": cdn, "http_host": http_host,
                 "uri": uri, "res_group": res_group, "res_type": res_type.lower(), "page_count": page_count,
                 "sum_bytes": sum_bytes, "max_bytes": int(max_bytes)}
            with open(result_file, 'a+') as r:
                r.writelines(json.dumps(t, ensure_ascii=False) + "\n")
    else:
        logging.error("开始统计 {} 加速域名 {} {} 访问请求为:0 ".format(cdn, http_host, start_time))


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

    # cdn_domain_name = {'阿里云': 'config/aliyun.txt', '腾讯云': 'config/tencent.txt', '七牛云': 'config/qiniu.txt'}
    # cdn_domain_name = {'七牛云': 'config/qiniu.txt'}
    cdn_domain_name = {'白山云': 'config/baishanyun.txt'}
    try:
        for k, v in cdn_domain_name.items():
            cdn_name = k
            with open(v, 'r') as f:
                for n in f.readlines():
                    domain_name = n.strip()
                    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    yesterday_datetime_00 = '{}T00:00:00:000Z'.format(yesterday)
                    result_file = "{}/cdn_stats_{}_{}_{}.log".format(result_path, cdn_name, domain_name, yesterday)
                    # 如果文件存储，清理
                    os.system('rm -rf {}'.format(result_file))
                    # 转化UTC时间减去8小时
                    es_query_start_datetime = (
                            datetime.datetime.strptime(yesterday_datetime_00, '%Y-%m-%dT%H:%M:%S:000Z')
                            - datetime.timedelta(hours=8))
                    es_query_start_str = es_query_start_datetime.strftime('%Y-%m-%dT%H:%M:%S:000Z')
                    # 统计间隔

                    hour_interval = 0.1
                    for i in range(int(24 / hour_interval)):
                        es_query_end_datetime = es_query_start_datetime + datetime.timedelta(hours=hour_interval)
                        # 转化为查询时间UTC字符串
                        es_query_start_str = datetime.datetime.strftime(es_query_start_datetime,
                                                                        "%Y-%m-%dT%H:%M:%S.000Z")
                        es_query_end_str = datetime.datetime.strftime(es_query_end_datetime, "%Y-%m-%dT%H:%M:%S.000Z")
                        # 调用查询
                        es_search(url, cdn_name, domain_name, es_query_start_str, es_query_end_str)
                        # 当前结束时间作为下一次开始时间
                        es_query_start_datetime = es_query_end_datetime

                    # time.sleep(1)

    except ConnectionError as e:
        err_msg = ("连接es集群地址：{} 超时".format(url))
    except:
        err_msg = ('Unexpected error:', sys.exc_info())
        logging(err_msg)
