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
import lightbulb

plugin = lightbulb.Plugin(
    "Show Avatar", "Display someones avatar for your viewing pleasure."
)


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "target", "The person with the avatar you wanna view", type=hikari.User
)
@lightbulb.command(
    "show_avatar",
    "Display someones avatar for your viewing pleasure.",
    pass_options=True,
    auto_defer=True,
    ephemeral=True,
    aliases=["pfp", "icon"],
)
@lightbulb.implements(lightbulb.SlashCommand)
async def show_avatar_command(ctx: lightbulb.SlashContext, target: hikari.User):
    if not await utils.validate_command(ctx):
        return

    await ctx.respond(
        f"Here is {target.mention}'s Avatar:", attachment=target.display_avatar_url
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
