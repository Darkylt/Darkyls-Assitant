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

import random
import re
from datetime import datetime

import config_reader as config
import database_interaction as db
import hikari
import lightbulb

plugin = lightbulb.Plugin("Messages", "Manages message database entries")


async def sanitize_content(content: str) -> str:
    # Remove leading and trailing whitespace
    content = str(content.strip())
    # Optionally, you can escape specific characters if needed
    # e.g., content = re.sub(r'[<>]', '', content)  # Removes < and > characters
    return content


def detect_sql_injection(content: str) -> bool:
    """
    Basic function to detect SQL injection patterns in the content.

    Args:
        content (str): The content to be checked for SQL injection patterns.

    Returns:
        bool: True if SQL injection patterns are detected, False otherwise.
    """
    # Common SQL injection patterns
    sql_patterns = [
        r"(?i)select\s+.*\s+from\s+",  # SELECT statements
        r"(?i)union\s+all\s+select\s+",  # UNION statements
        r"(?i)insert\s+into\s+",  # INSERT statements
        r"(?i)delete\s+from\s+",  # DELETE statements
        r"(?i)drop\s+table\s+",  # DROP TABLE statements
        r"(?i)update\s+.*\s+set\s+",  # UPDATE statements
        r"(?i)or\s+1=1",  # Common tautology-based injection
        r"(?i)and\s+1=1",  # Another common tautology-based injection
        r"(?i)\'\s+or\s+\'1\'=\'1",  # Single quote based injection
        r"(?i)\'\s+or\s+\'x\'=\'x",  # Another single quote based injection
        r"(?i)\'\s+and\s+\'x\'=\'x",  # Single quote with AND condition
    ]

    for pattern in sql_patterns:
        if re.search(pattern, content):
            return True
    return False


sql_injection_responses = [
    "You think you're so clever, don't you?",
    "Trying to play smart, I see.",
    "I have my eyes on you...",
    "No way you tried that.",
    "Nuh uh.",
]


@plugin.listener(hikari.events.MessageCreateEvent)
async def message_create(event: hikari.MessageCreateEvent) -> None:
    message = event.message

    # if message.guild_id != config.Bot.server:
    #    return

    if message.author.is_bot or message.author.is_system:
        return

    content = await sanitize_content(message.content) if message.content else ""

    if message.attachments:
        attachments = True
    else:
        attachments = False

    created_at = datetime.utcnow().isoformat()

    result = db.Messages.create_message_entry(
        message.id,
        content,
        message.channel_id,
        attachments,
        message.author.id,
        created_at,
    )

    if result is None:
        from bot import logger

        logger.error("There was an error while creating a new message entry.")

    if message.content and detect_sql_injection(content):
        from bot import logger

        logger.warning(
            f"Potential SQL injection attempt detected in message: '{message.content}' by {message.author.username}({message.author.id})"
        )

        await event.message.respond(
            random.choice(sql_injection_responses), reply=message
        )


@plugin.listener(hikari.events.MessageUpdateEvent)
async def message_edit(event: hikari.events.MessageUpdateEvent) -> None:
    message = event.message

    # if message.guild_id != config.Bot.server:
    #    return

    if message.author.is_bot or message.author.is_system:
        return

    content = await sanitize_content(message.content) if message.content else ""

    check = db.Messages.get_message_entry(message.id)

    if check:
        # If multiple entries exist, get the one with the highest 'edited' value
        if isinstance(check, list):
            latest_entry = max(check, key=lambda x: x["edited"])
        else:
            latest_entry = check

        if content == latest_entry["content"]:
            # Return if the content didn't change.
            # Because this is likely not an edit event but a crosspost or embed load event
            return

    if message.attachments:
        attachments = True
    else:
        attachments = False

    result = db.Messages.create_message_edit_entry(
        message.id, content, message.channel_id, attachments, message.author.id
    )

    if result is None:
        from bot import logger

        logger.error("There was an error while creating a new message edit entry.")

    if message.content and detect_sql_injection(content):
        from bot import logger

        logger.warning(
            f"Potential SQL injection attempt detected in message: '{message.content}' by {message.author.username}({message.author.id})"
        )

        await event.message.respond(
            random.choice(sql_injection_responses), reply=message
        )


@plugin.listener(hikari.events.MessageDeleteEvent)
async def message_delete(event: hikari.events.MessageDeleteEvent) -> None:
    message = event.message_id

    # Old message is already handled in Scripts/AutoMod/events.py
    if event.old_message:
        db.Messages.delete_message_entry(message)
        return

    message = db.Messages.get_message_entry(message)

    if message is None:
        return

    if isinstance(message, list):
        latest_entry = max(message, key=lambda x: x["edited"])
    else:
        latest_entry = message

    author = await plugin.app.rest.fetch_user(latest_entry["author"])

    if author is None:
        author_str = latest_entry["author"]
    else:
        author_str = author.mention

    channel = await plugin.app.rest.fetch_channel(latest_entry["channel_id"])

    embed = hikari.Embed(
        title="A message has been deleted.",
        description=f"{author_str}'s message has been deleted.",
        color=(hikari.Color.from_rgb(255, 0, 0)),
    )
    embed.add_field(name="Author:", value=author_str)
    content = str(latest_entry["content"]).replace("`", "'")
    embed.add_field(name="Content:", value=f"```{content}```")
    embed.add_field(name="Channel:", value=channel.mention)
    if latest_entry["edited"] > 0:
        if latest_entry["edited"] == 1:
            embed.add_field(name="Edited:", value=f"1 time")
        else:
            embed.add_field(name="Edited:", value=f"{latest_entry['edited']} times")

    await plugin.app.rest.create_message(config.Bot.logs_channel, embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
