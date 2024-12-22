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

# hehe

import re

import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("69", "Does you message add up to 69?")


async def extract_numbers(text: str) -> list:
    # Use regular expression to match both integers and floating point numbers
    numbers = re.findall(r"\d+\.\d+|\d+", text)
    # Convert matched strings to float or int as needed
    return [float(num) if "." in num else int(num) for num in numbers]


@plugin.listener(hikari.GuildMessageCreateEvent)
async def check(event: hikari.GuildMessageCreateEvent):
    if not config.Fun.enable_69:
        return

    author = event.message.author
    message = event.message
    if author.is_bot or author.is_system:
        return

    content = message.content

    if content:
        numbers = await extract_numbers(content)

        if numbers:
            total = sum(numbers)
            if total == 69:
                await message.add_reaction(emoji="69:1320385142040035358")

                if config.Fun.enable_69_message and len(numbers) > 1:
                    formatted_numbers = " + ".join(map(str, numbers))

                    response = f"All of the numbers in your message add up to 69!:\n\n```{formatted_numbers} = 69```"

                    await message.respond(response, mentions_reply=False, reply=message)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
