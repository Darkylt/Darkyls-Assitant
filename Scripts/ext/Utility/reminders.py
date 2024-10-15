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
import re
from datetime import datetime, timedelta

import bot_utils as utils
import database_interaction as db
import hikari
import lightbulb
import pytz

plugin = lightbulb.Plugin("Reminders", "Set reminders for yourself")

timezones = [
    "AoE",
    "SST",
    "HAST",
    "AKST",
    "PST",
    "MST",
    "CST",
    "EST",
    "AST",
    "ART",
    "GST",
    "AZOT",
    "GMT",
    "CET",
    "EET",
    "MSK",
    "GST",
    "PKT",
    "BST",
    "ICT",
    "CST",
    "JST",
    "AEST",
    "SBT",
    "NZST",
]

time_formats = {
    r"(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?": "relative",  # e.g., "1d 2h 15m"
    r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4}) (\d{1,2}):(\d{2})": "absolute_24h",  # e.g., "24.07.2024 13:07"
    r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4}) (\d{1,2}):(\d{2}) (AM|PM)": "absolute_12h",  # e.g., "24.07.2024 01:07 PM"
}


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("time", "e.g. 1d 2h 15m or 24.07.2024 13:07", str, required=True)
@lightbulb.option("message", "Set a message for yourself", str, required=True)
@lightbulb.option(
    "timezone",
    "Select your timezone",
    str,
    required=False,
    default="UTC",
    choices=timezones,
)
@lightbulb.option("dm", "Should the reminder be sent to your DMs?", bool, required=True)
@lightbulb.command(
    "remind",
    "Set reminders for yourself",
    pass_options=True,
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_reminder_command(
    ctx: lightbulb.SlashContext, time: str, message: str, timezone: str, dm: bool
) -> None:
    if not await utils.validate_command(ctx):
        return

    id = await utils.generate_id()

    now = datetime.now(pytz.timezone("UTC"))
    reminder_time = None

    # Try to match the time input with the given formats
    for pattern, fmt in time_formats.items():
        match = re.match(pattern, time)
        if match:
            if fmt == "relative":
                days, hours, minutes = match.groups(default="0")
                reminder_time = now + timedelta(
                    days=int(days), hours=int(hours), minutes=int(minutes)
                )
            elif fmt == "absolute_24h":
                day, month, year, hour, minute = match.groups()
                if len(year) == 2:
                    year = (
                        "20" + year
                    )  # Assuming 21st century for two-digit years in case this stupid code is relevant in 1000 years
                reminder_time = datetime(
                    int(year), int(month), int(day), int(hour), int(minute)
                )
            elif fmt == "absolute_12h":
                day, month, year, hour, minute, period = match.groups()
                if len(year) == 2:
                    year = (
                        "20" + year
                    )  # Assuming 21st century for two-digit years in case this stupid code is relevant in 1000 years
                hour = int(hour)
                if period == "PM" and hour != 12:
                    hour += 12
                elif period == "AM" and hour == 12:
                    hour = 0
                reminder_time = datetime(
                    int(year), int(month), int(day), hour, int(minute)
                )

            # Localize or convert time based on timezone
            if reminder_time:
                user_timezone = pytz.timezone(timezone)
                if reminder_time.tzinfo is None:
                    # If the datetime object is naive, localize it
                    reminder_time = user_timezone.localize(reminder_time)
                else:
                    # If the datetime object is already aware, convert it to user timezone
                    reminder_time = reminder_time.astimezone(user_timezone)

                # Convert to UTC
                reminder_time = reminder_time.astimezone(pytz.utc)
                reminder_time_iso = reminder_time.isoformat()
                break

    if not reminder_time:
        await ctx.respond(
            "Invalid time format. Please use one of the following formats: `1d 2h 15m`, `24.07.2024 13:07`, or `24.07.2024 01:07 PM`."
        )
        return

    delay = (reminder_time - now).total_seconds()
    if delay <= 0:
        await ctx.respond(
            "The specified time is in the past. Please provide a future time."
        )
        return

    db.Reminders.create_entry(
        id=id,
        user_id=ctx.author.id,
        reminder_time=reminder_time_iso,
        message=message,
        channel_id=ctx.channel_id,
        user_timezone=timezone,
        dm=dm,
    )

    # await schedule_reminder(ctx, delay, message)
    await ctx.respond(
        f"Reminder set for {utils.format_dt(reminder_time, 'f')}: '{message}'"
    )


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command(
    "list_reminders",
    "Shows your current set reminders",
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def list_reminders_command(ctx: lightbulb.SlashContext) -> None:
    if not await utils.validate_command(ctx):
        return

    reminders = db.Reminders.read_reminders(ctx.author.id, active=True)

    if reminders == []:
        await ctx.respond("No active reminders found.")
        return
    elif reminders is None:
        await ctx.respond("An error occurred.")
        return

    message = ""

    for reminder in reminders:
        formatted_time = utils.iso_8601_to_discord_timestamp(reminder["reminder_time"])
        message += f"Reminder: '{reminder['message']}' for {formatted_time} *({reminder['id']})*\n"

    embed = hikari.Embed(title="Active Reminders", description=message, color="#60b3e0")

    await ctx.respond(embed)


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "id", "The ID of the reminder. (Found in /list_reminders)", str, required=True
)
@lightbulb.command(
    "cancel_reminder",
    "Cancel a reminder",
    auto_defer=True,
    ephemeral=True,
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def cancel_reminder_command(ctx: lightbulb.SlashContext, id: str) -> None:
    if not await utils.validate_command(ctx):
        return

    result = db.Reminders.cancel_reminder(id)

    if result:
        await ctx.respond("Successfully deleted.")
    else:
        await ctx.respond("Couldn't delete your reminder. Double check the id.")


async def check_reminders():
    while True:
        try:
            now_utc = datetime.utcnow()
            # now_utc_iso = now_utc.isoformat()

            reminders = db.Reminders.read_reminders(active=True)

            for reminder in reminders:
                reminder_time_utc = datetime.fromisoformat(reminder["reminder_time"])

                # Convert reminder_time from UTC to user’s timezone
                user_timezone_str = reminder["timezone"]
                try:
                    user_timezone = pytz.timezone(user_timezone_str)
                except pytz.UnknownTimeZoneError:
                    # Handle unknown timezone error
                    continue

                reminder_time_user_timezone = reminder_time_utc.replace(
                    tzinfo=pytz.utc
                ).astimezone(user_timezone)
                now_user_timezone = now_utc.replace(tzinfo=pytz.utc).astimezone(
                    user_timezone
                )

                if reminder_time_user_timezone <= now_user_timezone:
                    await execute_reminder(reminder)

                    # Update reminder status to completed
                    db.Reminders.complete_reminder(reminder["id"])

            await asyncio.sleep(15)
        except Exception as e:
            from bot import logger

            logger.error(f"Error during check_reminders: {e}")


async def execute_reminder(reminder):
    dm = bool(reminder["dm"])

    color = "#60b3e0"

    user = await plugin.app.rest.fetch_user(reminder["user_id"])

    if dm:
        dm = await user.fetch_dm_channel()

        embed = hikari.Embed(
            title="🔔 Reminder", description=reminder["message"], color=color
        )

        embed.set_footer(reminder["id"])

        await dm.send(embed=embed)
    else:
        embed = hikari.Embed(
            title="🔔 Reminder",
            description=reminder["message"],
            color=color,
        )

        embed.set_footer(reminder["id"])

        await plugin.app.rest.create_message(
            reminder["channel_id"],
            content=f"Reminder for {user.mention}.",
            embed=embed,
            user_mentions=True,
        )


async def wait_until_initialized():
    """
    Wait until the bot is fully initialized and bot.application.app exists.
    """
    while not (
        hasattr(plugin.bot, "application")
        and getattr(plugin.bot.application, "app", None)
    ):
        await asyncio.sleep(1)


@plugin.listener(hikari.StartedEvent)
async def on_startup(event: hikari.StartedEvent):
    await wait_until_initialized()

    asyncio.create_task(check_reminders())


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
