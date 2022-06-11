#!/usr/bin/env python
# coding=utf-8
import datetime
import json
import wget
import requests
import configparser
import logging
import os
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcdn.request.v20180510.DescribeCdnDomainLogsRequest import DescribeCdnDomainLogsRequest
from aliyunsdkcdn.request.v20180510.DescribeUserDomainsRequest import DescribeUserDomainsRequest



def download_aliyun_cdnlog(domain_name):
    domain_name_all_list = list()
    request = DescribeUserDomainsRequest()
    request.set_accept_format('json')
    request.set_DomainStatus("online")
    response = client.do_action_with_exception(request)
    # python2:  print(response)
    data_dic = json.loads(str(response, encoding='utf-8'))['Domains']['PageData']
    for i in range(len(data_dic)):
        domain_name_all_list.append(data_dic[i]['DomainName'])
    return domain_name_all_list
    request = DescribeCdnDomainLogsRequest()
    request.set_accept_format('json')
    start_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.today()).strftime('%Y-%m-%d')
    start_date_start = start_date + 'T00:00:00Z'
    end_date_start = end_date + 'T00:00:00Z'
    print(end_date_start, start_date_start)
    request.set_StartTime(start_date_start)
    request.set_EndTime(end_date_start)
    request.set_PageSize(100)

    for i in range(len(domain_name)):
        print(domain_name[i])
        request.set_DomainName(domain_name[i])
        response = client.do_action_with_exception(request)
        # python2:  print(response)
        data_dic = json.loads(str(response, encoding='utf-8'))
        log_info = data_dic['DomainLogDetails']['DomainLogDetail'][0]['LogInfos']['LogInfoDetail']
        for d in range(len(log_info)):
            download_url = log_info[d]['LogPath']
            print(download_url)
            file_name = wget.filename_from_url(download_url)
            out_file = '{}.log'.format(file_name)
            os.system('wget --limit-rate={} "{}" -O {} > /dev/null 2>&1'.format(wget_limit, download_url, file_name))
            os.system('gunzip -c ' + file_name + ' > ' + out_file)
            os.system('rm -rf ' + file_name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='../logs/download_cdn_{}'.format(
                            datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')),
                        filemode='w')
    date_today = datetime.datetime.today().date()
    date_yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    wget_limit = '4m'
    # aliyunCDN
    '''
    pip install aliyun-python-sdk-cdn==3.7.1 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

    '''
    # https://github.com/TencentCloud/tencentcloud-sdk-python
    config = configparser.ConfigParser()
    config.read('../config/cdn.cfg', encoding='UTF-8')
    SecretId = config['aliyun']['SecretId']
    SecretKey = config['aliyun']['SecretKey']
    credentials = AccessKeyCredential(SecretId, SecretKey)
    work_path = '/Users/leo/Desktop/mydev/logs'
    client = AcsClient(region_id='cn-beijing', credential=credentials)
    os.chdir("{}/aliyun/".format(work_path))
    os.system('rm -rf *.log')
    download_aliyun_cdnlog()
