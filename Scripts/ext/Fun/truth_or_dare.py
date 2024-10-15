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

import aiohttp
import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("truth_or_dare", "Play truth or dare")


@plugin.command
@lightbulb.add_cooldown(5, 5, lightbulb.UserBucket)
@lightbulb.option("type", "Truth or Dare?", choices=("Truth", "Dare"))
@lightbulb.option(
    "category", "Type of question.", choices=("normal", "nsfw"), default="normal"
)
@lightbulb.option(
    "language",
    "A language other than english?",
    choices=("en", "bn", "de", "es", "fr", "hi", "tl"),
    default="en",
)
@lightbulb.command(
    "truth_or_dare", "Get a truth or dare question.", aliases=["trd"], pass_options=True
)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def truth_or_dare_command(
    ctx: lightbulb.context.SlashContext, type, category, language
) -> None:
    if category == "nsfw":
        nsfw = True
        rating = "r"
    else:
        nsfw = False
        rating = "pg13"

    if not await utils.validate_command(ctx, nsfw=nsfw):
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.truthordarebot.xyz/v1/{type}?rating={rating}"
        ) as resp:
            if resp.status != 200:
                await ctx.respond("Failed to get a question. Please try again later.")
                return
            response = await resp.json()

            if "question" not in response:
                await ctx.respond("Unexpected response format. Please try again later.")
                return

            if language == "en":
                question = response["question"]
            else:
                question = response["translations"][language]

    embed = hikari.Embed(
        title=f"**{type}** Question:",
        description=question,
        color=0x00FF00 if category == "normal" else 0xFF0000,
    )

    embed.set_author(name=ctx.author.username, icon=ctx.author.avatar_url)

    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
