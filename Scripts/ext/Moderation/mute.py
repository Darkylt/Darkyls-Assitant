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

plugin = lightbulb.Plugin("mute", "Handles muting and umuting a member")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MODERATE_MEMBERS))


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user", "The user you want to mute", hikari.Member, required=True)
@lightbulb.app_command_permissions(
    hikari.Permissions.MODERATE_MEMBERS, dm_enabled=False
)
@lightbulb.command(
    "mute", "Mute a user.", auto_defer=True, pass_options=True, ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def mute_command(ctx: lightbulb.SlashContext, user: hikari.Member) -> None:
    if not await utils.validate_command(ctx):
        return

    muted_role = config.Bot.muted_role
    verified_role = config.Bot.verified_role

    roles = await user.fetch_roles()

    if any(role.id == muted_role for role in roles):
        await ctx.respond(f"{user.mention} is already muted.")
        return

    await user.add_role(muted_role, reason=f"Muted by {ctx.author.username}")
    await user.remove_role(verified_role, reason=f"Muted by {ctx.author.username}")
    await ctx.respond(f"{user.mention} has been muted.")


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user", "The user you want to unmute", hikari.Member, required=True)
@lightbulb.app_command_permissions(
    hikari.Permissions.MODERATE_MEMBERS, dm_enabled=False
)
@lightbulb.command(
    "unmute", "Unmute a user.", auto_defer=True, pass_options=True, ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def unmute_command(ctx: lightbulb.SlashContext, user: hikari.Member) -> None:
    if not await utils.validate_command(ctx):
        return

    muted_role = config.Bot.muted_role
    verified_role = config.Bot.verified_role

    roles = await user.fetch_roles()

    if any(role.id == muted_role for role in roles):
        await user.remove_role(muted_role, reason=f"Unmuted by {ctx.author.username}")
        await user.add_role(verified_role, reason=f"Unmuted by {ctx.author.username}")
        await ctx.respond(f"{user.mention} has been unmuted.")
        return

    await ctx.respond(f"{user.mention} is not currently muted.")


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(
    hikari.Permissions.MODERATE_MEMBERS, dm_enabled=False
)
@lightbulb.command(
    "configure_mute_role",
    "Give the mute role the proper restrictions.",
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def configure_mute_role_command(ctx: lightbulb.SlashContext) -> None:
    if not await utils.validate_command(ctx):
        return

    muted_role = config.Bot.muted_role

    guild_channels = await plugin.app.rest.fetch_guild_channels(ctx.guild_id)

    permissions_to_deny = (
        hikari.Permissions.SEND_MESSAGES
        | hikari.Permissions.ADD_REACTIONS
        | hikari.Permissions.CONNECT
        | hikari.Permissions.CREATE_PUBLIC_THREADS
        | hikari.Permissions.CREATE_PRIVATE_THREADS
        | hikari.Permissions.USE_APPLICATION_COMMANDS
        | hikari.Permissions.VIEW_CHANNEL
    )

    for channel in guild_channels:
        if channel.parent_id == 1234402197337280523:
            permissions_to_deny = permissions_to_deny | hikari.Permissions.VIEW_CHANNEL

        overwrite = hikari.PermissionOverwrite(
            allow=0,
            deny=permissions_to_deny,
            type=hikari.PermissionOverwriteType.ROLE,
            id=muted_role,
        )

        await plugin.app.rest.edit_permission_overwrite(
            channel=channel.id,
            target=muted_role,
            target_type=hikari.PermissionOverwriteType.ROLE,  # Specify the target type
            deny=overwrite.deny,
            allow=overwrite.allow,
            reason="Restricting permissions for muted role.",
        )

    await ctx.respond("Permissions configured.")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
