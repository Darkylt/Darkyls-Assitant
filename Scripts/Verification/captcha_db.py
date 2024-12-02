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

import aiofiles
import config_reader as config

DB_PATH = os.path.join(config.Paths.data_folder, "Database", "verification.json")


async def read_db(id: str = None):
    """
    Reads the verification database

    Args:
        id (str): Only read a specific verification ID
    Returns:
        dict: A dictionary of entries
        None: An error occurred
    """
    if os.path.exists(DB_PATH):
        try:
            async with aiofiles.open(DB_PATH, "r") as file:
                data = json.loads(await file.read())
                if id is None:
                    return data
                else:
                    return data.get(id, None)
        except Exception as e:
            from bot import logger

            logger.error(f"Error while reading verification Database: {e}")
            return None
    else:
        return {}


async def register_captcha(
    id: str, user_id: int, captcha_type: int, value: str, message_id: int
):
    """
    For registering a new captcha in the database

    Args:
        id (str): The captcha ID
        user_id (str): The user who the captcha belongs to
        captcha_type (int): The captcha index
        value (str): The solutuon to the captcha
        message_id (int): The ID to the message
    """
    captchas = await read_db() or {}

    captchas[id] = [user_id, captcha_type, str(value), message_id]

    try:
        async with aiofiles.open(DB_PATH, "w") as file:
            await file.write(json.dumps(captchas, indent=4))
    except Exception as e:
        from bot import logger

        logger.error(f"Error while writing to verification Database: {e}")


async def get_id_from_user(user_id: int):
    """
    Gets the captcha ID from a given user id

    Returns:
        captcha_id (str): The captcha ID
        None: Not found / Error
    """
    data = await read_db()

    if data is None:
        from bot import logger

        logger.error(f"Error in get_message_id_from_user(): read_db() returned 'None'")
        return None

    try:
        for captcha_id, (stored_user_id, _, __, ___) in data.items():
            if stored_user_id == user_id:
                return captcha_id
        return None
    except Exception as e:
        from bot import logger

        logger.error(f"Error while getting captcha id from user id: {e}")


async def delete_entries_from_user_id(user_id: int):
    """
    Deletes entries from the verification database containing the given user ID

    Args:
        user_id (int): The user ID to search for and delete
    Returns:
        bool: True if entries were deleted, False otherwise
    """
    data = await read_db()
    if data is None:
        return False

    try:
        # Filter out entries with the given user ID
        updated_data = {
            captcha_id: details
            for captcha_id, details in data.items()
            if details[0] != user_id
        }

        async with aiofiles.open(DB_PATH, "w") as file:
            await file.write(json.dumps(updated_data, indent=4))

        return len(updated_data) != len(data)  # True if any entries were deleted
    except Exception as e:
        from bot import logger

        logger.error(f"Error while deleting entries by user ID: {e}")
        return False


async def get_message_id_from_user(user_id: int):
    """
    Gets the message ID from a given user ID

    Args:
        user_id (int): The user ID to search for

    Returns:
        message_id (int): The message ID
        None: Not found / Error
    """
    data = await read_db()
    if data is None:
        from bot import logger

        logger.error(f"Error in get_message_id_from_user(): read_db() returned 'None'")
        return None
    try:
        for captcha_id, (stored_user_id, _, __, message_id) in data.items():
            if stored_user_id == user_id:
                return message_id
        return None
    except Exception as e:
        from bot import logger

        logger.error(f"Error while getting message id from user id: {e}")
        return None
