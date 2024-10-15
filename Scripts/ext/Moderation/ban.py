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
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("Ban", "Bans a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))

time_durations = {
    "1 Hour": 3600,
    "5 Hours": 18000,
    "12 Hours": 43200,
    "1 Day": 86400,
    "2 Days": 172800,
    "3 Days": 259200,
    "4 Days": 345600,
    "5 Days": 432000,
    "6 Days": 518400,
    "7 Days": 604800,  # Max value I think
}


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option(
    "user", "The user that should be banned.", required=True, type=hikari.Member
)
@lightbulb.option("reason", "Why is the user being banned?", required=True, type=str)
@lightbulb.option(
    "delete_messages",
    "How far back should messages be deleted?",
    required=False,
    choices=list(time_durations.keys()),
    default=None,
)
@lightbulb.option(
    "notify_user",
    "Should I notify the user about the ban?",
    bool,
    required=False,
    default=True,
)
@lightbulb.command(
    "ban", "Ban a user", pass_options=True, auto_defer=True, ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def ban_command(
    ctx: lightbulb.SlashContext,
    user: hikari.Member,
    reason: str,
    delete_messages: str,
    notify_user: bool,
) -> None:
    """
    A command to ban a user.

    It processes the provided info and then bans the user.

    Processing:
        Retrieving provided information
        Fetching the user
        Mapping of delete messages options to time durations
        Banning the user
        Responding and logging
    """

    if not await utils.validate_command(ctx):
        return

    try:
        message_timer = time_durations.get(delete_messages, 0)

        user_name = user.global_name

        await plugin.bot.application.app.rest.ban_user(
            guild=ctx.guild_id,
            user=user.id,
            reason=reason,
            delete_message_seconds=message_timer,
        )

        await ctx.respond(
            "User has been banned successfully.", flags=hikari.MessageFlag.EPHEMERAL
        )

        from bot import Logging

        await Logging.log_message(
            f"User {user.mention} ({user_name}) has been banned by {ctx.author.mention}. Reason: {reason}"
        )

        # Notify the banned user (if possible)
        if notify_user:
            try:
                dm_channel = await user.fetch_dm_channel()
                if dm_channel:
                    await dm_channel.send(
                        f"You have been banned from **{ctx.get_guild().name}** for: {reason}"
                    )
            except Exception as dm_error:
                from bot import logger

                logger.warning(f"Failed to send DM to banned user: {dm_error}")

    except hikari.errors.ForbiddenError:
        await ctx.respond(
            "I do not have permission to ban the user.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    except KeyError:
        await ctx.respond(
            "Invalid option provided for message deletion time.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during the /ban command: {e}")
        await ctx.respond(
            "An error occurred while processing the command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
