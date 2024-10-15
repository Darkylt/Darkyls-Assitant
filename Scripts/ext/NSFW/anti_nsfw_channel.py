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

plugin = lightbulb.Plugin("anti_nsfw", "Prevent creation of nsfw")

ENABLED = True


@plugin.listener(hikari.events.GuildChannelUpdateEvent)
async def anti_nsfw(event: hikari.events.GuildChannelUpdateEvent) -> None:
    if ENABLED:
        if event.channel.guild_id == config.Bot.server:
            if event.channel.is_nsfw:
                await event.channel.edit(nsfw=False)
                from bot import logger

                logger.info(
                    f"Someone tried to update #{event.channel.name}({event.channel.id}) to NSFW. I reverted the change."
                )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
