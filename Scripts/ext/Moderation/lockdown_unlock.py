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

import json
import os

import aiohttp
import bot_utils as utils
import config_reader as config
import hikari
import lightbulb
from hikari import PermissionOverwrite, PermissionOverwriteType, Permissions

plugin = lightbulb.Plugin(
    "Unlock", "Lock down the server in case of emergency (Unlock)"
)
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))

# server = config.Bot.server
server = 1284115021152124948  # DEBUG server

backup_path = os.path.join(config.Paths.data_folder, "Server Backups")
backup_file_path = os.path.join(backup_path, f"{server}_server_backup.json")


def load_backup():
    with open(backup_file_path, "r") as file:
        backup_data = json.load(file)

    reconstructed_data = []

    for channel in backup_data["channels"]:
        # Reconstruct permission overwrites with explicit type mapping
        reconstructed_overwrites = []
        for overwrite in channel["permission_overwrites"]:
            if overwrite["type"] == "ROLE":
                permission_type = PermissionOverwriteType.ROLE
            elif overwrite["type"] == "MEMBER":
                permission_type = PermissionOverwriteType.MEMBER
            else:
                raise ValueError(
                    f"Unexpected permission overwrite type: {overwrite['type']}"
                )

            reconstructed_overwrites.append(
                PermissionOverwrite(
                    id=overwrite["id"],
                    type=permission_type,
                    allow=Permissions(overwrite["allow"]),
                    deny=Permissions(overwrite["deny"]),
                )
            )

        # Append the reconstructed channel data
        reconstructed_data.append(
            {
                "id": channel["id"],
                "name": channel["name"],
                "type": channel["type"],
                "parent_id": channel["parent_id"],
                "permission_overwrites": reconstructed_overwrites,
            }
        )

    print("Backup loaded successfully!")
    return reconstructed_data


async def apply_backup_data(reconstructed_data: list):

    for channel_data in reconstructed_data:
        # Fetch existing channel if it exists
        try:
            channel = await plugin.app.rest.fetch_channel(channel_data["id"])
        except hikari.NotFoundError:
            channel = None

        # Handle permissions for overwrites
        permission_overwrites = [
            hikari.PermissionOverwrite(
                id=overwrite.id,
                type=overwrite.type,
                allow=overwrite.allow,
                deny=overwrite.deny,
            )
            for overwrite in channel_data["permission_overwrites"]
        ]

        if channel:
            # Update existing channel
            await plugin.app.rest.edit_channel(
                channel.id,
                name=channel_data["name"],
                permission_overwrites=permission_overwrites,
            )
        else:
            # Create channel based on type
            if channel_data["type"] == "GUILD_TEXT":
                await plugin.app.rest.create_guild_text_channel(
                    server,
                    name=channel_data["name"],
                    permission_overwrites=permission_overwrites,
                )
            elif channel_data["type"] == "GUILD_VOICE":
                await plugin.app.rest.create_guild_voice_channel(
                    server,
                    name=channel_data["name"],
                    permission_overwrites=permission_overwrites,
                )
            elif channel_data["type"] == "GUILD_CATEGORY":
                await plugin.app.rest.create_guild_category(
                    server,
                    name=channel_data["name"],
                    permission_overwrites=permission_overwrites,
                )

    print("Backup data applied successfully!")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.command("unlock", "Remove a lockdown", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def lockdown_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return

    if ctx.author.id != config.Bot.owner_id:
        await ctx.respond("Only Darkyl is allowed to do this.")
        return

    message = await ctx.respond("Restoring...")

    reconstructed_data = load_backup()
    await apply_backup_data(reconstructed_data)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
