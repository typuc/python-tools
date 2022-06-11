# -*-coding:UTF-8-*-
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdn.v20180606 import cdn_client, models
import os
import json
import ssl
import requests
import datetime
import configparser
import logging
import wget
import time

### pip install tencentcloud-sdk-python

def get_tencent_cdn_domain_name():
    # 获取所有cdn加速域名并返回列表
    domain_name_all_list = list()
    try:
        req = models.DescribeDomainsConfigRequest()
        params = '{}'
        req.from_json_string(params)
        resp = client.DescribeDomainsConfig(req)
        domain_name_list = json.loads(resp.to_json_string())
        for i in range(0, len(domain_name_list["Domains"])):

            domain_name = domain_name_list["Domains"][i]["Domain"]
            print(domain_name)
            domain_name_all_list.append(domain_name)
        return domain_name_all_list
    except TencentCloudSDKException as err:
        print(err)

def download_tencent_cdnlog(domain_name, start_date, end_date):
    # 根据传入域名进行下载
    try:
        start_datetime = str(start_date) + " 00:00:00"
        end_datetime = str(end_date) + " 23:59:59"
        req = models.DescribeCdnDomainLogsRequest()
        params = {"Domain": domain_name, "StartTime": start_datetime, "EndTime": end_datetime}
        print(params)
        req.from_json_string(json.dumps(params))
        resp = client.DescribeCdnDomainLogs(req)
        download_url_list = json.loads(resp.to_json_string())
        #一个小时一个下载文件
        for i in range(0, len(download_url_list["DomainLogs"])):
            download_url = download_url_list["DomainLogs"][i]["LogPath"]
            #wget.download(download_url)
            file_name = domain_name + "-" + wget.filename_from_url(download_url)
            logging.info("开始下载域名：{} 日志 {}".format(domain_name,file_name))
            os.system('wget --limit-rate={} "{}" -O {}'.format(wget_limit, download_url, file_name))
            time.sleep(1)
            #下载完成后进行解压
            os.system('gunzip -c ' + file_name + ' > ' + file_name + '.log')
            os.system('rm -rf ' + file_name)
    except TencentCloudSDKException as err:
        logging.error("开始下载域名：{} error {}".format(domain_name, err))





def download_baishanyun_cdnlog(domain_name, start_date, end_date):
    # 根据传入域名进行下载
    start_datetime = str(start_date)
    end_datetime = str(end_date)
    url = 'https://cdn.api.baishan.com/v2/stat/log/getList?token='
    time_range = '&start_time={}&end_time={}'.format(start_datetime, end_datetime)
    # parm = '&domain={}'.format('bim-cdn.highso.com.cn')
    parm = '&domain={}'.format(domain_name)
    request_url = url + baishanyun_token + time_range + parm

    print(request_url)
    resp = requests.get(request_url).json()
    #读取日志下载地址
    for i in range(0, len(resp['data'])):
        download_url = resp['data'][i]['url']
        file_name = domain_name + "-" + wget.filename_from_url(download_url)
        out_file = '{}.log'.format(file_name)
        print(download_url)
        logging.info("开始下载域名：{} 日志 {}".format(domain_name, file_name))
        os.system('wget --limit-rate={} "{}" -O {}'.format(wget_limit, download_url, file_name))
        os.system('gunzip -c ' + file_name + ' > ' + out_file)
        os.system('rm -rf ' + file_name)


def get_baishanyun_cdn_domain_name():
    # 获取所有cdn加速域名并返回列表
    domain_name_all_list = list()
    url = 'https://cdn.api.baishan.com/v2/domain/list?token='
    parm = '&page_number=1&page_size=50&domain_status=serving'
    request_url = url + baishanyun_token + parm
    resp = requests.get(request_url).json()
    domain_name_list = resp['data']['list']
    for i in range(0, len(domain_name_list)):
        domain_name = domain_name_list[i]["domain"]
        print(domain_name)
        domain_name_all_list.append(domain_name)
    return domain_name_all_list


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='/tmp/download_cdn_{}'.format(
                            datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')),
                        filemode='w')
    # 获取当天和前一天日期
    # date_today = "2020-09-14"
    # date_yesterday = "2020-09-08"
    date_today = datetime.datetime.today().date()
    date_yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    wget_limit = "5m"
    work_path = os.getcwd()
    os.chdir(work_path)
    env = "dev"
    # 腾讯CDN
    #https://github.com/TencentCloud/tencentcloud-sdk-python
    config = configparser.ConfigParser()
    config.read('config/cdn.cfg', encoding='UTF-8')
    download_path = config[env]['download_path']
    SecretId = config['tencent']['SecretId']
    SecretKey = config['tencent']['SecretKey']
    baishanyun_token = config['baishanyun']['baishanyun_token']
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        # os.chdir("{}/tencent/".format(download_path))
        # os.system('rm -rf *.log')
        # cred = credential.Credential(SecretId, SecretKey)
        # httpProfile = HttpProfile()
        # httpProfile.endpoint = "cdn.tencentcloudapi.com"
        # clientProfile = ClientProfile()
        # clientProfile.httpProfile = httpProfile
        # client = cdn_client.CdnClient(cred, "", clientProfile)
        # for d in get_tencent_cdn_domain_name():
        #     time.sleep(3)
        #     download_tencent_cdnlog(d, date_yesterday, date_yesterday)
        # #download_tencent_cdnlog('www.haixuemeili.com', date_yesterday, date_today)
        # 白山云CDN
        os.chdir("{}/baishanyun/".format(download_path))
        print(os.getcwd())
        os.system('rm -rf *.log')
        # for d in get_baishanyun_cdn_domain_name():
        #     download_baishanyun_cdnlog(d)

        download_baishanyun_cdnlog('bccdn-video-source.haixue.com', '2022-06-06', '2022-06-06')
    except Exception as err:
        print(err)
        #logging.error("{}".format(err))