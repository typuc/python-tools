from rocketmq.client import Producer, Message, PushConsumer
import time, random
import json


def rocketmq_push(topic, num):
    n = 0
    producer.start()
    while n < num:
        s = ''
        msg = Message(topic)
        msg.set_keys('XXX')
        msg.set_tags('XXX')
        msg.set_body(s.join(random.sample('abcdefghijklmnopqrstuvwxyz', 5)))
        ret = producer.send_sync(msg)
        n = n + 1
        time.sleep(0.01)
        print(n)
    producer.shutdown()


def callback(msg):
    print(msg.id, msg.body)


if __name__ == '__main__':
    topic = 'xrf_test'
    producer = Producer(topic)
    add = '192.168.16.211:10911'
    producer.set_namesrv_addr(add)
    producer.set_session_credentials(access_key='rocketmq', access_secret='12345678', channel='4')
    print("start push")
    rocketmq_push(topic, 10)
    consumer = PushConsumer('CID_test_xrf')
    consumer.set_namesrv_addr(add)
    consumer.set_session_credentials(access_key='rocketmq', access_secret='12345678', channel='4')
    consumer.subscribe('xrf_test', callback)
    consumer.start()

    while True:
        time.sleep(10)

    consumer.shutdown()
