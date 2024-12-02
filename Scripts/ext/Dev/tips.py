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

import json
import os

import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb
import timed_events

plugin = lightbulb.Plugin("Tips", "Some commands for managing daily tips")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.option("tip", "The tip that should be added to the document", type=str)
@lightbulb.command("admin_add_tip", "Add a tip to the random daily tips")
@lightbulb.implements(lightbulb.SlashCommand)
async def add_tip_command(ctx: lightbulb.SlashContext):
    """
    A command used to add a new tip to the list of tips.

    Processing:
        Checks if the command is run by darkyl
        Reads the existing data
        Adds the new tip
        Writes the updated file
        Responds
    """

    try:
        if ctx.author.id != config.Bot.owner_id:
            await ctx.respond(
                "Only darkyl can add tips.", flags=hikari.MessageFlag.EPHEMERAL
            )
            return

        database = os.path.join(config.Paths.assets_folder, "Text", "tips.json")

        if os.path.exists(database) and os.path.getsize(database) > 0:
            with open(database, "r") as file:
                data = json.load(file)
        else:
            data = {"tips": []}

        tip = getattr(ctx.options, "tip", None, flags=hikari.MessageFlag.EPHEMERAL)

        if tip is None:
            await ctx.respond("Couldn't read tip")
            return

        data["tips"].append(tip)

        with open(database, "w") as file:
            json.dump(data, file, indent=4)

        await ctx.respond("Tip added successfully!", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occcurred during /admin_add_tip command: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("admin_send_tip", "Trigger the send tip event")
@lightbulb.implements(lightbulb.SlashCommand)
async def trigger_tip_command(ctx: lightbulb.SlashContext):
    """
    A command used to trigger sending the tip.

    Processing:
        Triggers the tip
        Responds
    """

    try:
        if not await utils.validate_command(ctx):
            return

        await timed_events.random_tip(plugin.bot)

        await ctx.respond(
            "The tip has been sent :)", flags=hikari.MessageFlag.EPHEMERAL
        )
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during /admin_send_tip command: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
