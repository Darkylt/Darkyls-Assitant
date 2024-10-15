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

import database_interaction as db
import hikari
import lightbulb

plugin = lightbulb.Plugin("Leave", "Removes a user from the databse if they leave")


@plugin.listener(hikari.events.MemberDeleteEvent)
async def leave(event: hikari.MemberDeleteEvent) -> None:

    db.Users.delete_user_entry(user_id=event.user_id)
    db.Messages.delete_messages_by_author(author_id=event.user_id)
    db.Commands.delete_commands_by_user(user_id=event.user_id)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
