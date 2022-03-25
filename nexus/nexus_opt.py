import xml.etree.ElementTree as ET
import re
import requests
from datetime import datetime, timedelta
import time
import configparser
# 获取所有版本和打包时间
def nexus_get_artifact(service_name, repo, repo_path):
    version_list = {}
    request_uri = '{}/{}{}{}/'.format(url, repo, repo_path, service_name)
    #print(request_uri)
    resp = requests.get(url=request_uri, auth=auth)
    #print(resp)
    if resp.status_code == 404:
        return version_list
    root = ET.fromstring(resp.text)
    version_re = re.compile(r'(\d{1,3})')

    for e in root.iterfind('data/content-item/resourceURI'):
        # 通过正则匹配版本号
        url_last = e.text
        #print(e.text)
        version_now = e.text.split('{}/'.format(service_name))[1]
        # print(version_now)
        if version_re.match(version_now):
            version = version_now.split('/')[0]
            version_url = '{}{}/'.format(request_uri, version)
            resp_version = requests.get(url=version_url, auth=auth)
            version_root = ET.fromstring(resp_version.text)
            version_result = version_root.findall('data/content-item/lastModified')
            if version_result:
                version_time = version_result[0].text
                # #  获取当前版本所有构建物时间，只取第一个
                #version_time = version_root.findall('data/content-item/lastModified')[0].text
                #print(version_root.findall('data/content-item/lastModified'))
                get_time = datetime.strptime(version_time, "%Y-%m-%d %H:%M:%S.0 UTC").strftime("%Y-%m-%d %H:%M:%S")
                # 保存版本和构建时间
                version_list[version] = get_time
                #print(version)

    return version_list


# 执行删除
def exec_del(service_name, del_version, del_uri):
    time.sleep(0.01)
    # print(del_uri)
    resp = requests.delete(url=del_uri, auth=auth)
    if resp.status_code == 204:
        print("{} {} del succcess".format(service_name, del_version))
    else:
        print("{} {} del faild".format(service_name, del_version))


# 执行nexus历史版本请求
def nexus_del_artifact(service_name, repo, repo_path, version_keep_number, version_keep_day):
    #获取指定仓库下服务的所有历史版本
    version_list = nexus_get_artifact(service_name, repo, repo_path,)
    if len(version_list) == 0:
        print('{} {} 未找到匹配版本'.format(service_name, repo))
        return 0

    request_uri = '{}/{}{}{}/'.format(url, repo, repo_path, service_name)
    today = datetime.now()
    # version_list = {'1.0.0': '2020-11-02 12:48:27', '1.0.1': '2020-11-03 10:01:02', '1.0.2': '2020-11-04 02:20:39'}
    # 通过版本时间进行倒序排列结果
    a = sorted(version_list.items(), key=lambda x: x[1], reverse=True)
    n = 0
    # releases保留最近1年版本或者最少10个版本
    if repo == 'releases':
        version_keep_number = 10
        if len(a) > version_keep_number:
            for i in range(version_keep_number, len(a)):
                # 获取删除版本，日期
                version_now = a[i][0]
                version_date = a[i][1]
                del_uri = "{}{}/".format(request_uri, version_now)
                ###del
                exec_del(service_name, version_now, del_uri)
                n = n + 1

            # 获取需要删除版本
            # for i in range(version_keep_number, len(a)):
            #     # 获取删除版本，日期
            #     version_now = a[i][0]
            #     version_date = a[i][1]
            #     # 判断当前版本是否超过最大保留天数
            #     if (today - datetime.strptime(version_date, '%Y-%m-%d %H:%M:%S')).days > version_keep_day:
            #         n = n + 1
            #         del_uri = "{}{}/".format(request_uri, version_now)
            #         ###del
            #         exec_del(service_name, version_now, del_uri)
        print('{} 版本总数：{} 删除历史版本 {}'.format(service_name, len(a), n))
    #其他仓库保留最近5个版本
    else:
        if len(a) > version_keep_number:
            # 获取需要删除版本
            for i in range(version_keep_number, len(a)):
                # 获取删除版本，日期
                version_now = a[i][0]
                version_date = a[i][1]
                del_uri = "{}{}/".format(request_uri, version_now)
                ###del
                exec_del(service_name, version_now, del_uri)
                n = n + 1
            print('{} {} 版本总数：{} 删除历史版本 {}'.format(service_name, repo, len(a), n))

        else:
            print('{} {} 版本总数：{} 删除历史版本 {}'.format(service_name, repo, len(a), 0))
    return 0

### start at here
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../config.cfg', encoding='UTF-8')
    url = config['nexus']['url']
    username = config['nexus']['username']
    password = config['nexus']['password']
    auth = (username, password)
    repo = 'snapshots'
    # nexus_del_artifact('jjxt-service-api', 'snapshots', 5, 180)
    with open('service_list.txt', 'r') as f:
        for s in f.readlines():
            print(s)
            print(username)
            # repo_path = s.split()[0].split('releases')[1]
            # service_name = s.split()[1].strip()
            # nexus_del_artifact(service_name, repo, repo_path, 5, 365)

