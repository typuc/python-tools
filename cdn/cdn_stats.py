import os
import json
import wget
import time
import requests
from urllib.parse import quote

def get_baishanyun_domain_list():
    """
    获取白山云域名列表
    """
    protocol_type = 'http'
    baishanyun_domain_list = []
    domain_list_url = ("https://cdn.api.baishan.com/v2/domain/list?token={}\
    &page_number=1&page_size=100\
    &domain_status=serving&protocol_type={}").format(baishan_token,protocol_type)
    resp = requests.get(url=domain_list_url)
    domain_list = json.loads(resp.text)
    for d in domain_list["data"]["list"]:
        baishanyun_domain_list.append(d['domain'])
    return baishanyun_domain_list
def get_baishanyun_bandwith(domain):
    """
    获取指定域名带宽
    """
    protocol_type = 'http'
    url = ("https://cdn.api.baishan.com/v2/stat/bandwidth/eachDomain?token={}&domains={}&start_time=2021-02-07%2012:10&end_time=2021-02-07%2013:10&domain_status=serving&data_type=traffic").format(baishan_token, domain)
    resp = requests.get(url=url)
    res = json.loads(resp.text)
    #print(bandwith["data"][domain]["data"])
    for d in res["data"][domain]["data"]:
        print(("时间 {} bytes {} ").format(d[0],d[1]))
def get_baishanyun_httpcode(domain):
    """
    获取指定域名带宽
    """
    protocol_type = 'http'
    url = ("https://cdn.api.baishan.com/v2/stat/httpcode/eachDomain?token={}&domains={}&start_time=2021-02-07%2012:10&end_time=2021-02-07%2013:10&domain_status=serving&data_type=traffic").format(baishan_token, domain)
    resp = requests.get(url=url)
    print(url)
    res = json.loads(resp.text)
    #print(bandwith["data"][domain]["data"])
    print(res["data"][domain]["data"])

def get_baishanyun_origin_ratio(domain):
    """
    获取指定域名带宽
    """
    protocol_type = 'http'
    url = ("https://cdn.api.baishan.com/v2/stat/originErrRatio?token={}&domains={}&start_time=2021-02-07%2012:10&end_time=2021-02-07%2013:10&domain_status=serving").format(baishan_token, domain)
    resp = requests.get(url=url)
    print(url)
    res = json.loads(resp.text)
    #print(bandwith["data"][domain]["data"])
    for d in res["data"]:
        print(d[0], d[1]["5xx"], d[1]["4xx"])
def get_baishanyun_origin_bandwith(domain):
    """
    获取指定域名带宽
    """
    protocol_type = 'http'
    url = ("https://cdn.api.baishan.com/v2/stat/originBandwidth/eachDomain?token={}\
        &domains={}&start_time=2021-02-07%2012:10\
        &end_time=2021-02-07%2013:10&domain_status=serving").strip()
    print(url)
    resp = requests.get(url=url)

    res = json.loads(resp.text)
    for d in res["data"][domain]["data"]:
        print(d[0], d[1])
def get_baishanyun_origin_request(domain):
    """
    获取指定域名带宽
    """
    protocol_type = 'http'
    url = ("https://cdn.api.baishan.com/v2/stat/originRequest/eachDomain?token={}&domains={}&start_time=2021-02-07%2012:10&end_time=2021-02-07%2013:10&domain_status=serving").format(baishan_token, domain)
    resp = requests.get(url=url)
    print(url)
    res = json.loads(resp.text)
    for d in res["data"][domain]["data"]:
        print(d[0], d[1])


if __name__ == '__main__':
    baishan_token = '11111111'
    #print(get_baishanyun_domain_list())
    domain = 'bs-cdn-video.highso.com.cn'
    #get_baishanyun_bandwith(domain)
    #get_baishanyun_httpcode(domain)
    #get_baishanyun_origin_ratio(domain)
    get_baishanyun_origin_bandwith(domain)
    #get_baishanyun_origin_request(domain)
