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
from urllib.parse import urlparse

import bot_utils as utils
import buttons
import config_reader as config
import hikari


async def check_attachments(attachments) -> str:
    """
    Returns true if the attachments aren't valid
    """

    for attachment in attachments:
        filename = str(attachment.filename)
        filetype = filename.split(".")[-1]
        if not filetype in config.AutoMod.allowed_files:
            return filename

    return False


async def check_message(content: str, nsfw: bool) -> list[str]:
    """
    A function that performs various checks on a message to moderate it.

    Args:
        content (str): The content of the message
        nsfw (bool): Was the message sent in a channel marked as nsfw?
    Returns:
        list(str): List of violations
    """
    violations = []
    flagged_strings = []
    try:
        if not nsfw:
            if config.AutoMod.filter_nsfw_language:
                nsfw_language_status, flagged_word = await check_for_nswf(content)
                if nsfw_language_status:
                    violations.append(f"NSFW language")
                    flagged_strings.append(flagged_word)

            url_status, flagged_url = await check_url(content)
            if url_status:
                violations.append(f"Disallowed URL")
                flagged_strings.append(flagged_url)

    except Exception as e:
        from bot import logger

        logger.error(f"Error during check_message(): {e}")

    return violations, flagged_strings


async def extract_urls(content: str) -> list:
    """
    Takes in a string and extracts domains.

    Example:
        Input: "I love this video: https://www.youtube.com/watch?v=JqZRB4WtqZI, and this website: https://darkylmusic.com/discord-bot/"
        Return: ["youtube.com", "darkylmusic.com"]
    """
    try:
        # Improved regular expression to find URLs or domains in the content
        url_pattern = re.compile(
            r"https?://[^\s/$.?#].[^\s]*|www\.[^\s/$.?#].[^\s]*|[^\s/$.?#]+\.[^\s/$.?#]+"
        )
        matches = url_pattern.findall(content)

        # Extract domains from the matches
        domains = set()
        for match in matches:
            # Handle URLs starting with 'www.'
            if match.startswith("www."):
                match = "http://" + match

            # Parse URL
            parsed_url = urlparse(match)
            domain = parsed_url.netloc or parsed_url.path

            # Remove any trailing paths or fragments
            domain = domain.split("/")[0]

            # Handle cases where domain might include port number
            domain = domain.split(":")[0]

            # Remove subdomains, keeping only the main domain
            domain_parts = domain.split(".")
            if len(domain_parts) > 2:
                domain = ".".join(domain_parts[-2:])
            domains.add(domain)

        return list(domains)

    except Exception as e:
        from bot import logger

        logger.error(f"Error during extract_urls: {e}")
        return []


async def check_url(content: str):
    """
    Checks if any contained links are on the allow list.

    Args:
        content (str): The content of the message
    Returns:
        True: If the URL is disallowed
        False: If the URL is allowed
    """
    status = False
    flagged_url = ""

    try:

        allow_list_path = os.path.join(
            config.Paths.data_folder, "whitelisted_sites.txt"
        )

        # Read the whitelist file and store allowed domains in a set
        with open(allow_list_path, "r") as file:
            allowed_domains = {line.strip() for line in file if line.strip()}

        # Extract domains from the content
        urls = await extract_urls(content)

        # Check if any of the extracted URLs are not in the whitelist
        for url in urls:
            if url not in allowed_domains:
                status = True
                flagged_url = url
                break

    except Exception as e:
        from bot import logger

        logger.error(f"Error during check_url(): {e}")

    return status, flagged_url


async def check_for_nswf(content: str) -> bool:
    """
    A function that checks if the message contains a banned word.

    Args:
        content (str): The content of the message
    Returns:
        bool: True if the message contains a banned word, False otherwise.
    """

    flagged_word = ""

    # Check for NSFW words
    try:
        banned_words_folder = os.path.join(
            config.Paths.data_folder, "Banned Content", "Words", "NSFW Words"
        )
        nsfw_words_files = os.listdir(banned_words_folder)

        for filename in nsfw_words_files:
            with open(
                os.path.join(banned_words_folder, filename), "r", encoding="utf-8"
            ) as file:
                nsfw_words = file.read().splitlines()
                for word in nsfw_words:
                    if word.lower() in content.lower():
                        flagged_word = word
                        return True, flagged_word
    except Exception as e:
        from bot import logger

        logger.error(f"Error during check_for_nsfw(): {e}")

    return False, flagged_word


""" REPORT SECION """
# Section that handles the reporting


def create_report_embed(
    event: hikari.MessageCreateEvent, violations: list[str], flagged_strings: list[str]
) -> hikari.Embed:
    """Creates an embed for the violation report."""
    try:
        report_embed = hikari.Embed(
            title="**Report**",
            description=f"**AutoMod** has reported {event.author.mention}.",
            color=hikari.Color.from_hex_code("#fc0000"),
        )
        report_embed.set_thumbnail(event.author.make_avatar_url())
        report_embed.add_field(
            "**Reported User:**", value=f"{event.author.mention} `({event.author_id})`"
        )
        report_embed.add_field(
            "**Reason:**",
            value=f"Message contains the following violations:\n{', '.join(violations)}",
        )
        if flagged_strings:
            if len(flagged_strings) > 1:
                formatted_flagged_strings = ", ".join(
                    flagged_strings[:-1] + " and " + flagged_strings[-1]
                )
            else:
                formatted_flagged_strings = flagged_strings[0]
        else:
            formatted_flagged_strings = "None"

        report_embed.add_field("**Flagged:**", value=formatted_flagged_strings)
        report_embed.add_field("**Original Message:**", value=event.message.content)
        return report_embed
    except Exception as e:
        from bot import logger

        logger.error(f"Error during create_report_embed(): {e}")


def update_report_data(user_id, message_id: int, violations: list[str]):
    """Updates the report data."""
    try:
        database_path = os.path.join(
            config.Paths.data_folder, "Database", "reports.json"
        )
        report_data = {}

        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    report_data = json.load(file)
                except json.JSONDecodeError:
                    pass

        user_id = str(user_id)
        if user_id not in report_data:
            report_data[user_id] = {"reasons": {}}

        reason = f"Message contains the following violations:\n{', '.join(violations)} {asyncio.run(utils.generate_id())}"
        report_data[user_id]["reasons"][reason] = {
            "reporter": "AutoMod",
            "report_message": message_id,
        }

        with open(database_path, "w") as file:
            json.dump(report_data, file, indent=4)
    except Exception as e:
        from bot import logger

        logger.error(f"Error during update_report_data(): {e}")


async def handle_violations(
    event: hikari.MessageCreateEvent, violations: list[str], flagged_strings: list[str]
):
    """Handles violations detected by auto moderation."""
    try:
        violation_message = (
            f"Your message contains the following violations:\n{', '.join(violations)}\n\n"
            "You will be reported to a mod.\nIf you believe this is an error, "
            "please message a mod or an admin."
        )
        await event.message.respond(
            violation_message, flags=hikari.MessageFlag.EPHEMERAL
        )

        report_embed = create_report_embed(event, violations, flagged_strings)
        return report_embed
    except Exception as e:
        from bot import logger

        logger.error(f"Error during handle_violations(): {e}")
