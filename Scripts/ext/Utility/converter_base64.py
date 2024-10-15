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

import base64
import binascii

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Converter Base64", "Convert to or from base64")


"""
Some helper functions for encoding and decoding to and from base64 and ASCII
"""


def encode(value: str):
    """
    Encode a text string into a base64 string.

    Args:
        value (str): A text string to be encoded.
    Returns:
        str: The encoded base64 string.
    """

    try:
        sample_string_bytes = value.encode("utf-8")
        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("utf-8")
        return base64_string, None
    except (binascii.Error, UnicodeDecodeError) as e:
        return None, str(e)


def decode(value: str):
    """
    Decode a base64 string into a text string.

    Args:
        value (str): A base64 string to be decoded.
    Returns:
        tuple: A tuple where the first element is the decoded text string (or an empty string if decoding fails),
               and the second element is either None (indicating success) or the error message (if decoding fails).
    """

    try:
        base64_bytes = value.encode("utf-8")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("utf-8")
        return sample_string, None
    except (binascii.Error, UnicodeDecodeError) as e:
        return None, str(e)


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("value", "The value to decode or encode", str, required=True)
@lightbulb.option(
    "mode",
    "Convert base64 to utf-8 or vice versa",
    str,
    required=True,
    choices=["text to b64", "b64 to text"],
)
@lightbulb.command("converter_base64", "Convert to or from base64", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_base64_command(ctx: lightbulb.SlashContext, mode: str, value: str):
    if not await utils.validate_command(ctx):
        return

    try:
        if mode == "text to b64":
            direction = "Base64 🡪 UTF-8"
            result, error_message = decode(value)
        elif mode == "b64 to text":
            direction = "Base64 🡨 UTF-8"
            result, error_message = encode(value)
        else:
            await ctx.respond(
                "Invalid input for 'mode'.", flags=hikari.MessageFlag.EPHEMERAL
            )
            return

        if result is None:
            await ctx.respond(f"Couldn't use your input: {error_message}")
            return

        await ctx.respond(
            embed=hikari.Embed(
                title=f"{direction} Conversion:", description=f"```{result}```"
            )
        )
    except UnicodeEncodeError:
        await ctx.respond(
            "Found an unsupported character. I can't decode your input.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
