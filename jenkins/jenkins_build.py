import configparser
import requests
import jenkins
import time

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
    with open('list.txt', 'r') as f:
        for i in f.readlines():
            server.build_job(i.strip(), {'BRANCH': 'master'})
