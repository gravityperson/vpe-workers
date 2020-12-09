import configparser
import os

from workers import __PATH__
from workers.packages.logger import logger

QUEUE_NAME = "profile"
RABBIT_HOST = "localhost"
CONFIG_FILE = f"{__PATH__}\\config.ini"

if not os.path.exists(CONFIG_FILE):
    logger.critical(" [x] Config file is missing")
    exit()

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

config.add_section("APP")
config.set("APP", "RABBIT_HOST", RABBIT_HOST)
config.set("APP", "RABBIT_QUEUE", QUEUE_NAME)