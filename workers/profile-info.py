#!/usr/bin/env python3

import asyncio
import json

import aiovk
import pika

from workers.config import config
from workers.logger import logger

RABBIT_HOST = config.get("APP", "RABBIT_HOST")
RABBIT_QUEUE = config.get("APP", "RABBIT_QUEUE")

APP_ID = config.get("API", "APP_ID", fallback=0)
APP_SCOPE = config.get("API", "APP_SCOPE", fallback=0)


def callback(channel, method, properties, body):
    try:
        request = json.loads(body)
        login = request["login"]
        password = request["password"]

        logger.info(" [x] Received a new login/password pair")
        asyncio.run(main(login, password))
    except Exception as e:
        logger.critical(" [x] An error occurred: %s" % e)


async def main(login, password):
    session = aiovk.ImplicitSession(login=login,
                                    password=password,
                                    app_id=APP_ID,
                                    scope=APP_SCOPE)
    logger.debug(" [x] Authorizing attempt")
    await session.authorize()

    api = aiovk.API(session)

    logger.debug(" [x] Requesting profile info")
    user_info = await api("account.getProfileInfo")

    logger.info(" [x] First/Last name: %s %s" %
                (user_info["first_name"], user_info["last_name"]))

    await session.close()


def start_consuming():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST))
    except:
        logger.critical(" [x] Error rabbitmq connecting. Exiting")
        exit()

    channel = connection.channel()

    channel.queue_declare(queue=RABBIT_QUEUE)
    channel.basic_consume(queue=RABBIT_QUEUE,
                          auto_ack=True,
                          on_message_callback=callback)

    logger.info(" [x] Waiting for profile requests")
    channel.start_consuming()


if __name__ == "__main__":
    logger.info(" [x] Initializing application")
    start_consuming()

    exit()
