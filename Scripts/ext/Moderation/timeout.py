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

plugin = lightbulb.Plugin("timeout", "Timeout a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MODERATE_MEMBERS))


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(
    hikari.Permissions.MODERATE_MEMBERS, dm_enabled=False
)
@lightbulb.option("reason", "the reason for the timeout", type=str, required=False)
@lightbulb.option(
    "days", "the duration of the timeout (days)", type=int, required=False, default=0
)
@lightbulb.option(
    "hours", "the duration of the timeout (hour)", type=int, required=False, default=0
)
@lightbulb.option(
    "minutes",
    "the duration of the timeout (minute)",
    type=int,
    required=False,
    default=0,
)
@lightbulb.option(
    "seconds",
    "the duration of the timeout (second)",
    type=int,
    required=False,
    default=0,
)
@lightbulb.option(
    "user", "the user you want to be put in timeout", type=hikari.Member, required=True
)
@lightbulb.command("timeout", "Timeout a member", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def timeout_command(
    ctx: lightbulb.SlashContext,
    user: hikari.Member,
    seconds: int,
    minutes: int,
    hours: int,
    days: int,
    reason: str,
):
    """
    A command to timeout a user

    Processing:
        Get the amount of time to timeout for
        Apply the timeout
        Respond
    """

    if not await utils.validate_command(ctx):
        return

    reason = reason or f"No Reason Provided."
    now = datetime.datetime.now()
    then = now + datetime.timedelta(
        days=days, hours=hours, minutes=minutes, seconds=seconds
    )

    if (then - now).days > 28:
        await ctx.respond(
            "You can't time someone out for more than 28 days",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        # Adding the actual timeout
        await ctx.bot.rest.edit_member(
            user=user,
            guild=ctx.get_guild(),
            communication_disabled_until=then,
            reason=reason,
        )
    except hikari.errors.ForbiddenError:
        await ctx.respond(
            "I do not have permission to timeout the user.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while trying to timeout user: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            await ctx.respond(
                f"Removing timeout from **{user.mention}**",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            from bot import Logging

            await Logging.log_message(
                f"The user {user.mention} had their timeout removed."
            )
            await user.send("Your timeout was removed.")
        else:
            await ctx.respond(
                f"The user {user.mention} has been timed out until <t:{int(then.timestamp())}:R> for `{reason}`",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            from bot import Logging

            await Logging.log_message(
                f"The user {user.mention} has been timed out until <t:{int(then.timestamp())}:R> for `{reason}`"
            )
            await user.send(
                f"You have been timed out until <t:{int(then.timestamp())}:R> for `{reason}`"
            )
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /timeout while responding: {e}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
