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

import os

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Allow URL", "Add a URL to the allow list")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.option("url", "Domain name without https:// or anything", str, required=True)
@lightbulb.command(
    "allow_url",
    "Add a URL to the allow list",
    pass_options=True,
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def allow_url(ctx: lightbulb.SlashContext, url: str) -> None:
    if not await utils.validate_command(ctx):
        return

    if url.startswith("http"):
        await ctx.respond(
            "Must be domain name only. For example: darkylmusic.com instead of https://darkylmusic.com"
        )
        return

    if "/" in url:
        await ctx.respond(
            "Must be domain name only. For example: darkylmusic.com instead of https://darkylmusic.com/discord-bot/"
        )
        return

    if url.count(".") > 1:
        await ctx.respond(
            "Must be domain name only. For example: darkylmusic.com instead of https://example.darkylmusic.com or www.darkylmusic.com"
        )
        return

    allow_list_path = os.path.join(config.Paths.data_folder, "whitelisted_sites.txt")

    try:
        with open(allow_list_path, "a") as file:
            file.write(f"\n{url}")
        await ctx.respond(f"The URL `{url}` has been added to the allow list.")
    except Exception as e:
        await ctx.respond(f"An error occurred while adding the URL: {e}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
