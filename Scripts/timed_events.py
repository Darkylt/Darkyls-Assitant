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

import asyncio
import json
import os
import random

import config_reader as config
import hikari
import schedule


async def choose_random_tip():
    """
    Chooses a random fact from the tips.json

    Returns:
        random_fact: str
            The selected random tip as a string.
        None
            If an error occurred
    """
    try:
        with open(
            os.path.join(config.Paths.assets_folder, "Text", "tips.json"), "r"
        ) as file:
            data = json.load(file)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while trying to load tips.json {e}")
        return None

    try:
        string_list = data["tips"]

        random_fact = random.choice(string_list)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while trying to read tips.json: {e}")
        return None

    return random_fact


async def send_random_tip(bot, fact: str) -> bool:
    """
    A function used for sending the selected tip in a nice embed.

    Args:
        bot (object):
            The bot app object
        fact (str):
            The random fact as a string
    Returns:
        True: Success
        False: Fail
    """
    try:
        thumbnail = hikari.File(
            os.path.join(config.Paths.assets_folder, "logo_300x300.png")
        )

        embed = hikari.Embed(
            title="**Random Music Production tip of the day!**",
            description="Here's your daily random production tip",
        )
        embed.set_thumbnail(thumbnail)
        embed.add_field(name="**Tip:**", value=fact, inline=False)

        await bot.application.app.rest.create_message(
            config.Bot.random_tips_channel, embed=embed, role_mentions=True
        )
        return True
    except Exception as e:
        from bot import logger

        logger.error(f"Error while sending random tip: {e}")
        return False


async def random_tip(bot):
    """
    Sends a random tip

    Processing:
        Chooses a random tip
        Sends the chosen random tip
    """
    if config.Bot.random_tips:
        fact = await choose_random_tip()

        if fact is None:
            return

        await send_random_tip(bot=bot, fact=fact)
        return
    else:
        return


async def run_events(bot):
    schedule.every().day.at("12:00").do(lambda: asyncio.create_task(random_tip(bot)))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)
