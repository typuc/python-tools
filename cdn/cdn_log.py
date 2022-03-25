# -*-coding:UTF-8-*-
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdn.v20180606 import cdn_client, models
import os
import json
import wget
import time
import requests
import datetime

def download_tencent_cdnlog(domain_name,start_date,end_date):
    # 根据传入域名进行下载
    try:
        start_datetime = str(start_date)  + " 00:01:05"
        end_datetime = str(end_date) + " 00:00:05"
        req = models.DescribeCdnDomainLogsRequest()
        params = {"Domain": domain_name, "StartTime":  start_datetime, "EndTime": end_datetime}
        print(params)
        req.from_json_string(json.dumps(params))
        resp = client.DescribeCdnDomainLogs(req)
        download_url_list = json.loads(resp.to_json_string())
        for i in range(0, len(download_url_list["DomainLogs"])):
            download_url = download_url_list["DomainLogs"][i]["LogPath"]
            print(download_url)
            wget.download(download_url)
            time.sleep(0.2)
            file_name = wget.filename_from_url(download_url)
            os.system('gunzip -c ' + file_name + ' > ' + file_name + '.log')
            os.system('rm -rf ' + file_name)
    except TencentCloudSDKException as err:
        print(err)


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
def download_baishanyun_cdnlog(domain_name):
    # 根据传入域名进行下载
    url = 'https://cdn.api.baishan.com/v2/stat/log/getList?token='
    time_range = '&start_time={}&end_time={}'.format(date_yesterday,date_yesterday)
    #parm = '&domain={}'.format('bim-cdn.highso.com.cn')
    parm = '&domain={}'.format(domain_name)
    request_url = url + baishanyun_token + time_range + parm
    resp = requests.get(request_url).json()

    for i in range(0, len(resp['data'])):
        download_url = resp['data'][i]['url']
        print(download_url)
        file_name = domain_name + "-" + wget.filename_from_url(download_url)
        out_file = '{}.log'.format(file_name)
        #wget.download(download_url,out=file_name)
        os.system('wget --limit-rate=1024 ' + download_url + ' -O ' + file_name )
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
    #获取当天和前一天日期
    #date_today = "2020-09-14"
    #date_yesterday = "2020-09-08"
    date_today = datetime.datetime.today().date()
    date_yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    #腾讯CDN
    #workPath = os.getcwd()
    os.chdir("../tx")
    os.system('rm -rf *.log')
    cred = credential.Credential("111111", "11111")
    httpProfile = HttpProfile()
    httpProfile.endpoint = "cdn.tencentcloudapi.com"
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = cdn_client.CdnClient(cred, "", clientProfile)
    for d in get_tencent_cdn_domain_name():
        time.sleep(3)
        download_tencent_cdnlog(d,date_yesterday,date_today)
    #download_tencent_cdnlog('import.highso.com.cn', date_yesterday, date_today)
    #白山云CDN
    baishan_token = '11111'
    # os.chdir("bs")
    # os.system('rm -rf *.log')
    # # for d in get_baishanyun_cdn_domain_name():
    # #      download_baishanyun_cdnlog(d)
    # download_baishanyun_cdnlog('bccdn.enc-mp4.haixue.com')
