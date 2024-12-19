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

import datetime
import json
import os

import aiohttp
import bot_utils as utils
import config_reader as config
import hikari
import lightbulb
import vars
from hikari import Permissions

plugin = lightbulb.Plugin("Lockdown", "Lock down the server in case of emergency")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))

server = config.Bot.server
# server = 1284115021152124948  # DEBUG server

# Set the critical roles that should be removed from users
roles_to_remove = [config.Bot.admin_role, config.Bot.mod_role]

backup_path = os.path.join(config.Paths.data_folder, "Server Backups")
backup_file_path = os.path.join(backup_path, f"{server}_server_backup.json")
backup_data_memory = {}


async def download_image(url, backup_file_path):
    """Helper function to download an image."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(backup_file_path, "wb") as f:
                    f.write(await response.read())
                return backup_file_path
            else:
                print(f"Failed to download image from {url}")
                return None


async def create_backup():
    global backup_data_memory

    os.makedirs(backup_path, exist_ok=True)

    guild = await plugin.app.rest.fetch_guild(server)
    guild_channels = await plugin.app.rest.fetch_guild_channels(server)

    guild_info = {
        "id": guild.id,
        "name": guild.name,
        "description": guild.description or "No description provided",
        "rules_channel_id": guild.rules_channel_id,
        "afk_channel_id": guild.afk_channel_id,
        "icon_url": guild.icon_url,
        "banner_url": guild.banner_url,
    }

    icon_backup_file_path = None
    banner_backup_file_path = None

    if guild.icon_url:
        icon_backup_file_path = os.path.join(backup_path, f"{server}_icon.png")
        icon_backup_file_path = await download_image(
            guild.icon_url, icon_backup_file_path
        )

    if guild.banner_url:
        banner_backup_file_path = os.path.join(backup_path, f"{server}_banner.png")
        banner_backup_file_path = await download_image(
            guild.banner_url, banner_backup_file_path
        )

    backup_data = []

    for channel in guild_channels:
        serialized_overwrites = [
            {
                "id": overwrite.id,
                "type": overwrite.type.name,  # Serialize the enum as its name
                "allow": overwrite.allow.value,  # Serialize permissions as integers
                "deny": overwrite.deny.value,
            }
            for overwrite in channel.permission_overwrites.values()
        ]

        backup_data.append(
            {
                "id": channel.id,
                "name": channel.name,
                "parent_id": channel.parent_id,
                "type": channel.type.name,  # Serialize channel type as name
                "permission_overwrites": serialized_overwrites,
            }
        )

    backup_data_memory = {
        "guild": guild_info,
        "icon_backup_file_path": icon_backup_file_path,
        "banner_backup_file_path": banner_backup_file_path,
        "channels": backup_data,
    }

    print("Backup data stored in memory successfully!")


async def lockdown_channels(reason):
    global backup_data_memory

    guild_channels = await plugin.app.rest.fetch_guild_channels(server)

    deny_perms_text = (
        Permissions.SEND_MESSAGES
        | Permissions.CREATE_PRIVATE_THREADS
        | Permissions.CREATE_PUBLIC_THREADS
        | Permissions.ADD_REACTIONS
    )

    deny_perms_voice = (
        Permissions.CONNECT
        | Permissions.SEND_MESSAGES
        | Permissions.ADD_REACTIONS
        | Permissions.READ_MESSAGE_HISTORY
    )

    embed = hikari.Embed(
        title="🚨 Server Lockdown Activated 🚨",
        description="The Server is currently under lockdown.\nThis is to ensure the safety and security of our community. This action has been taken due to suspicious activity or a potential threat, such as a server raid or unauthorized actions by a server member. All channels are now read-only, and permissions have been restricted for all roles.",
        colour=0xFF0000,
        timestamp=datetime.datetime.now().astimezone(),
    )
    embed.set_author(
        name="Darkyl's Assistant",
        url="https://darkylmusic.com/discord-bot/",
        icon="https://darkylmusic.com/assets/images/discord/pfp.png",
    )
    if reason:
        embed.add_field(
            name="Why is this happening?",
            value=reason,
            inline=False,
        )
    else:
        embed.add_field(
            name="Why is this happening?",
            value="The lockdown is a precautionary measure to prevent further disruptions and to ensure that the server remains a safe space for everyone.",
            inline=False,
        )
    embed.add_field(
        name="What does this mean for you?",
        value="During the lockdown, you will be unable to send messages, react to messages, or join voice channels. Please be patient while we address the situation. Relax and grab some tea☕.",
        inline=False,
    )
    embed.add_field(
        name="Next Steps:",
        value="Our moderation team is investigating and resolving the issue as quickly as possible.\nWe will provide updates in the announcements channel or via direct messages from the moderation team.",
        inline=False,
    )
    embed.set_footer(
        text="Thank you for your patience and understanding during this time. We aim to restore full functionality as soon as possible."
    )

    lockdown_messages = {}

    for channel in guild_channels:
        if channel.type.name == "GUILD_TEXT" or channel.type.name == "GUILD_VOICE":
            for overwrite in channel.permission_overwrites.values():
                role_id = overwrite.id
                # Skip if the overwrite is for @everyone
                if role_id == server:
                    continue

                existing_allow = overwrite.allow if overwrite else Permissions.NONE
                existing_deny = overwrite.deny if overwrite else Permissions.NONE

                # Determine the new deny permissions based on channel type
                if channel.type.name == "GUILD_TEXT":
                    new_deny = existing_deny | deny_perms_text
                elif channel.type.name == "GUILD_VOICE":
                    new_deny = existing_deny | deny_perms_voice

                # Keep the 'allow' permissions that do not contradict the new denies
                new_allow = existing_allow & ~new_deny

                # Update permissions for this role
                await plugin.app.rest.edit_permission_overwrite(
                    channel=channel.id,
                    target=role_id,
                    target_type=hikari.PermissionOverwriteType.ROLE,
                    allow=new_allow,
                    deny=new_deny,
                    reason="Lockdown.",
                )

            # Apply lockdown to the @everyone role (server role)
            existing_overwrite = next(
                (
                    po
                    for po in channel.permission_overwrites.values()
                    if po.id == server
                ),
                None,
            )
            existing_allow = (
                existing_overwrite.allow if existing_overwrite else Permissions.NONE
            )
            existing_deny = (
                existing_overwrite.deny if existing_overwrite else Permissions.NONE
            )

            if channel.type.name == "GUILD_TEXT":
                new_deny = existing_deny | deny_perms_text
            elif channel.type.name == "GUILD_VOICE":
                new_deny = existing_deny | deny_perms_voice

            # Keep the 'allow' permissions that do not contradict the new denies
            new_allow = existing_allow & ~new_deny

            # Update permissions for the @everyone role
            await plugin.app.rest.edit_permission_overwrite(
                channel=channel.id,
                target=server,  # @everyone
                target_type=hikari.PermissionOverwriteType.ROLE,
                allow=new_allow,
                deny=new_deny,
                reason="Lockdown.",
            )

            if channel.type.name == "GUILD_TEXT":
                message = await plugin.app.rest.create_message(channel.id, embed=embed)
                lockdown_messages[str(channel.id)] = message.id

    if "messages" not in backup_data_memory:
        backup_data_memory["messages"] = {}

    backup_data_memory["messages"].update(lockdown_messages)


async def lockdown_members():
    global backup_data_memory

    role_ids = roles_to_remove

    members = await plugin.app.rest.fetch_members(server)

    if "removed_roles" not in backup_data_memory:
        backup_data_memory["removed_roles"] = {}

    for member in members:
        try:
            current_roles = await member.fetch_roles()

            # Extract role IDs from the Role objects
            current_role_ids = {role.id for role in current_roles}

            roles_to_remove = current_role_ids.intersection(set(role_ids))

            for role_id in roles_to_remove:
                await member.remove_role(role_id, reason="Lockdown.")

                if str(member.id) not in backup_data_memory["removed_roles"]:
                    backup_data_memory["removed_roles"][str(member.id)] = []
                backup_data_memory["removed_roles"][str(member.id)].append(role_id)

        except Exception as e:
            from bot import logger

            logger.error(f"Error removing roles from member {member.id}: {e}")


async def save_backup_to_file():
    """Function to write the global backup data to a file."""
    global backup_data_memory

    if not backup_data_memory:
        print("No backup data found in memory. Nothing to save.")
        return

    try:
        with open(backup_file_path, "w") as file:
            json.dump(backup_data_memory, file, indent=4)
        print(f"Backup data saved to file: {backup_file_path}")
    except PermissionError as e:
        print(f"Failed to save backup file due to permission error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving the backup: {e}")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.option("reason", "Why is this happening?", type=str, required=False)
@lightbulb.command(
    "lockdown", "Lock the server.", ephemeral=True, auto_defer=True, pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def lockdown_command(ctx: lightbulb.SlashContext, reason: str):
    if not await utils.validate_command(ctx):
        return

    if ctx.author.id != config.Bot.owner_id:
        await ctx.respond("Only Darkyl is allowed to do this.")
        return

    message = await ctx.respond("Creating backup...")

    await create_backup()

    await message.edit("Going into lockdown...")

    await lockdown_channels(reason)

    await lockdown_members()

    await save_backup_to_file()

    vars.lockdown = True

    await message.edit("Server locked.")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
