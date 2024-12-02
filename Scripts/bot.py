# Copyright (C) 2024  Darkyl

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/.

import datetime
import glob
import logging
import os
import time
import warnings
from logging.handlers import TimedRotatingFileHandler

import config_reader as config
import hikari
import hikari.channels
import hikari.errors
import hikari.permissions
import lavalink_rs
import lightbulb
import miru

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Initializing Bot
class Bot(lightbulb.BotApp):
    __slots__ = ("lavalink",)

    def __init__(self) -> None:
        super().__init__(
            token=config.Bot.token,
            default_enabled_guilds=(config.Bot.server, 811591956668219422),
            intents=hikari.Intents.ALL,
        )

        self.lavalink = lavalink_rs.LavalinkClient


bot = Bot()

# Initializing miru
miru_client = miru.Client(bot)

logging.basicConfig(level=logging.DEBUG)  # Set the default logging level

# with open(os.path.join(config.Paths.logs_folder, "latest.log"), 'w'):
#    pass

logger = logging.getLogger(__name__)


class Logging:
    """
    A class used for the bots logging.
    """

    async def log_message(log: str):
        """
        Sends a message into the logs channel on discord
        Args:
            log (str): The message
        """

        try:
            await bot.application.app.rest.create_message(
                config.Bot.logs_channel,
                log,
                user_mentions=False,
                mentions_everyone=False,
                mentions_reply=False,
            )
        except Exception as e:
            logger.error(f"Following error occured during log message: {e}")

    class LoggingExcludeFilter(logging.Filter):
        pass
        # def filter(self, record):
        #    # Suppress log message from google-api-python-client
        #    if ("file_cache is only supported with oauth2client<4.0.0" in record.getMessage() or
        #        "ssl.PROTOCOL_TLS is deprecated" in record.getMessage()):
        #        return False
        #    return True

    def configure_logging():
        """
        Setting up logging settings
        """

        # Cleaning up console
        suppressed = [
            "googleapicliet.discovery_cache",
            "lightbulb.internal",
            "hikari.gateway",
            "lightbulb.app",
        ]
        for pack_logger in suppressed:
            logging.getLogger(pack_logger).setLevel(logging.ERROR)

        latest_file_handler = logging.FileHandler(
            os.path.join(config.Paths.logs_folder, "latest.log")
        )
        latest_file_handler.setLevel(logging.DEBUG)

        # Create a TimedRotatingFileHandler to create log files with timestamps (e.g., 2024-05-03_12-00-00.log)
        filename = os.path.join(
            config.Paths.logs_folder,
            f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        )
        time_file_handler = TimedRotatingFileHandler(
            filename=filename, when="midnight", interval=1, backupCount=7
        )
        time_file_handler.setLevel(
            logging.DEBUG
        )  # Set the logging level for the file handler

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        latest_file_handler.setFormatter(formatter)
        time_file_handler.setFormatter(formatter)

        exclude_filter = Logging.LoggingExcludeFilter()
        latest_file_handler.addFilter(exclude_filter)
        time_file_handler.addFilter(exclude_filter)

        root_logger = logging.getLogger()
        root_logger.addHandler(latest_file_handler)
        root_logger.addHandler(time_file_handler)

    def purge_old_logs(logs_folder, retention_period):
        """
        A helper function for getting rid of out of date logs
        """
        current_time = time.time()
        for file_path in glob.glob(os.path.join(logs_folder, "*.log")):
            if os.stat(file_path).st_mtime < current_time - retention_period:
                os.remove(file_path)
