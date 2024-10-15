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

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Fakemod", "Troll people")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option(
    "user", "The user you want to fake ban", type=hikari.OptionType.USER, required=True
)
@lightbulb.option(
    "channel",
    "The channel you want to send the message in",
    type=hikari.TextableGuildChannel,
    required=False,
    default=None,
)
@lightbulb.option(
    "reason", "Why should the user be banned?", type=str, required=False, default=None
)
@lightbulb.command(
    "fakeban", "Do some trolling by fake banning someone", pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def fakeban_command(
    ctx: lightbulb.SlashContext,
    user: hikari.User,
    channel: hikari.TextableGuildChannel,
    reason: str,
):
    if not await utils.validate_command(ctx):
        return

    await ctx.respond("✅", flags=hikari.MessageFlag.EPHEMERAL)

    if not channel:
        channel = ctx.channel_id

    if not reason:
        reason = "No reason provided"

    await plugin.app.rest.create_message(
        channel=channel,
        content=f"{user.mention} was banned for: '{reason}'!",
        user_mentions=True,
    )


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.KICK_MEMBERS, dm_enabled=False)
@lightbulb.option(
    "user", "The user you want to fake kick", type=hikari.OptionType.USER, required=True
)
@lightbulb.option(
    "channel",
    "The channel you want to send the message in",
    type=hikari.TextableGuildChannel,
    required=False,
    default=None,
)
@lightbulb.option(
    "reason", "Why should the user be kicked?", type=str, required=False, default=None
)
@lightbulb.command(
    "fakekick", "Do some trolling by fake kicking someone", pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def fakeban_command(
    ctx: lightbulb.SlashContext,
    user: hikari.User,
    channel: hikari.TextableGuildChannel,
    reason: str,
):
    if not await utils.validate_command(ctx):
        return

    await ctx.respond("✅", flags=hikari.MessageFlag.EPHEMERAL)

    if not channel:
        channel = ctx.channel_id

    if not reason:
        reason = "No reason provided"

    await plugin.app.rest.create_message(
        channel=channel,
        content=f"{user.mention} was kicked for: '{reason}'!",
        user_mentions=True,
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
