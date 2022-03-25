import configparser
import requests
import jenkins
import time

def jenkins_reload():
    with open('jenkins_test0.xml', 'r') as f:
        for s in f.readlines():
            service_name = s.strip()
            url = 'http://jenkins.highso.com.cn/job/{}/reload'.format(service_name)
            auth = (user_ID, api_token)
            resp = requests.post(url=url, auth=auth)
            if resp.status_code == 200:
                print('reload {} '.format(service_name))
            else:
                print('reload1111 {} '.format(service_name))
            time.sleep(0.1)

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('../config/jenkins.cfg', encoding='utf-8')
    url = config['test']['jenkins_url']
    print(url)
    jenkins_url = config['test']['jenkins_url']
    username = config['test']['username']
    password = config['test']['password']
    user_ID = config['test']['password']
    api_token = config['test']['api_token']
    project = 'merchant-test0-goods-mgt'
    jenkins_url = 'http://jenkins.test0.highso.com.cn'
    server = jenkins.Jenkins(jenkins_url, username=username, password=password)
    print(server.get_job_info('merchant-test0-goods-mgt')['lastCompletedBuild'])

