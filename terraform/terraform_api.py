# /bin/env python
# -*- coding: UTF-8 -*-import json
import os
import re
import requests
import json
import sys, getopt

def gen_terraform_var(hosts):
    uhost_type_count = {}
    ali_ecs_type_count = {}
    '''统计机器类型和数量'''
    for k, v in hosts.items():
        uhost_type_count[k] = len(v)
        ali_ecs_type_count['ali_ecs_' + k] = len(v)
    ali_ecs_type_num = ""
    for k, v in ali_ecs_type_count.items():
        ali_ecs_type_num = ali_ecs_type_num + "{} = {} \n".format(k, v)

        with open("temp/alicloud_instance_temp", "r") as f:
            for line in f.readlines():
                line.replace('temp_instance', k)
                with open("tmp/alicloud_instance.tf", "a") as o:
                    o.writelines(line.replace('temp_instance', k) + '\n')
    print(ali_ecs_type_num)


def get_origin_lb_backend(hosts, lb_name):
    ip_list = list()
    for k, v in hosts.items():
        for i, ng in v.items():
            if ng == lb_name:
                ip_list.append(i)
    return ip_list


def get_origin_type_ip(hosts):
    origin_type_ip = {}
    for k, v in hosts.items():
        ip_list = list()
        for i, t in v.items():
            ip_list.append(i)
        ip_list.sort()
        origin_type_ip[k] = ip_list
    return origin_type_ip


def get_ecs_type_ip():
    #os.system("cd {} && terraform output -json > tmp/ecs_out.tf".format(terraform_path))
    #os.system("cp temp/test_output.tf  tmp/output.tf")
    false = False
    re_ip = re.compile(r'^ip')
    ali_ecs_ip_id = {}
    with open("tmp/ecs_out.tf", 'r') as out:
        terraform_output = json.load(out)
    ali_ecs_ip = {}
    for k, v in terraform_output.items():
        if re_ip.match(k) and len(v['value']) != 0:
            # 获取ecs类型
            ali_ecs_type = k.split('ali_ecs_')[1]
            # 存储当前类型所有IP地址
            ali_ecs_ip[ali_ecs_type] = v['value']
            ali_ecs_id = terraform_output["id_ali_ecs_{}".format(ali_ecs_type)]["value"]
            # 读取当前类型ecs IP地址和id对应关系
            for ip in range(0, len(v['value'])):
                ali_ecs_ip_id[v['value'][ip]] = ali_ecs_id[ip]
    return ali_ecs_ip, ali_ecs_ip_id


def gen_slb_backend_ids(origin_ulb, ip_to_ip, ip_id):
    #生成slb和ecs ids对应关系
    #os.system("cp temp/test_output.tf  tmp/output.tf".format(terraform_path))
    for k, v in origin_ulb.items():
        ecs_id = list()
        for i in range(0, len(v)):
            ecs_id.append(ip_id[ip_to_ip[v[i]]])
        #根据slb模版生成terraform文件
        os.system("cp temp/alicloud_slb_temp  tmp/alicloud_slb_{}.tf".format(k))
        print("{} slb: backend server ids:{}".format(k, ecs_id))
        with open("tmp/alicloud_slb_{}.tf".format(k), "r") as f:
            for line in f.readlines():
                e = json.dumps(ecs_id)
                r1 = line.replace("temp_backend", e.split('"')[1])
                r2 = (r1.replace("temp_slb", k))
                with open("tmp/alicloud_slb.tf", "a") as o:
                    o.writelines(r2 + "\n")


def call_backup_tools(ip_to_ip):
    body = json.dumps(ip_to_ip)
    uri = "/api/disaster/serverDistribution"
    headers = {'content-type': "application/json"}
    req = requests.post(http_host + uri, headers=headers, data=body)
    if req.status_code == 200:
        print("call back successful")
    else:
        print("call back status {}".format(req.status_code))


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hcb:")
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('terraform_api.py -c ecs #创建虚拟机')
            print('terraform_api.py -b ecs #绑定虚拟机到slb')
            sys.exit()
        elif opt == "-c":
            # 生成机器型号和数量,通过模版生成配置文件片段,比如 8c32g: 4(台）
            os.system("rm tmp/*")
            gen_terraform_var(ucloud_uhost)
        elif opt == "-b":
            # 获取生产机房机器类型包含的IP集合
            old_ip = get_origin_type_ip(ucloud_uhost)

            # main(sys.argv[1:])

            # 获取新创建机器IP
            new_ip = get_ecs_type_ip()[0]
            # 获取创建机器ip和id对应关系
            new_ip_id = get_ecs_type_ip()[1]
            print(new_ip_id)
            # 生成原始机器和创建机器的IP对应关系 {"old_ip": "new_ip"}
            dic_ip_to_ip = dict()
            for k, v in old_ip.items():
                for i in range(0, len(v)):
                    dic_ip_to_ip[old_ip[k][i]] = new_ip[k][i]
            # # 返回新老IP地址给工具平台
            call_backup_tools(dic_ip_to_ip)
            # # 生成新lb与后段服务器id对应关系
            gen_slb_backend_ids(ucloud_ulb_backend, dic_ip_to_ip, new_ip_id)


if __name__ == '__main__':
    http_host = "http://toolkit.h.highso.com.cn"
    uri = "/api/disaster/serverDistribution"
    #获取工具平台当前机器信息
    ucloud_uhost = requests.get(http_host + uri, "rehearsal=true").json()
    ucloud_uhost1 = {
        "1c1g": {"10.9.140.156": "normal", "10.9.49.251": "www"},
        "8c32g": {"10.9.170.16": "normal", "10.9.117.226": "kong", "10.9.165.36": "normal"},
        "16c64g": {"10.9.14.111": "www", "10.9.116.198": "crm", "10.9.83.55": "normal"}
    }
    ulb_list = ["crm", "kong", "www"]
    ucloud_ulb_backend = dict()

    # 获取ucloud业务线lb后端nginx IP对应关系
    for lb in range(0, len(ulb_list)):
        backend_list = get_origin_lb_backend(ucloud_uhost, ulb_list[lb])
        if backend_list is not None:
            ucloud_ulb_backend[ulb_list[lb]] = backend_list
    #主函数，功能选择
    main(sys.argv[1:])