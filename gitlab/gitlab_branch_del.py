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
        if re.match(r'^test', b.name):
            test[b.name] = b.commit["committed_date"]
        if re.match(r'^hotfix', b.name):
            hotfix[b.name] = b.commit["committed_date"]
        if re.match(r'^feature', b.name):
            feature[b.name] = b.commit["committed_date"]
        if re.match(r'^auto_release', b.name):
            auto_release[b.name] = b.commit["committed_date"]

    # 判断分支是否为空
    if len(test) > 0:
        branches_list.append({'test': test})
    if len(hotfix) > 0:
        branches_list.append({'hotfix': hotfix})
    if len(feature) > 0:
        branches_list.append({'feature': feature})
    if len(auto_release) > 0:
        branches_list.append({'auto_release': auto_release})
    # 遍历分支类型
    del_count = 0
    for b in branches_list:
        # 遍历指定分支类型中所有分支
        for k_b, v_b in b.items():
            # 根据提交时间对分支进行排序
            d_sorted_by_value = sorted(v_b.items(), key=lambda x: x[1], reverse=True)
            # 获取最新分支时间
            branches_newest_name = d_sorted_by_value[0][0]
            branches_newest_date = datetime.strptime(d_sorted_by_value[0][1], "%Y-%m-%dT%H:%M:%S.%f+08:00")
            # 获取最新创建日期
            n = 0
            for k, v in d_sorted_by_value:
                branches_commit_date = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f+08:00")
                # 判断当前分支最后一次提交是否在指定天数以前，90天默认
                if (branches_newest_date - branches_commit_date).days > days:
                    n = n + 1
                    print('{} 删除成功'.format(k))
                    #project.branches.delete(k)
                    del_count = del_count + 1
                    del_all = n

            if n > 0:
                print('-' * 30)
                print('{} {} 分支总数{}, 删除分支 {}'.format(team_project, k_b, len(d_sorted_by_value),n))

    # print('*' * 60)
    print('{} 总共删除分支 {}'.format(team_project, del_count))


if __name__ == '__main__':
    ##api https://python-gitlab.readthedocs.io/en/1.3.0/api-usage.html
    gl = gitlab.Gitlab.from_config('prod', 'gitlab.config')
    # 根据项目名字进行查找
    with open('../git_list.txt', 'r') as f:
        for i in f:
            team_project = i.strip('\n')
            try:
                project = gl.projects.get(team_project)
                days = 90
                test, hotfix, feature, auto_release = ({}, {}, {}, {})
                # 获取所有分支
                # print('*' * 60)
                # print("清理项目{}".format(team_project))
                get_all_delete_branche(project)
                time.sleep(1)
            except gitlab.exceptions.GitlabGetError as e:
                if e.response_code == 404:
                    print('*' * 30)
                    print('项目{} 未找到!'.format(team_project))
                pass
        del_all = 0
        # print('*' * 60)
        # print('删除分支 {}'.format(del_all))