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

import buttons
import hikari
import lightbulb
import miru
import timed_events

plugin = lightbulb.Plugin("startup", "Containing functions called at startup")


async def wait_until_initialized():
    """
    Wait until the bot is fully initialized and bot.application.app exists.
    """
    while not (
        hasattr(plugin.bot, "application")
        and getattr(plugin.bot.application, "app", None)
    ):
        await asyncio.sleep(1)


@plugin.listener(hikari.StartedEvent)
async def on_startup(event: hikari.StartedEvent):
    """
    Gets called when the bot starts.
    """
    from bot import logger

    logger.info("Bot is online")

    # Set status
    try:
        await plugin.bot.update_presence(
            status=hikari.Status.ONLINE,
            activity=hikari.Activity(name="Darkyl", type=hikari.ActivityType.LISTENING),
        )
    except Exception as e:
        logger.error(f"An error occurred during startup while updating presence: {e}")

    # Start button views
    try:
        await buttons.ManageViews.start_views(
            miru.Client(plugin.bot),
            views=[
                buttons.VerifyView,
                buttons.ReactionRoles.Descriptor,
                buttons.ReactionRoles.Pronouns,
                buttons.ReactionRoles.Region,
                buttons.ReactionRoles.Pings,
                buttons.Report,
                buttons.Worm,
                buttons.ModMenu,
                buttons.NSFWOptIn,
                buttons.NSFWOptOut,
                buttons.RockPaperScissors,
                buttons.RockPaperScissorsReplay,
                buttons.Confess,
                buttons.Test,
                buttons.HelpMenu,
            ],
        )

    except Exception as e:
        logger.error(f"An error occurred during startup while starting views: {e}")

    await wait_until_initialized()

    # Running background tasks
    try:
        asyncio.create_task(timed_events.run_events(plugin.bot))
    except Exception as e:
        logger.error(f"An error occurred during startup while starting timers: {e}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
