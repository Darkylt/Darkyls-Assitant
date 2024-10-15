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

import asyncio
import datetime
import json

import aiohttp
import bot_utils as utils
import buttons
import config_reader as config
import hikari
import hikari.messages
import lightbulb
import miru
import miru.client

plugin = lightbulb.Plugin("Test", "Some test stuff for admins")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


ENABLED = True


async def test(ctx: lightbulb.SlashContext):

    modal = buttons.MyModal()
    builder = modal.build_response(miru.client.Client)

    await builder.create_modal_response(ctx.interaction)

    miru.Client.start_modal(modal)


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.command("admin_test", "A command used for testing / setting up the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def test_command(ctx: lightbulb.SlashContext):
    """
    A command used to test the bot.
    It performs some basic checks and then executes the test() function
    """
    if not await utils.validate_command(ctx):
        return

    try:
        if not ctx.author.id == config.Bot.owner_id:
            await ctx.respond(
                "This command can only be used by Darkyl.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        if not ENABLED:
            await ctx.respond("Command disabled.", flags=hikari.MessageFlag.EPHEMERAL)
            return
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while processing the /admin_tst command {e}")

    try:
        await test(ctx)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during the test: {e}")


event = hikari.events.StartedEvent


async def wait_until_initialized():
    """
    Wait until the bot is fully initialized and bot.application.app exists.
    """
    while not (
        hasattr(plugin.bot, "application")
        and getattr(plugin.bot.application, "app", None)
    ):
        await asyncio.sleep(1)


@plugin.listener(event)
async def test_event(event: event) -> None:

    await wait_until_initialized()


#    asyncio.create_task(check_minecraft())


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
