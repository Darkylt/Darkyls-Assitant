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

import bot_utils as utils
import buttons
import config_reader as config
import hikari
import lightbulb
import miru
import miru.client

plugin = lightbulb.Plugin("Custom Role", "Give a custom role to someone.")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.option(
    "role_name",
    "The name of the role",
    str,
    required=True,
    max_length=100,
    min_length=1,
)
@lightbulb.option(
    "user", "The user to assignt the role to", hikari.Member, required=True
)
@lightbulb.option("color", "Color in hex", str, required=False, default="95adad")
@lightbulb.command(
    "custom_role",
    "Give a custom role to someone.",
    pass_options=True,
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def custom_role_command(
    ctx: lightbulb.SlashContext, role_name: str, user: hikari.Member, color: str
):
    if not await utils.validate_command(ctx):
        return

    role = await plugin.app.rest.create_role(
        ctx.guild_id, name=role_name, color=hikari.Color.from_hex_code(color)
    )

    await plugin.app.rest.add_role_to_member(
        ctx.guild_id,
        user,
        role,
        reason=f"Custom role assigned by {ctx.author.username}.",
    )

    await ctx.respond(
        f"New role {role.mention} added to {user.mention}!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
