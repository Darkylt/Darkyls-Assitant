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
import buttons
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Rock Paper Scissors", "Play Rock Paper Scissors")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("rock_paper_scissors", "Play Rock Paper Scissors.")
@lightbulb.implements(lightbulb.SlashCommand)
async def rps_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return

    view = buttons.RockPaperScissors()

    await ctx.respond("Choose your option!", components=view)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
