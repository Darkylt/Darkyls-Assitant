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
from collections import deque
from datetime import datetime, timedelta

import config_reader as config
import hikari
import lightbulb
import member_managment
import vars
from Verification.captcha_enabling import update_captcha_status

plugin = lightbulb.Plugin("welcome", "Handles joining")

# Raid detection configuration
raid_threshold = (
    config.AutoMod.Raids.member_threshold
)  # Number of members joining within the time frame to be considered a raid
time_frame = timedelta(
    seconds=config.AutoMod.Raids.time_frame
)  # Time frame in which the number of joins are counted
join_times = deque()  # Stores the join times of members


@plugin.listener(hikari.MemberCreateEvent)
async def handle_join(event: hikari.MemberCreateEvent):
    """
    Gets called when a new member joins.
    It runs a helper function used for handling new joins.
    """

    try:
        if event.member.is_bot or event.member.is_system:
            return

        now = datetime.now()

        # Remove join times outside the time frame
        while join_times and now - join_times[0] > time_frame:
            join_times.popleft()

        # Add the current join time
        join_times.append(now)

        # Check for raid condition
        if len(join_times) >= raid_threshold:
            vars.raid = True

            from bot import Logging

            Logging.log_message(
                f"Raid detected! More than {raid_threshold} members joined within {time_frame} seconds."
            )

            from bot import logger

            logger.warning(
                f"Raid detected! More than {raid_threshold} members joined within {time_frame} seconds."
            )
        else:
            vars.raid = False

        await update_captcha_status()

        if not vars.raid:
            await member_managment.new_member(event.member, plugin.bot)

    except Exception as e:
        from bot import logger

        logger.error(f"Error during member join event: {e}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
