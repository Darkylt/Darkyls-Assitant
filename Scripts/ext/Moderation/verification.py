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

plugin = lightbulb.Plugin("Verify", "Helping with verification")


@plugin.listener(hikari.events.DMMessageCreateEvent)
async def on_message(event: hikari.events.DMMessageCreateEvent) -> None:
    if event.author.is_bot or event.author.is_system:
        return

    from Verification import captcha, captcha_db

    if await captcha_db.get_id_from_user(event.author_id):
        if event.message.content.lower() == "regenerate":
            await captcha.regenerate(plugin.bot, event.author_id)
            return

        await captcha.verify_solution(event.message)
    else:
        return


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
