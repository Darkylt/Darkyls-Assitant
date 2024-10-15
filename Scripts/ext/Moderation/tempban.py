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
import json
import os
import re
from datetime import datetime, timedelta, timezone

import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("TempBan", "Bans a user temporarily")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))

BAN_DATA_FILE = os.path.join(config.Paths.data_folder, "Database", "bans.json")


def load_ban_data():
    if os.path.exists(BAN_DATA_FILE):
        with open(BAN_DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_ban_data(data):
    with open(BAN_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


async def load_active_bans():
    ban_data = load_ban_data()
    current_time = datetime.now(timezone.utc).timestamp()
    tasks = []
    for guild_id, bans in ban_data.items():
        for user_id, ban_info in bans.items():
            unban_time = ban_info["unban_time"]
            if unban_time > current_time:
                duration = unban_time - current_time
                tasks.append(schedule_unban(int(guild_id), int(user_id), duration))
            else:
                try:
                    await plugin.bot.application.app.rest.unban_user(
                        guild=int(guild_id), user=int(user_id)
                    )
                except hikari.errors.ForbiddenError:
                    pass
                except Exception as e:
                    from bot import logger

                    logger.error(f"An error occurred while unbanning the user: {e}")
    await asyncio.gather(*tasks)


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option(
    "user", "The user that should be banned.", required=True, type=hikari.Member
)
@lightbulb.option("reason", "Why is the user being banned?", required=True, type=str)
@lightbulb.option(
    "delete_messages",
    "How far back should messages be deleted?",
    required=False,
    choices=[
        "1 Hour",
        "5 Hours",
        "12 Hours",
        "1 Day",
        "2 Days",
        "3 Days",
        "4 Days",
        "5 Days",
        "6 Days",
        "7 Days",
    ],
    default=None,
)
@lightbulb.option(
    "duration",
    "How long should the ban last? (e.g., 1y2d3h29m2s)",
    required=True,
    type=str,
)
@lightbulb.command("tempban", "Ban a user temporarily", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def tempban_command(
    ctx: lightbulb.SlashContext,
    user: hikari.Member,
    reason: str,
    delete_messages,
    duration: str,
):
    """
    A command to temporarily ban a user.

    It processes the provided info and then bans the user.

    Processing:
        Retreiving provided information
        Fetching the user
        Mapping of delete messages options to time durations
        Banning the user
        Responding and logging
        Scheduling the unban
    """

    if not await utils.validate_command(ctx):
        return

    try:
        time_durations = {
            "1 Hour": 3600,
            "5 Hours": 18000,
            "12 Hours": 43200,
            "1 Day": 86400,
            "2 Days": 172800,
            "3 Days": 259200,
            "4 Days": 345600,
            "5 Days": 432000,
            "6 Days": 518400,
            "7 Days": 604800,
        }

        message_timer = time_durations.get(delete_messages, 0)
        ban_duration = parse_duration(duration)

        if ban_duration is None:
            await ctx.respond(
                "Invalid duration format. Please use a format like '1y2d3h29m2s'.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        try:
            await plugin.bot.application.app.rest.ban_user(
                guild=ctx.guild_id,
                user=user.id,
                reason=reason,
                delete_message_seconds=message_timer,
            )
        except hikari.errors.ForbiddenError:
            await ctx.respond(
                "I do not have permission to ban the user.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        await ctx.respond(
            "User has been banned successfully.", flags=hikari.MessageFlag.EPHEMERAL
        )

        # Save ban data
        ban_data = load_ban_data()
        if str(ctx.guild_id) not in ban_data:
            ban_data[str(ctx.guild_id)] = {}
        ban_data[str(ctx.guild_id)][str(user.id)] = {
            "unban_time": (
                datetime.utcnow() + timedelta(seconds=ban_duration)
            ).timestamp()
        }
        save_ban_data(ban_data)

        # Schedule the unban
        await schedule_unban(ctx.guild_id, user.id, ban_duration)

    except KeyError:
        await ctx.respond(
            "Invalid option provided.", flags=hikari.MessageFlag.EPHEMERAL
        )
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during the /tempban command: {e}")
        await ctx.respond(
            "An error occurred while processing the command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def parse_duration(duration: str) -> int:
    """
    Parses a duration string (e.g., '1y2d3h29m2s') and returns the total duration in seconds.

    Args:
        duration (str): The duration string to parse.

    Returns:
        int: The total duration in seconds.
    """
    time_units = {
        "y": 31536000,  # years
        "d": 86400,  # days
        "h": 3600,  # hours
        "m": 60,  # minutes
        "s": 1,  # seconds
    }

    total_seconds = 0
    matches = re.findall(r"(\d+)([ydhms])", duration)
    for value, unit in matches:
        if unit in time_units:
            total_seconds += int(value) * time_units[unit]
        else:
            return None

    return total_seconds if total_seconds > 0 else None


async def schedule_unban(guild_id, user_id, duration):
    await asyncio.sleep(duration)
    try:
        await plugin.bot.application.app.rest.unban_user(guild=guild_id, user=user_id)
        # Remove the ban entry from the data file
        ban_data = load_ban_data()
        if str(guild_id) in ban_data and str(user_id) in ban_data[str(guild_id)]:
            del ban_data[str(guild_id)][str(user_id)]
            if not ban_data[str(guild_id)]:
                del ban_data[str(guild_id)]
            save_ban_data(ban_data)
    except hikari.errors.ForbiddenError:
        # Handle the case where the bot does not have permission to unban the user
        pass
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while unbanning the user: {e}")


@plugin.listener(hikari.StartedEvent)
async def on_started(event):
    ban_data = load_ban_data()
    current_time = datetime.now(timezone.utc).timestamp()
    tasks = []

    for guild_id, bans in ban_data.items():
        for user_id, ban_info in bans.items():
            unban_time = ban_info["unban_time"]
            if unban_time > current_time:
                duration = unban_time - current_time
                tasks.append(schedule_unban(int(guild_id), int(user_id), duration))
            else:
                try:
                    await plugin.bot.application.app.rest.unban_user(
                        guild=int(guild_id), user=int(user_id)
                    )
                    # Remove the ban entry from the data file
                    if (
                        str(guild_id) in ban_data
                        and str(user_id) in ban_data[str(guild_id)]
                    ):
                        del ban_data[str(guild_id)][str(user_id)]
                        if not ban_data[str(guild_id)]:
                            del ban_data[str(guild_id)]
                        save_ban_data(ban_data)
                except hikari.errors.ForbiddenError:
                    pass
                except Exception as e:
                    from bot import logger

                    logger.error(f"An error occurred while unbanning the user: {e}")

    await asyncio.gather(*tasks)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
