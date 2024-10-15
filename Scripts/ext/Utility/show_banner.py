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
    "Show Banner", "Display someones Banner for your viewing pleasure."
)

# FOR SOME REASON TARGET.BANNER_URL IS NONE EVEN IF THE USER HAS A BANNER WTF

# @plugin.command
# @lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
# @lightbulb.option("target", "The person with the avatar you wanna view", type=hikari.User)
# @lightbulb.command("show_banner", "Display someones Banner for your viewing pleasure.", pass_options=True, auto_defer=True, ephemeral=True)
# @lightbulb.implements(lightbulb.SlashCommand)
# async def show_banner_command(ctx: lightbulb.SlashContext, target: hikari.User):
#    if not await utils.validate_command(ctx):
#        return

#    banner = target.banner_url

#    print(banner)

#    if banner:
#        await ctx.respond(f"Here is {target.mention}'s Banner:", attachment=banner)
#    else:
#        await ctx.respond(f"{target.mention} doesn't have a Banner set.")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
