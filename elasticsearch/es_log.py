import datetime
import time
import elasticsearch7
import json
import sys
import os
from elasticsearch7 import Elasticsearch
import matplotlib.pyplot as plt
import numpy as np


# 使用的索引，因日期时区问题，所以要指定昨天和前天的索引名
# index_name = "deploy_metrics_pro-{date},deploy_metrics_pro-{b_date}".format(date=yesterday,b_date=before_yesterday)

# 实例化Elasticsearch类，并设置超时间为120秒，默认是10秒的，如果数据量很大，时间设置更长一些
def ESsearch(indexName, indexDate, business, endTime, startTime):
    startTime = str(indexDate) + "T" + str(startTime) + ":00:00.000+0800"
    endTime = str(indexDate) + "T" + str(endTime) + ":59:59.999+0800"
    es = Elasticsearch(url, timeout=120)
    data = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "lte": endTime,
                                "gte": startTime
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "status_ok": {
                "filter": {
                    "terms": {"status": ["200", "301", "301", "302"]}
                }
            },
            "status_error": {
                "filter": {"terms": {"status": ["499", " 500", "502", "504", "555"]}
                           }
            }
        }
    }
    print(indexName, endTime, startTime)
    res = es.search(index=indexName, body=data)
    okCount = res["aggregations"]["status_ok"]["doc_count"]
    errorCount = res["aggregations"]["status_error"]["doc_count"]
    allCount = okCount + errorCount
    if allCount == 0:
        pageAvaliable = "100.000"
    else:
        pageAvaliable = ('%.3f' % ((okCount / allCount) * 100))

    action = {
        "@timestamp": startTime,
        "line_of_business": business,
        "availability_ratio": float(pageAvaliable),
        "error_page": errorCount,
        "ok_page": okCount,
        "all_page": allCount

    }
    with open('1.txt', 'a+') as f:
        f.write(str(action) + "\n")
    es.index(index="nginx_access_availability_ratio", body=action)
    #return (pageAvaliable, errorCount, okCount)


def ESsearch_tp(indexName, start_hour, end_hour, search_date):
    es = Elasticsearch(url, timeout=120)
    startTime = str(search_date) + "T" + str(start_hour) + ":00:00.000+0800"
    endTime = str(search_date) + "T" + str(end_hour) + ":59:59.999+0800"
    # print(startTime, endTime)
    data = {
        "size": 0,
        "track_total_hits": "true",
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "lte": endTime,
                                "gt": startTime
                            }
                        }
                    },
                    {
                        "range": {
                            "upstream_response_time": {
                                "gte": "0.005"
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "tp": {
                "percentiles": {
                    "field": "upstream_response_time",
                    "percents": [99]
                }
            }
        }
    }

    res = es.search(index=indexName, body=data)
    tp_out = '%.3f' % (res["aggregations"]["tp"]["values"]["99.0"])
    # print('{}T{}:00 {}'.format(search_date, end_hour, tp_out))
    return tp_out


def out_pic():
    data = {
        "size": 100,
        "_source": ["@timestamp", "line_of_business", "availability_ratio"],
        "sort": [
            {"@timestamp": {"order": "asc"}}],
        "query": {
            "match_all": {}
        }
    }
    es = Elasticsearch(url, timeout=120)
    res = es.search(index="nginx_access_availability_ratio", body=data)
    lt = res["hits"]["hits"]
    x = []
    y = []
    for l in lt:
        utc = datetime.datetime.strptime(l['_source']['@timestamp'], "%Y-%m-%dT%H:%M:%S.000+0800").strftime(
            '%Y-%m-%d %H')
        x.append(utc)
        y.append(l['_source']['availability_ratio'])
    plt.plot(x, y)
    plt.xlabel("date")
    plt.ylabel("TP99(s)")
    plt.xticks(rotation=50)
    plt.show()


#
if __name__ == '__main__':
    workPath = os.getcwd()
    os.chdir(workPath)
    # url = "http://192.168.16.213:9205/"
    url = "http://117.50.20.66:29200/"
    # inputDate = sys.argv[1]
    #indexBusiness = sys.argv[2]
    inputDate = "2020-10-15"
    indexDateLastDay = (datetime.datetime.strptime(inputDate, '%Y-%m-%d') + datetime.timedelta(days=-1)).strftime(
        '%Y%m%d')
    indexBusiness = "www"
    indexDate = datetime.datetime.strptime(inputDate, '%Y-%m-%d').strftime('%Y%m%d')
    # out_pic()
    for i in range(0, 24):
        searchHour = str(i).rjust(2, '0')
        indexName = 'nginx_access_{}_{}'.format(indexBusiness, indexDate)
        if i < 8:
            indexName = 'nginx_access_{}_{}'.format(indexBusiness, indexDateLastDay)
        es = ESsearch(indexName=indexName, business=indexBusiness, indexDate=inputDate, startTime=searchHour,
                      endTime=searchHour)
        # print('{} {} : {} app avaliable {}'.format(indexBusiness, indexDate, searchHour, es))
    # x = []
    # y = []
    # for i in range(0, 24, 2):
    #     start_hour = str(i).rjust(2, '0')
    #     end_hour = str(i + 1).rjust(2, '0')
    #     indexName = 'nginx_access_ops_{}'.format(indexDate)
    #     search_date = inputDate
    #     if i < 8:
    #          indexName = 'nginx_access_ops_{}'.format(indexDateLastDay)
    #          #search_date = "2020-10-14"
    #
    #          #print(indexName, start_hour, end_hour, inputDate)
    #     t = (ESsearch_tp(indexName,start_hour,end_hour,search_date))
    #     x.append(search_date + " " + end_hour)
    #     y.append(t)
    # plt.plot(x, y)
    # plt.xlabel("date")
    # plt.ylabel("TP99(s)")
    # plt.xticks(rotation=50)
    # plt.show()
