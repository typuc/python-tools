import gitlab
import datetime
import time
import json
import sys
import re
from datetime import datetime, timedelta
import requests
##api https://python-gitlab.readthedocs.io/en/1.3.0/api-usage.html

def get_all_delete_branche(project):

    branches_list = []
    # 获取当前项目所有分支
    project_branches = project.branches.list()
    #     if re.match(r'^{}'.format(b_t),b.name) :
    # 对分支名称开头进行判断，test,feature,hotfix
    for b in project_branches:
        if re.match(r'^master', b.name):
            test[b.name] = b.commit["committed_date"]

if __name__ == '__main__':
    ##api https://python-gitlab.readthedocs.io/en/1.3.0/api-usage.html
    gl = gitlab.Gitlab.from_config('prod', '../config/gitlab.config')
    # 根据项目名字进行查找
    n = 0
    with open('../git_list.txt', 'r') as f:
        for i in f:
            team_project = i.strip('\n')
            try:
                project = gl.projects.get(team_project)
                commits = project.commits.list(since='2021-01-01T00:00:00Z', until='2021-06-30T23:59:59Z', ref_name='master', lazy=True)
                if len(commits) > 0:
                    print("{},{}".format(team_project,len(commits)))
                time.sleep(1)
            except gitlab.exceptions.GitlabGetError as e:
                if e.response_code == 404:
                    print('*' * 30)
                    #print('项目{} 未找到!'.format(team_project))
                pass
        del_all = 0
        # print('*' * 60)
        # print('删除分支 {}'.format(del_all))