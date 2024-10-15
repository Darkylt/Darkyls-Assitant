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
from datetime import datetime, timezone

import bot_utils as utils
import buttons
import config_reader as config
import database_interaction
import dateutil
import dateutil.parser
import hikari
import hikari.errors
import image_manager
import lightbulb

plugin = lightbulb.Plugin("ModMenu", "A control panel for a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option("user", "The target", type=hikari.User)
@lightbulb.command(
    "mod_menu",
    "Your control panel for a user",
    pass_options=True,
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def mod_menu_command(ctx: lightbulb.SlashContext, user: hikari.User):
    if not await utils.validate_command(ctx):
        return

    # Fetch user to get extra info available
    user = await ctx.app.rest.fetch_member(ctx.guild_id, user.id)

    banner = await image_manager.download_image(user.banner_url, user.id)

    if banner is None:
        color = utils.get_color(user)
    else:
        if banner.endswith("gif"):
            banner = await image_manager.gif_to_png(banner)

        avg_red, avg_green, avg_blue = image_manager.average_color(str(banner))
        color = hikari.Color.from_rgb(int(avg_red), int(avg_green), int(avg_blue))

    embed = hikari.Embed(
        title=f"**Mod Menu:** {user.username}",
        description=f"This is a mod menu for this user. Here you can access most important information and quickly perform actions!",
        color=color,
    )
    user_avatar = user.avatar_url
    if user_avatar is not None:
        embed.set_thumbnail(user_avatar)

    embed.add_field("**• Nickname:**", value=f"{user.display_name or '-'}")
    embed.add_field("**• User ID:**", value=f"{user.id}")
    if user.is_bot:
        embed.add_field("**• Bot:**", value=f"'The user is a bot.'")
    embed.add_field(
        "**• Account create date:**",
        value=f"{utils.format_dt(user.created_at)} ({utils.format_dt(user.created_at, style='R')})",
    )
    embed.add_field(
        "**• Joined at:**",
        value=f"{utils.format_dt(user.joined_at)} ({utils.format_dt(user.joined_at, style='R')})",
    )

    embed.add_field("**• Badges:**", value="   ".join(utils.get_badges(user)) or "`-`")
    embed.add_field(
        "**• Timed out:**",
        value=f"Until: {utils.format_dt(user.communication_disabled_until()) if user.communication_disabled_until() is not None else '-'}",
    )

    stats = database_interaction.Users.get_user_entry(user_id=user.id)

    if stats:
        (id, msg_count, xp, level, cmds_used, reported, been_reported, nsfw_opt_out) = (
            stats
        )

        embed.add_field("**• Messages Sent:**", value=msg_count)
        embed.add_field("**• Commands Used:**", value=cmds_used)
        embed.add_field("**• XP:**", value=xp)
        embed.add_field("**• Level:**", value=level)
        embed.add_field("**• Opted Out of NSFW:**", value=bool(nsfw_opt_out))

    roles_list = [
        role.mention
        for role in utils.sort_roles(user.get_roles())
        if role.id != ctx.guild_id
    ]
    roles = ", ".join(roles_list) if roles_list else "`-`"
    embed.add_field("**• Roles:**", value=f"{roles}")

    warnings_file = os.path.join(config.Paths.data_folder, "Database", "warnings.json")

    if os.path.exists(warnings_file):
        with open(warnings_file, "r") as file:
            warnings_data = json.load(file)
            user_warnings = warnings_data.get(str(user.id), [])
            if user_warnings:
                warnings_text = "\n\n".join(
                    [f"`{warning}`" for warning in user_warnings]
                )
                embed.add_field("**• Warnings:**", value=warnings_text)
            else:
                embed.add_field("**• Warnings:**", value="No warnings")
    else:
        embed.add_field("**• Warnings:**", value="Couldn't find the warnings database.")

    if stats:
        embed.add_field("**• Reported user:**", value=reported)
        embed.add_field("**• Been reported:**", value=been_reported)

    reports_file = os.path.join(config.Paths.data_folder, "Database", "reports.json")

    if os.path.exists(reports_file):
        with open(reports_file, "r") as file:
            reports_data = json.load(file)
            user_reports = reports_data.get(str(user.id), {})
            if user_reports:
                reasons = user_reports.get("reasons", {})
                if reasons:
                    reasons_text = ""
                    for reason, details in reasons.items():
                        reporter = details.get("reporter")
                        if reporter.isdigit():
                            reporter_user = await ctx.app.rest.fetch_user(reporter)
                            reporter_mention = f"{reporter_user.mention}"
                        else:
                            reporter_mention = reporter
                        reasons_text += f"`{reason}`\nBy {reporter_mention}\n\n"
                    embed.add_field(
                        "**• Reports:**",
                        value=reasons_text.strip() or "No reports for this user",
                    )
                else:
                    embed.add_field("**• Reports:**", value="No reports for this user")
            else:
                embed.add_field("**• Reports:**", value="No reports for this user")
    else:
        embed.add_field("**• Reports:**", value="Couldn't find the reports database.")

    if banner is not None:
        embed.set_image(user.banner_url)

    embeds = [embed]

    all_messages = database_interaction.Messages.get_messages_by_author(user.id)

    if all_messages is not None:

        msg_info_embed = hikari.Embed(
            title="Messages",
            description="The following embeds are the last 5 messages sent by the user.\n\nIf the messages have been edited to obstruct vital information you can use `/message_history` to see older versions of the message. The message ID should be at the very bottom of the embed. Note: Messages can only be picked up while the bot is running and if the bot can see them. Some information might be incomplete.",
            color="ff0000",
        )

        embeds.append(msg_info_embed)

        # Create a dictionary to keep track of the message with the highest edited count for each msg_id
        message_dict = {}

        for message in all_messages:
            msg_id = message["msg_id"]
            if (
                msg_id not in message_dict
                or message["edited"] > message_dict[msg_id]["edited"]
            ):
                message_dict[msg_id] = message

        # Convert dictionary values back to a list
        filtered_messages = list(message_dict.values())

        # Sort filtered_messages by the 'created_at' field in ascending order
        filtered_messages.sort(key=lambda m: datetime.fromisoformat(m["created_at"]))

        # Get the bottom 10 messages (or fewer if there aren't that many)
        bottom_messages = filtered_messages[-5:]

        # Create and send embeds for each of the bottom messages
        for entry in bottom_messages:
            formatted_date = utils.iso_8601_to_discord_timestamp(entry["created_at"])

            if entry["edited"] > 0:
                title = "Message (Edited)"
            else:
                title = "Message"

            title = "Message"

            content = str(entry["content"]).replace("`", "'")

            msg_embed = hikari.Embed(
                title=title,
                description=f"```{content}```",
                color=0x0099FF,
            )

            channel = await plugin.app.rest.fetch_channel(entry["channel_id"])

            msg_embed.add_field(
                name="Channel:", value=f"{channel.mention}", inline=False
            )
            msg_embed.set_author(
                name=user.username, icon=hikari.files.URL(str(user.avatar_url))
            )
            msg_embed.add_field(name="Created at:", value=formatted_date, inline=False)
            msg_embed.add_field(
                name="Attachments:", value=str(bool(entry["attachments"]))
            )
            msg_embed.set_footer(str(entry["msg_id"]))

            embeds.append(msg_embed)

    commands = database_interaction.Commands.get_commands_by_user(user.id)

    if commands is not None:
        commands.sort(key=lambda m: datetime.fromisoformat(m["used_at"]))

        bottom_commands = commands[-5:]

        cmd_str = ""

        for cmd_entry in bottom_commands:
            cmd_str += f"/{cmd_entry['cmd_name']}\n"

        cmd_embed = hikari.Embed(title="Latest commands", description=cmd_str)

        embeds.append(cmd_embed)

    view = buttons.ModMenu()

    await ctx.respond(f"{user.mention}", embeds=embeds, components=view)

    if banner is not None:
        os.remove(banner)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
