#!/usr/bin/env python3

import asyncio
import json
import os
import time

import aiovk
import aiovk.mixins
import pika
from aiovk.exceptions import VkAuthError
from aiovk.parser import AuthPageParser

from workers.packages.config import config
from workers.packages.logger import logger

RABBIT_HOST = config.get("APP", "RABBIT_HOST")
RABBIT_QUEUE = config.get("APP", "RABBIT_QUEUE", fallback="profile")
APP_ID = config.get("API", "APP_ID")
APP_SCOPE = config.get("API", "APP_SCOPE")
LOGS_PATH = config.get("APP", "LOGS_PATH")


def callback(channel, method, properties, body):
    try:
        request = json.loads(body)
        login = request["login"]
        password = request["password"]

        logger.info("Received a new login/password pair")
        asyncio.run(main(login, password))
    except Exception as e:
        logger.critical("An error occurred: %s" % e)

# this an override of external class;
# we need it because the library has some issues; will be refactored later
class VkSession(aiovk.ImplicitSession):
    async def enter_captcha(self, url, sid):
        bytes = await self.driver.get_bin(url, {})
        with open('captcha.jpg', 'wb') as f:
            f.write(bytes)
        return input("Enter captcha: ")

    async def enter_confirmation_сode(self):
        return input('Enter confirmation сode: ')

    async def _process_auth_form(self, html: str) -> (str, str):
        """
        Parsing data from authorization page and filling the form and submitting the form

        :param html: html page
        :return: url and  html from redirected page
        """
        # Parse page
        p = AuthPageParser()
        p.feed(html)
        p.close()

        # Get data from hidden inputs
        form_data = dict(p.inputs)
        form_url = p.url
        form_data['email'] = self.login
        form_data['pass'] = self.password
        if p.message:
            # Show form errors
            raise VkAuthError('invalid_data', p.message, form_url, form_data)
        elif p.captcha_url:
            form_data['captcha_key'] = await self.enter_captcha(
                "{}".format(p.captcha_url),
                form_data['captcha_sid']
            )
            form_url = "{}".format(form_url)

        # Send request
        url, html = await self.driver.post_text(form_url, form_data)
        return url, html


async def main(login, password):
    session = VkSession(login=login,
                        password=password,
                        app_id=APP_ID,
                        scope=APP_SCOPE)
    logger.debug("Authorizing attempt")
    await session.authorize()

    api = aiovk.API(session)

    logger.debug("Requesting profile info")
    user_info = await api("account.getProfileInfo")

    logger.info("First/Last name: %s %s" %
                (user_info["first_name"], user_info["last_name"]))

    if not os.path.exists(LOGS_PATH):
        os.mkdir(LOGS_PATH)

    user_id = user_info["id"]
    file_name = time.strftime(f"{user_id}-%Y.%m.%d-%H.%M.%S.json")

    with open(f"{LOGS_PATH}\\{file_name}", "w+", encoding="utf-8") as file:
        json.dump(user_info, file, indent=4, ensure_ascii=False)

    await session.close()


def start_consuming():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST))
    except:
        logger.critical("Error rabbitmq connecting. Exiting")
        exit()

    channel = connection.channel()

    channel.queue_declare(queue=RABBIT_QUEUE)
    channel.basic_consume(queue=RABBIT_QUEUE,
                          auto_ack=True,
                          on_message_callback=callback)

    logger.info("Waiting for profile requests")
    channel.start_consuming()


if __name__ == "__main__":
    logger.info("Initializing application")
    start_consuming()

    exit()
