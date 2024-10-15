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

import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("Purge", "Purge messages from a channel")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MODERATE_MEMBERS))


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "channel",
    "The channel you want to set",
    hikari.TextableGuildChannel,
    required=False,
)
@lightbulb.option(
    "amount", "The number of messages to purge.", type=int, required=True, max_value=500
)
@lightbulb.app_command_permissions(hikari.Permissions.MANAGE_MESSAGES, dm_enabled=False)
@lightbulb.command(
    "purge",
    "Purge messages from this channel.",
    aliases=["clear", "prune"],
    auto_defer=True,
    ephemeral=True,
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def purge_command(
    ctx: lightbulb.SlashContext, channel: hikari.TextableGuildChannel, amount: int
) -> None:
    """
    Deletes all messages from a channel

    Processing:
        Performs some quick checks on the inputs
        Fetches all the messages that fit the criteria
        Deletes them
        Responds
    """
    if not await utils.validate_command(ctx):
        return

    if amount > 500:
        await ctx.respond(
            "You can only purge 500 messages at once, max",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if channel is None:
        channel = ctx.get_channel()

    iterator = (
        ctx.bot.rest.fetch_messages(channel)
        .limit(amount)
        .take_while(
            lambda msg: (
                datetime.datetime.utcnow() - msg.created_at.replace(tzinfo=None)
            )
            < datetime.timedelta(days=14)
        )
    )
    if iterator:
        async for messages in iterator.chunk(50):
            await ctx.bot.rest.delete_messages(channel, messages)
        # await ctx.respond(f"**Messages has been sucessfully deleted.**", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond(
            "Could not find any messages younger than 14 days!",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
