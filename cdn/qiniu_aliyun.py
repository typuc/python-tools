    #!/usr/bin/env python
    # coding=utf-8
import datetime
import json
import wget
import requests
import configparser
import logging
import os
import qiniu
from qiniu import CdnManager
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcdn.request.v20180510.DescribeCdnDomainLogsRequest import DescribeCdnDomainLogsRequest
from aliyunsdkcdn.request.v20180510.DescribeUserDomainsRequest import DescribeUserDomainsRequest


def download_file(cdn_name, domain_name, download_url):
    file_name = wget.filename_from_url(download_url)
    out_file = '{}.log'.format(file_name)
    logging.info("开始下载: {} 域名：{} 日志 {}".format(cdn_name, domain_name, file_name))
    os.system('wget --limit-rate={} "{}" -O {} > /dev/null 2>&1'.format(wget_limit, download_url, file_name))
    os.system('gunzip -c ' + file_name + ' > ' + out_file)
    os.system('rm -rf ' + file_name)


def download_aliyun_cdnlog():
    cdn_name = "阿里云"
    SecretId = config['aliyun']['SecretId']
    SecretKey = config['aliyun']['SecretKey']
    credentials = AccessKeyCredential(SecretId, SecretKey)
    print("start")

    client = AcsClient(region_id='cn-beijing', credential=credentials)
    os.chdir("{}/aliyun".format(cdn_log_path))
    os.system('rm -rf *.log')
    # 获取cdn加速域名

    domain_name_all_list = list()
    request = DescribeUserDomainsRequest()
    request.set_accept_format('json')
    request.set_DomainStatus("online")
    response = client.do_action_with_exception(request)
    # python2:  print(response)
    data_dic = json.loads(str(response, encoding='utf-8'))['Domains']['PageData']
    for i in range(len(data_dic)):
        domain_name_all_list.append(data_dic[i]['DomainName'])
    # 根据域名列表下载日志
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
    print(domain_name_all_list)
    for i in range(len(domain_name_all_list)):
        print(domain_name_all_list[i])
        # request.set_DomainName(domain_name_all_list[i])
        # response = client.do_action_with_exception(request)
        # # python2:  print(response)
        # data_dic = json.loads(str(response, encoding='utf-8'))
        # log_info = data_dic['DomainLogDetails']['DomainLogDetail'][0]['LogInfos']['LogInfoDetail']
        # for d in range(len(log_info)):
        #     download_url = log_info[d]['LogPath']
        #     download_file(cdn_name, domain_name_all_list[i], download_url)

def download_qiniu_cdnlog():
    cdn_name = '七牛'
    accessKey = config['qiniu']['accessKey']
    secretKey = config['qiniu']['secretKey']
    auth = qiniu.Auth(accessKey, secretKey)
    os.chdir("{}/qiniu".format(cdn_log_path))
    os.system('rm -rf *.log')
    host = 'https://fusion.qiniuapi.com/v2/tune/log/list'
    cdn_manager = CdnManager(auth)
    domain_name = [
        'highso.cn',
        'static-grt-test.highso.com.cn',
        'pjm7yq5dk.bkt.clouddn.com',
        'p59gbi74v.bkt.clouddn.com',
        'testimg.highso.com.cn',
        'static.highso.com.cn',
        'oliifevjj.bkt.clouddn.com',
        'video.source.highso.com.cn',
        '7xu0qb.com2.z0.glb.qiniucdn.com',
        '7xu0qb.com2.z0.glb.clouddn.com',
        '7xu0qb.com1.z0.glb.clouddn.com',
        'enc-mp4.qiniudn.com',
        'm5-h.u.qiniudn.com',
        'haixue-log.qiniudn.com',
        'm5-h-b.qiniudn.com',
        '7xkkt9.dl1.z0.glb.clouddn.com',
        '7xav1k.dl1.z0.glb.clouddn.com',
        '7mnp33.com2.z0.glb.qiniucdn.com',
        '7mnozw.com2.z0.glb.qiniucdn.com',
        '7mnn8p.com2.z0.glb.qiniucdn.com',
        '7mnp33.com2.z0.glb.clouddn.com',
        '7mnozw.com2.z0.glb.clouddn.com',
        '7mnn8p.com2.z0.glb.clouddn.com',
        '7xav1k.com1.z0.glb.clouddn.com',
        '7mnp33.com1.z0.glb.clouddn.com',
        '7mnozw.com1.z0.glb.clouddn.com',
        '7mnn8p.com1.z0.glb.clouddn.com',
        'm5-q.highso.com.cn'
    ]
    data_dic = cdn_manager.get_log_list_data(domain_name, date_yesterday)

    log_info = data_dic[0]['data']
    for k, v in log_info.items():
        for d in range(len(v)):
            download_url = v[d]['url']
            download_file(cdn_name, k, download_url)


if __name__ == '__main__':
    work_path = os.getcwd()
    #dev
    cdn_log_path = '/Users/leo/Desktop/mydev/logs'
    app_log_path = '/Users/leo/Desktop/mydev/logs'
    #prod
    # cdn_log_path = '/data/logs/cdn'
    # app_log_path = '/tmp'
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='{}/download_cdn_{}'.format(app_log_path,
                                                             datetime.datetime.strftime(datetime.datetime.now(),
                                                                                        '%Y-%m-%d')),
                        filemode='w')
    date_today = datetime.datetime.today().date()
    date_yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    wget_limit = '4m'
    config = configparser.ConfigParser()
    config.read('{}/config/cdn.cfg'.format(work_path), encoding='UTF-8')

    '''
    pip install aliyun-python-sdk-cdn==3.7.1 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
     # https://github.com/TencentCloud/tencentcloud-sdk-python
    '''
    try:
        # qiniuCDN
        #download_qiniu_cdnlog()
        # 阿里云CDN

        download_aliyun_cdnlog()
    except Exception as err:
        logging.error("{}".format(err))
