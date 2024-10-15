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

plugin = lightbulb.Plugin("Stop", "A stop command for admins")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.command("admin_stop", "Stop the Bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def stop_command(ctx: lightbulb.SlashContext) -> None:
    """
    A command that gracefully shuts down the bot if executed by the specified user.
    """
    from bot import logger

    try:
        if ctx.author.id == config.Bot.owner_id:

            await ctx.respond(
                "Bot is shutting down.", flags=hikari.MessageFlag.EPHEMERAL
            )
            logger.info(f"{ctx.author.id} executed /{ctx.command.name}")
            await plugin.bot.update_presence(status=hikari.Status.OFFLINE)
            await plugin.bot.close()
            logger.info("Bot shut down by command.")

        else:

            await ctx.respond(
                "You are not permitted to shut down the Bot",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

    except (hikari.errors.NotFoundError, hikari.errors.ForbiddenError) as e:
        logger.error(f"Error occurred during /admin_stop command: {e!r}")
        await ctx.respond(
            f"An error occurred! {await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    except Exception as e:
        logger.error(f"Unexpected error during /admin_stop command: {e!r}")
        await ctx.respond(
            "An unexpected error occurred!", flags=hikari.MessageFlag.EPHEMERAL
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
