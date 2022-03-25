# -*-coding:UTF-8-*-
import etcd
import sys
import json


# client.write('/skydns/local/highso/node1/rabbitmq-common/auto','192.168.1.1')
# result = client.read('/skydns/local/highso/node1/rabbitmq-common/auto')
# print(result.key,result.value)


def etcd_update():
    n = 0
    ##修改dns
    with open(file, 'r') as f:
        for line in f:
            l_list = line.split()
            domain = l_list[0]
            ip = l_list[2]
            res = domain.strip().split('.')
            domain_key = url
            for i in range(len(res) - 1, -1, -1):
                domain_key = domain_key + '/' + res[i]
            value_ip = {"host": ip}
            value_ip_str = json.dumps(value_ip)
            client.write(domain_key, value_ip_str)
            n = n + 1
    print("修改记录 {} 成功".format(n))


def etcd_recovery():
    ###还原dns
    n = 0
    with open(file, 'r') as f:
        for line in f:
            l_list = line.split()
            domain = l_list[0]
            ip = l_list[1]
            res = domain.strip().split('.')
            domain_key = url
            for i in range(len(res) - 1, -1, -1):
                domain_key = domain_key + '/' + res[i]
            value_ip = {"host": ip}
            value_ip_str = json.dumps(value_ip)
            client.write(domain_key, value_ip_str)
            result = client.read(domain_key)
            print(result.key, result.value)
            n = n + 1
        print("修改记录 {} 成功".format(n))

if __name__ == '__main__':
    args = sys.argv[1]
    print(args)
    #args = 'modify'
    url = '/skydns'
    file = 'disconf/dns.txt'
    #conn_host = '192.168.16.243'
    conn_host = '192.168.1.201'
    client = etcd.Client(host=conn_host, port=2379)
    # etcd_update(d, i)
    if args == 'modify':
        etcd_update()
    elif args == 'recovery':
        etcd_recovery()
    else:
        print("输入选择错误，只支持 modify 或者 recovery ")



