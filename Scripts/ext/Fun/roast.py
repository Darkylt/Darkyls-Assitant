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

import random
import re

import aiohttp
import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Roast", "Send some roasts")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "The user that shall be roasted!", type=hikari.Member, required=True
)
@lightbulb.option(
    "language",
    "The language the roast should be in",
    type=str,
    choices=["en", "de", "cn", "el", "es", "fr", "ru", "sw"],
    default="en",
    required=False,
)
@lightbulb.command("roast", "Roast someone!")
@lightbulb.implements(lightbulb.SlashCommand)
async def roast_command(ctx: lightbulb.SlashContext):
    """
    A command used to roast people

    Options:
        user (member): The member that should be roasted
        language (str): The language the roast should be in

    Processing:
        Responds when the bot is tagged (and returns)
        Defines the parameters for the API
        Gets response from the API
        Responds with the insult
    """
    if not await utils.validate_command(ctx):
        return

    user = getattr(ctx.options, "user", None)

    if user.id == plugin.bot.get_me().id:
        await ctx.respond(
            random.choice(
                [
                    "Heh, nice try. But no.",
                    "I see what you did there...but no.",
                    "Nope...",
                    "Roast yourself challenge? No thanks...",
                    "I'm not gonna roast myself.",
                    "You think you're clever or something?",
                    "Haha, so funny, asking the stupid bot to roast itself.😐",
                    "Leave me out of this!",
                    "Nice try, but I'm fireproof.",
                    "I'm not participating in a self-roasting session, sorry.",
                    "I'd roast myself, but I prefer to keep things cool.",
                    "Self-roasting? That's a bit too meta for my circuits.",
                    "I'm built to serve, not to self-destruct with roasts.",
                    "My code may be hot, but my roasts are not for self-consumption.",
                    "I'd roast myself, but I'm too busy serving up insults for others.",
                    "My processors are already being roasted by the stupid request you made",
                ]
            )
        )

    lang = getattr(ctx.options, "language", None)

    if lang is None:
        lang = "en"

    params = {"lang": lang, "type": "json"}

    url = "https://evilinsult.com/generate_insult.php"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    insult = data["insult"]
                    for word in config.Bot.censored_roast_words:
                        insult = re.sub(
                            r"\b" + re.escape(word) + r"\b",
                            "*" * len(word),
                            insult,
                            flags=re.IGNORECASE,
                        )
                    if user.id == ctx.author.id:
                        await ctx.respond(
                            f"{ctx.author.mention} roasted themselves: **{insult}**",
                            user_mentions=True,
                        )
                    else:
                        await ctx.respond(
                            f"{user.mention} **{insult}**", user_mentions=True
                        )
                else:
                    from bot import logger

                    logger.error(f"Failed to fetch insult: {response.status}")
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
