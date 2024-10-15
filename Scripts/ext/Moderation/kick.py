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

plugin = lightbulb.Plugin("Kick", "Kick a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.KICK_MEMBERS))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.KICK_MEMBERS, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS))
@lightbulb.option("user", "The user that should be kicked", type=hikari.OptionType.USER)
@lightbulb.option(
    "reason", "Why is the user being banned?", type=str, required=False, default=None
)
@lightbulb.command(
    "kick", "Kick a user", pass_options=True, auto_defer=True, ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def kick_command(ctx: lightbulb.SlashContext, user: hikari.User, reason: str):
    """
    A command to kick a user.

    It processes the provided info and then kicks the user.

    Processing:
        Retrieving provided information
        Fetching the user
        Kicking the user
        Responding and logging
    """

    if not await utils.validate_command(ctx):
        return

    try:
        guild_id = ctx.guild_id
        user_id = user.id
        user_name = user.global_name

        try:
            await ctx.app.rest.kick_user(guild=guild_id, user=user_id, reason=reason)
            await ctx.respond(
                f"User {user.mention} ({user_name}) has been kicked successfully.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

            from bot import Logging

            await Logging.log_message(
                f"User {user.mention} ({user_name}) has been kicked by {ctx.author.mention}. Reason: {reason}"
            )

        except hikari.errors.ForbiddenError:
            await ctx.respond(
                "I do not have permission to kick the user.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

        except hikari.errors.NotFoundError:
            await ctx.respond(
                "The user could not be found.", flags=hikari.MessageFlag.EPHEMERAL
            )

        except Exception as e:
            from bot import logger

            logger.error(f"An error occurred while trying to kick the user: {e}")
            await ctx.respond(
                "An error occurred while trying to kick the user. Please try again later.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during the /kick command: {e}")
        await ctx.respond(
            f"An error occurred! {await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
