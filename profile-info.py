#!/usr/bin/env python3

import asyncio
import json

import aiovk
import pika

from logger import info, critical, debug

APP_ID = 4544367
APP_SCOPE = 140492255

QUEUE_NAME = "profile"
RABBIT_HOST = "localhost"


def callback(channel, method, properties, body):
    try:
        request = json.loads(body)
        login = request["login"]
        password = request["password"]

        info(" [x] Received a new login/password pair")
        asyncio.run(main(login, password))
    except Exception as e:
        critical(" [x] An error occurred: %s" % e)


async def main(login, password):
    session = aiovk.ImplicitSession(login=login,
                                    password=password,
                                    app_id=APP_ID,
                                    scope=APP_SCOPE)
    debug(" [x] Authorizing attempt")
    await session.authorize()

    api = aiovk.API(session)

    debug(" [x] Requesting profile info")
    user_info = await api("account.getProfileInfo")

    info(" [x] First/Last name: %s %s" %
         (user_info["first_name"], user_info["last_name"]))

    await session.close()


def start_consuming():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST))
    except:
        critical(" [x] Error rabbitmq connecting. Exiting")
        exit()

    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME,
                          auto_ack=True,
                          on_message_callback=callback)

    info(" [x] Waiting for profile requests")
    channel.start_consuming()


if __name__ == "__main__":
    info(" [x] Initializing application")
    start_consuming()

    exit()
