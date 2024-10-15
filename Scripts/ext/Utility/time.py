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
import re

import config_reader as config
import hikari
import lightbulb
import pytz

plugin = lightbulb.Plugin("Time", "Time related commands")


TIMEDELTA_REGEX = re.compile(
    r"((?P<years>\d+?)Y|years)?((?P<months>\d+?)M|months)?((?P<weeks>\d+?)W|weeks)?((?P<days>\d+?)D|days)?"
    + r"((?P<hours>\d+?)h|hr|hours)?((?P<minutes>\d+?)m|min|minutes)?((?P<seconds>\d+?)s|sec|seconds)?"
)
TIME_TO_SECONDS = {
    "years": 31_536_000,
    "months": 2_628_288,
    "weeks": 604_800,
    "days": 86_400,
    "hours": 3600,
    "minutes": 60,
    "seconds": 1,
}


def str_to_timedelta(timedelta_str: str) -> datetime.timedelta | None:
    parts = TIMEDELTA_REGEX.match(timedelta_str)
    seconds = 1.0  # to not error when your try to respond immediately
    if parts is None:
        return None
    for k, v in parts.groupdict().items():
        if v is None:
            continue
        seconds += float(v) * TIME_TO_SECONDS[k]

    return datetime.timedelta(seconds=seconds)


@plugin.command
@lightbulb.option("timezone", "The timezone.", default="UTC")
@lightbulb.option("timedelta", "The timedelta.")
@lightbulb.command("time_in", "Get the time.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def cmd_time_in(ctx: lightbulb.context.SlashContext) -> None:
    timedelta = str_to_timedelta(getattr(ctx.options, "timedelta", None))
    if timedelta is None:
        await ctx.respond("Couldn't convert timedelta.")
        return
    try:
        timezone = pytz.timezone(getattr(ctx.options, "timezone", None))
    except pytz.UnknownTimeZoneError:
        await ctx.respond("Unknown timezone.")
        return
    unix_timestamp = int(
        (
            datetime.datetime.utcnow()
            + timedelta
            + timezone.utcoffset(datetime.datetime.utcnow())
        ).timestamp()
    )
    await ctx.respond(f"It will be <t:{unix_timestamp}:f>.")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
