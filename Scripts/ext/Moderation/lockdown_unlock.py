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
import vars
from hikari import PermissionOverwrite, PermissionOverwriteType, Permissions

plugin = lightbulb.Plugin(
    "Unlock", "Lock down the server in case of emergency (Unlock)"
)
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))

server = config.Bot.server
# server = 1284115021152124948  # DEBUG server

backup_path = os.path.join(config.Paths.data_folder, "Server Backups")
backup_file_path = os.path.join(backup_path, f"{server}_server_backup.json")


def load_backup_channels():
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


async def apply_backup_data_channels(reconstructed_data: list):

    channel_id_map = {
        channel_data["id"]: channel_data for channel_data in reconstructed_data
    }

    for channel_data in reconstructed_data:
        try:
            channel = await plugin.app.rest.fetch_channel(channel_data["id"])
        except hikari.NotFoundError:
            channel = None

        permission_overwrites = [
            hikari.PermissionOverwrite(
                id=overwrite.id,
                type=overwrite.type,
                allow=overwrite.allow,
                deny=overwrite.deny,
            )
            for overwrite in channel_data["permission_overwrites"]
        ]

        # Check if parent_id exists and if it's valid
        category = None
        if "parent_id" in channel_data:
            parent_channel_data = channel_id_map.get(channel_data["parent_id"])
            if parent_channel_data and parent_channel_data["type"] == "GUILD_CATEGORY":
                category = parent_channel_data["id"]

        if channel:
            await plugin.app.rest.edit_channel(
                channel.id,
                name=channel_data["name"],
                permission_overwrites=permission_overwrites,
                parent_category=category,
            )
        else:
            # Create channel based on type
            if channel_data["type"] == "GUILD_TEXT":
                await plugin.app.rest.create_guild_text_channel(
                    server,
                    name=channel_data["name"],
                    permission_overwrites=permission_overwrites,
                    category=category,
                )
            elif channel_data["type"] == "GUILD_VOICE":
                await plugin.app.rest.create_guild_voice_channel(
                    server,
                    name=channel_data["name"],
                    permission_overwrites=permission_overwrites,
                    category=category,
                )
            elif channel_data["type"] == "GUILD_CATEGORY":
                await plugin.app.rest.create_guild_category(
                    server,
                    name=channel_data["name"],
                    permission_overwrites=permission_overwrites,
                )

    print("Backup data applied successfully!")


async def apply_backup_data_roles():
    with open(backup_file_path, "r") as file:
        data = json.load(file)

    # Extract the removed roles data
    removed_roles = data.get("removed_roles", {})

    for user_id, role_ids in removed_roles.items():
        for role_id in role_ids:
            try:
                await plugin.app.rest.add_role_to_member(
                    server, user_id, role_id, reason="Restoring from lockdown."
                )
            except Exception as e:
                from bot import logger

                logger.error(f"Error adding role {role_id} to user {user_id}: {e}")


async def clean_up_messages():
    try:
        with open(backup_file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file at {backup_file_path} was not found.")
        return
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the backup file.")
        return

    messages = data.get("messages", {})
    if not messages:
        print("No messages found in the backup data.")
        return

    for channel_id, message_id in messages.items():
        try:
            await plugin.app.rest.delete_message(channel_id, message_id)
        except Exception as e:
            from bot import logger

            logger.error(
                f"Error deleting message {message_id} in channel {channel_id}: {e}"
            )

    print("Message cleanup completed.")


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

    reconstructed_data = load_backup_channels()
    await apply_backup_data_channels(reconstructed_data)

    await apply_backup_data_roles()

    await clean_up_messages()

    vars.lockdown = False

    await message.edit("Restoring successful.")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
