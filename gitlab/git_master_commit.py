import gitlab
import time
import json
import sys
import re
import datetime
import requests
import pymysql

from elasticsearch7 import Elasticsearch


##api https://python-gitlab.readthedocs.io/en/1.3.0/api-usage.html

def es_wirte(json_data):
    es = Elasticsearch(url, timeout=120)
    # json_data ={ '@timestamp': '2021-08-02T13:20:51.000+08:00', 'project': <Project id:875>, 'author_email': 'tumingjian4586@haixue.com', 'short_id': '499d85e6', 'author_name': '涂铭鉴', 'branch': 'master'}
    es.index(index="gitlab_commit_log", body=json_data)


def branche_count(project):
    branch = project.branches.get('master')
    week_day_dict = {
        '1': '星期一',
        '2': '星期二',
        '3': '星期三',
        '4': '星期四',
        '5': '星期五',
        '6': '星期六',
        '7': '星期天',
        '0': '星期天',
    }
    end_date = datetime.datetime.now().date()
    start_date = (datetime.datetime.now().date() - datetime.timedelta(days=1))
    end_date = '2022-10-11'
    start_date = '2021-10-11'
    print(start_date, end_date, branch)
    commits = project.commits.list(ref_name="master", since=str(start_date) + 'T00:00:00.000+08:00',
                                   until=str(end_date) + 'T00:00:00.000+08:00', page=0, per_page=100000)
    n = 0
    a = 0
    for c in commits:

        if 'Merge' in c.message or c.author_name == "ucloudl-slave" or c.author_name == 'jenkins':
            n = n + 1
        else:
            week_day = datetime.datetime.strptime(c.created_at, '%Y-%m-%dT%H:%M:%S.000+08:00').strftime('%u')
            day_hour = datetime.datetime.strptime(c.created_at, '%Y-%m-%dT%H:%M:%S.000+08:00').strftime('%H')
            json_data = {
                "@timestamp": c.created_at,
                "project": project.name,
                "week_day": week_day_dict[week_day],
                "commit_hour": day_hour,
                "author_email": c.author_email,
                "short_id": c.short_id,
                "author_name": c.author_name,
                "branch": "master"}
            print(json_data)
        #     #es_wirte(json_data)


if __name__ == '__main__':
    ##api https://python-gitlab.readthedocs.io/en/1.3.0/api-usage.html
    # url = "http://192.168.16.213:9205"
    gl = gitlab.Gitlab.from_config('prod', '../config/gitlab.cfg')

    for a in gl.projects.list(all=True, order_by='name'):
        print(a.path_with_namespace)
        try:
            project = gl.projects.get(a.path_with_namespace)
            branche_count(project)
            time.sleep(1)
        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                print('*' * 30)
                print('项目{} 未找到!'.format(a.path_with_namespace))
            pass

