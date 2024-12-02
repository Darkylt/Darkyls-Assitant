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
import random

import bot_utils as utils
import config_reader as config
import database_interaction
import hikari
import hikari.errors
import image_manager


async def new_member(member: hikari.Member, bot):
    """
    Handles a new server member.
    Sends the welcome card.

    Processing:
        Downloads the avatar of the new user
        Converts to png if it is a gif
        Resizes the image to a set size
        Generates the card
        Sends the welcome card and message
    """
    pfp_link = member.avatar_url

    pfp_path = await image_manager.download_image(image_url=pfp_link, id=member.id)

    if pfp_path is None:
        return None

    if str(pfp_path).endswith("gif"):
        pfp_path = await image_manager.gif_to_png(pfp_path)

    await image_manager.resize_image(pfp_path)

    await image_manager.make_card(pfp_path)

    file = hikari.File(pfp_path)

    await bot.application.app.rest.create_message(
        config.Join.channel,
        f"<@{member.id}>, welcome to **Darkyl's Discord**.",
        attachment=file,
        user_mentions=True,
    )

    if not await image_manager.delete(pfp_path):
        return


async def warn_member(user_id: int, reason: str) -> bool:
    """
    A script that handles warning a member.

    Args:
        user_id (int): The ID of the user that should be warned
        reason (str): The reason of the warn
    Returns:
        True: If the warn was a success
        False: If something went wrong (usually missing permissions)
    """
    try:
        database_path = os.path.join(
            config.Paths.data_folder, "Database", "warnings.json"
        )
        data = {}

        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                data = json.load(file)

        user_id = str(user_id)

        if user_id in data:
            data[user_id].append(reason)
        else:
            data[user_id] = [reason]

        with open(database_path, "w") as file:
            json.dump(data, file, indent=4)

        warnings_count = len(data.get(user_id, []))

        if (
            (config.AutoMod.kick_threshold - 2)
            < warnings_count
            < (config.AutoMod.kick_threshold + 1)
        ):
            try:
                await hikari.Application.app.rest.kick_user(
                    guild=config.Bot.server,
                    user=int(user_id),
                    reason="Too many warnings",
                )
            except hikari.errors.ForbiddenError:
                return False
        elif warnings_count >= (config.AutoMod.ban_threshold - 1):
            try:
                await hikari.Application.app.rest.ban_user(
                    guild=config.Bot.server,
                    user=int(user_id),
                    delete_message_seconds=0,
                    reason="Too many warnings from moderators.",
                )
            except hikari.errors.ForbiddenError:
                return False
    except Exception as e:
        from bot import logger

        logger.error(f"Error during warn_member: {e}")
        return False

    return True


async def skibidy_toilet_enysmo(bot):
    """
    Makes sure Enysmo is being put in his place
    """
    await asyncio.sleep(10)

    enysmo = await bot.application.app.rest.fetch_member(
        config.Bot.server, user=175892694952837120
    )
    enysmo.add_role(config.ReactionRoles.skibidy_toilet_role)


async def update_user_stats(
    user_id: int, msg: bool, cmd: bool, rep: bool, extra_xp: int = 0
):
    """
    Updates the user stats database

    Args:
        user_id (int): The User ID of the account that should be added
        msg (bool): If the event was triggered by a message
        cmd (bool): If the event was triggered by a command
        rep (bool): If the event was triggered by a report
        extra_xp (int): If the user should be rewarded extra XP
    """

    try:
        if database_interaction.Users.update_user_entry(
            user_id=int(user_id),
            increment=True,
            msg_count=int(msg),
            cmds_used=int(cmd),
            reported=int(rep),
        ):
            try:
                await update_xp(user_id=int(user_id), report=rep, add_xp=extra_xp)
            except Exception as e:
                from bot import logger

                logger.error(f"An error occurred while trying to update_xp: {e}")
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred in update_user_stats: {e}")


async def get_level_from_xp(xp):
    try:
        # calculate level from xp
        xp = int(xp)
        level = 0
        for required_xp in config.Level.leve_from_xp_mapping.values():
            if xp >= required_xp:
                level += 1

            else:
                break
        return level
    except Exception as e:
        from bot import logger

        logger.error(f"Following error occurred during get_level_from_xp(): {e}")
        return None


async def level_increase(level, user_id, bot):
    try:
        embed = hikari.Embed(
            title="Level increase", description=f"<@{user_id}> is now level {level}!"
        )
        embed.set_thumbnail(os.path.join(config.Paths.assets_folder, "pfp.png"))
        from bot import bot

        await bot.application.app.rest.create_message(
            channel=config.Bot.level_update_channel, embed=embed
        )
    except Exception as e:
        from bot import logger

        logger.error(f"Error during level increase message (level_increase()): {e}")


async def update_xp(user_id: int, report: bool, add_xp: int = 0) -> bool:
    """
    A function for updating the XP.

    Args:
        user_id (int). The ID of the user
        report (bool): If the cause for the xp increase is a report
        add_xp (int): Add additional XP
    """

    user_data = database_interaction.Users.get_user_entry(user_id=user_id)

    if user_data:
        (
            id,
            msg_count,
            current_xp,
            last_level,
            cmds_used,
            reported,
            been_reported,
            nsfw_opt_out,
        ) = user_data
    else:
        from bot import logger

        logger.error("During update_xp: User entry not found or error occurred.")

    random_xp = random.randint(0, 5)

    xp = int(current_xp + random_xp + add_xp)

    level = await get_level_from_xp(xp)
    if level is None:
        return

    if config.Bot.level_updates_enabled:
        if level > last_level:
            level_increase(level, user_id)

    database_interaction.Users.update_user_entry(
        user_id=user_id,
        increment=False,
        msg_count=msg_count,
        xp=xp,
        level=level,
        cmds_used=cmds_used,
        reported=reported,
        been_reported=been_reported,
        nsfw_opt_out=nsfw_opt_out,
    )

    return
