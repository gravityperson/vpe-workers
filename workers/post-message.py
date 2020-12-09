#!/usr/bin/env python3

import json
import sys

import pika

QUEUE_NAME = "profile"
RABBIT_HOST = "localhost"


def post_message(channel, message):
    channel.basic_publish(exchange="",
                          routing_key=QUEUE_NAME,
                          body=message)
    print(" [x] Sent '%s'" % message)


if __name__ == "__main__":
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    login = sys.argv[1]
    password = sys.argv[2]

    post_message(channel, json.dumps({"login": login, "password": password}))
    connection.close()

    exit()
