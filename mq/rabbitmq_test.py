import pika
import time


def callback(ch, method, properties, body):  # 定义一个回调函数，用来接收生产者发送的消息
    print('consum time {} {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), body.decode('utf-8')))


###推送
credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.16.211', '5672', '/', credentials))
# connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.16.228', '5672', '/', credentials))

# channel = connection.channel()
# n = 3
# print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
# while n > 0:
#     time.sleep(1)
#     channel.basic_publish(exchange='xrf_test_delay', routing_key='test', body='push time {} message {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), n))
#     #print('message {}'.format(n))
#     n = n - 1
# connection.close()
# ###消费
# connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.16.228', '5672', '/', credentials))
#
# channel = connection.channel()
# channel.basic_consume(on_message_callback=callback, queue='xrf_test_queue', auto_ack=True)
# channel.start_consuming()
# connection.close()
### x-delayed-message
channel = connection.channel()
message_body = 'push time {} x-delayed-message'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
# channel.exchange_declare(exchange="xrf_delayed_message", exchange_type="x-delayed-message",
#                          arguments={"x-delayed-type": "direct"})
# channel.queue_declare(queue='task_queue', durable=True)
# channel.queue_bind(queue="task_queue", exchange="test-x", routing_key="task_queue")
channel.basic_publish(exchange='xrf_delayed_message', routing_key='test', body=message_body,
                      properties=pika.BasicProperties(headers={"x-delay": 30000}))

connection.close()
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.16.228', '5672', '/', credentials))

channel = connection.channel()
channel.basic_consume(on_message_callback=callback, queue='xrf_test_queue', auto_ack=True)
channel.start_consuming()
