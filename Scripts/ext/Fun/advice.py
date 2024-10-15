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

import json

import aiohttp
import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("advice", "Let me give you some useful advice!")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("advice", "Let me give you some useful advice!")
@lightbulb.implements(lightbulb.SlashCommand)
async def advice_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return

    url = "https://api.adviceslip.com/advice"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = json.loads(await response.read())
                    advice = data["slip"]["advice"]
                    await ctx.respond(f"Here's some advice for you: {advice}")
                else:
                    from bot import logger

                    logger.error(f"Failed to fetch advice: {response.status}")
                    await ctx.respond(
                        f"An error occurred!{await utils.error_fun()}",
                        flags=hikari.MessageFlag.EPHEMERAL,
                    )
    except Exception as e:
        from bot import logger

        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
