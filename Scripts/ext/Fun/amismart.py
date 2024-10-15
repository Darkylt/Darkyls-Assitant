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

import hashlib
import random

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("amismart", "Am I smart?")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "Get the IQ of a different user", type=hikari.Member, required=False
)
@lightbulb.command("am_i_smart", "Are you smart?", auto_defer=True, pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def amismart_command(ctx: lightbulb.SlashContext, user=hikari.Member):
    if not await utils.validate_command(ctx):
        return

    if user is None:
        id = ctx.author.id
        mention = ctx.author.mention
        message = "Your IQ is {iq}."
    else:
        id = user.id
        mention = user.mention
        message = "{user}'s IQ is {iq}."

    # Special case handling
    if id == config.Bot.owner_id:
        await ctx.respond(message.format(iq="-∞", user=mention))
        return
    elif user.is_bot or user.is_system:
        await ctx.respond(message.format(iq="∞", user=mention))
        return

    # Hash the user ID to generate a deterministic seed for randomness
    hash_object = hashlib.sha256(str(id).encode())
    hex_dig = hash_object.hexdigest()
    seed = int(hex_dig[:8], 16)
    random.seed(seed)

    # Generate the IQ
    iq = random.randint(0, 200)

    await ctx.respond(message.format(iq=iq, user=mention))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
