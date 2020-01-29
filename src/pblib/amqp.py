import pika
import threading
from os import environ
from time import sleep
import traceback


def getAmqpData():
    host = environ.get("MQ_HOST")
    username = environ.get("MQ_USERNAME")
    password = environ.get("MQ_PASSWORD")
    port = int(environ.get("MQ_PORT")) if environ.get("MQ_PORT") is not None else 5672
    vhost = environ.get("MQ_VHOST") if environ.get("MQ_VHOST") is not None else "/"

    if host is None or username is None or password is None:
        return {}

    result = {'host': host, 'user': username, 'password': password, 'port': port, 'vhost': vhost}
    return result


class client():
    def publish(client, toExchange, routingKey, message):
        connection = client.getConnection()
        channel = client.getChannel(connection)

        channel.basic_publish(exchange=toExchange, routing_key=routingKey, body=str(message))
        print(" [x] Sent: " + str(message))

        connection.close()

    def addConsumer(name, queue, bindings, callback):
        t = threading.Thread(target=client.receive, name=name, args=([name, queue, bindings, callback]))
        t.daemon = True
        t.start()

    def receive(name, queue, bindings, callback):
        try:
            connection = client.getConnection(client)
            channel = client.getChannel(client, connection)
            channel.add_on_cancel_callback(client.onCancel)

            for fromExchange in bindings:
                client.setupChannel(client, channel, queue, fromExchange)
                for withRoutingKeys in bindings[fromExchange]:
                    client.addBinding(channel, queue, fromExchange, withRoutingKeys)

            channel.basic_consume(queue, callback, consumer_tag=name)
            print(' [*] Waiting for messages. To exit press CTRL+C')

            channel.start_consuming()
        except Exception as error:
            if (str(error) == 'onCancel'):
                print('Got a basic.cancel message from amqp. Trying to restart the consumer...')
            else:
                print(traceback.format_exc())
                print(error)
                print("Consumer broke unexpectedly, trying to restart the consumer...")

            print("Restarting consumer...")
            sleep(3)
            client.addConsumer(name, queue, bindings, callback)
            return False

    # default callback when message is received, prints the message and ack's it
    def printReceivedMessage(ch, method=None, properties=None, body=None):
        print(" [x] Received %r" % body)
        ch.basic_ack(method.delivery_tag)

    ######################################################
    # From now on, the functions are mainly internal     #
    # Make sure you know what you're doing if you change #
    # something behind this point                        #
    ######################################################

    def getCredentials(client):
        data = getAmqpData()
        credentials = pika.PlainCredentials(data['user'], data['password'])
        return credentials

    def getParameters(param):
        data = getAmqpData()
        parameters = pika.ConnectionParameters(data['host'], data['port'], data['vhost'], client.getCredentials(param))
        return parameters

    def getConnection(param):
        parameters = client.getParameters(param)
        connection = pika.BlockingConnection(parameters)
        return connection

    def getChannel(client, connection):
        channel = connection.channel()
        return channel

    def setupChannel(client, channel, queue, fromExchange, exchange_type='topic'):
        channel.exchange_declare(exchange=fromExchange, exchange_type=exchange_type, passive=False, durable=True,
                                 auto_delete=False, internal=False)
        channel.queue_declare(queue=queue)
        channel.basic_qos(prefetch_count=1)

    def addBinding(channel, queue, fromExchange, withRoutingKeys):
        channel.queue_bind(queue=queue, exchange=fromExchange, routing_key=withRoutingKeys)

    def onCancel(channel):
        raise Exception('onCancel')
