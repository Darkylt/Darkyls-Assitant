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
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("SlowMode", "Set the slowmode for a channel")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_CHANNELS))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "interval",
    "The interval amount (in seconds)",
    type=int,
    min_value=0,
    max_value=21600,
    required=True,
)
@lightbulb.option(
    "channel",
    "The channel you want to set",
    hikari.TextableGuildChannel,
    required=False,
)
@lightbulb.app_command_permissions(
    hikari.permissions.Permissions.MANAGE_CHANNELS, dm_enabled=False
)
@lightbulb.command(
    "slowmode", "Set the slowmode interval for a channel", pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def slowmode_command(
    ctx: lightbulb.SlashContext, channel: hikari.TextableGuildChannel, interval: int
):
    """
    A command to set the slowmode for a channel

    Processing:
        Gets the provided info and performs some basic checks
        Applies the slowmode
        Responds
    """

    if not await utils.validate_command(ctx):
        return

    time = interval

    if channel is None:
        channel = ctx.get_channel()

    if time < 0:
        await ctx.respond(
            f"The parameter 'interval' has to be a positive number",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    try:
        await ctx.bot.rest.edit_channel(channel, rate_limit_per_user=time)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occcurred while attempting to set slowmode: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    if time == 0:
        await ctx.respond(
            f"Removed slow mode from selected {channel.mention}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    else:
        if time > 1:
            await ctx.respond(
                f"Slowmode of {time} seconds has been set for {channel.mention}",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        if time <= 1:
            await ctx.respond(
                f"Slowmode of {time} second has been set for {channel.mention}",
                flags=hikari.MessageFlag.EPHEMERAL,
            )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
