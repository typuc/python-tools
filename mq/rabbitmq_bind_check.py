#!/bin/python3
# 
import json


new_config = 'mq_new.config'
old_config = 'mq_old.config'

new_bindings = set()
old_bindings = set()
new_queue = set()
old_queue = set()
new_exchange = set()
old_exchange = set()
with open(new_config, 'r') as f:
    config_json = json.load(f)
    new_queue_number = len(config_json['queues'])
    new_exchanges_number = len(config_json['exchanges'])
    bindings = config_json['bindings']
    for q in range(0, len(config_json['queues'])):
        new_queue.add(config_json['queues'][q]['name'])
    for e in range(0, len(config_json['exchanges'])):
        new_exchange.add(config_json['exchanges'][e]['name'])
    for binding in bindings:
        queue_key = binding['destination'] + '@' + binding['routing_key'] + '@' + binding['source']
        #print(queue_key)
        new_bindings.add(queue_key)
with open(old_config, 'r') as f:
    config_json = json.load(f)
    bindings = config_json['bindings']
    old_queue_number = len(config_json['queues'])
    old_exchanges_number = len(config_json['exchanges'])
    for q in range(0, len(config_json['queues'])):
        old_queue.add(config_json['queues'][q]['name'])
    for e in range(0, len(config_json['exchanges'])):
        old_exchange.add(config_json['exchanges'][e]['name'])
    for binding in bindings:
        queue_key = binding['destination'] + '@' + binding['routing_key'] + '@' + binding['source']
        old_bindings.add(queue_key)
delta_bindings = old_bindings - new_bindings
delta_queue = old_queue - new_queue
delta_exchange = old_exchange - new_exchange
if delta_bindings:
    for i in delta_bindings:
        print(i)
elif delta_queue:
    for i in delta_queue:
        print("当前配置比如前一个检查周期缺少队列：".format(i))
elif delta_exchange:
    for i in delta_queue:
        print("当前配置比如前一个检查周期缺少exchange".format(i))
