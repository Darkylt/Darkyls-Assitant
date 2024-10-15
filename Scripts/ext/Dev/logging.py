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

import config_reader as config
import hikari
import lightbulb
from bot import Logging

plugin = lightbulb.Plugin("logging", "Logging events")


@plugin.listener(hikari.BanCreateEvent)
async def on_ban(event: hikari.BanCreateEvent):
    """
    A function for logging a ban
    """
    ban = await event.fetch_ban()

    await plugin.app.rest.create_message(
        config.Bot.logs_channel,
        f"{ban.user.username} was banned for {ban.reason}",
        user_mentions=False,
        mentions_everyone=False,
        mentions_reply=False,
    )


@plugin.listener(hikari.BanDeleteEvent)
async def on_unban(event: hikari.BanDeleteEvent):
    """
    A function for logging an unban
    """
    user = await event.fetch_user()

    await plugin.app.rest.create_message(
        config.Bot.logs_channel,
        f"{user.username} was unbanned.",
        user_mentions=False,
        mentions_everyone=False,
        mentions_reply=False,
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
