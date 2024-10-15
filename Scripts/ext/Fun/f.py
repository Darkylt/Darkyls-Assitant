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

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("F", "Pay your respects!")

hearts = ["❤", "💛", "💚", "💙", "💜", "♥", "o7"]


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "text", "What do you want to pay respect to?", required=False, type=str
)
@lightbulb.command(
    "f", "Press F to pay respect.", pass_options=True, aliases=["respect"]
)
@lightbulb.implements(lightbulb.SlashCommand)
async def f_command(ctx: lightbulb.SlashContext, text: str):
    if not await utils.validate_command(ctx):
        return

    reason = f"for **'{text}'** " if text else ""

    await ctx.respond(
        f"**{ctx.author.mention}** has paid their respect {reason}{random.choice(hearts)}"
    )


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("respect", "Press F to pay respect.")
@lightbulb.implements(lightbulb.MessageCommand)
async def f_message_command(ctx: lightbulb.Context):
    if ctx.author.is_bot or ctx.author.is_system:
        return

    from bot import logger

    logger.info(f"{ctx.author.username} used respect message command.")  #

    message = getattr(ctx.options, "target", None)
    author = message.author  #

    msg = await plugin.app.rest.fetch_message(ctx.channel_id, message)

    await msg.respond(
        f"**{ctx.author.mention}** has paid their respect for {author.mention}{random.choice(hearts)}",
        reply=msg,
        mentions_reply=True,
    )

    await ctx.respond("Respects paid o7", flags=hikari.MessageFlag.EPHEMERAL)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
