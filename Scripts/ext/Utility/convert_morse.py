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

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Converter Morse", "Convert to or from morse code")

morse_alphabet_mapping = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    " ": "/",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ".": ".-.-.-",
    ",": "--..--",
    ":": "---...",
    "?": "..--..",
    "'": ".----.",
    "-": "-....-",
    "/": "-..-.",
    "@": ".--.-.",
    "=": "-...-",
}


def encode(value: str):
    encoded_message = ""
    for char in value[:]:
        if char.upper() in morse_alphabet_mapping:
            encoded_message += morse_alphabet_mapping[char.upper()] + " "
    return encoded_message


def decode(value: str):
    inverse_morse_alphabet = dict((v, k) for (k, v) in morse_alphabet_mapping.items())
    separated_message = value.split(" ")
    decoded_message = ""
    for char in separated_message:
        if char in inverse_morse_alphabet:
            decoded_message += inverse_morse_alphabet[char]
    return decoded_message


def is_valid_text(value: str):
    return all(char.upper() in morse_alphabet_mapping for char in value)


def is_valid_morse(value: str):
    valid_chars = set(".-/ ")
    return all(char in valid_chars for char in value)


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("value", "The value to decode or encode", str, required=True)
@lightbulb.option(
    "mode",
    "Convert Morse to ASCII or vice versa",
    str,
    required=True,
    choices=["text to morse", "morse to text"],
)
@lightbulb.command("converter_morse", "Convert to or from morse", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_binary_command(ctx: lightbulb.SlashContext, mode: str, value: str):
    if not await utils.validate_command(ctx):
        return

    if mode == "text to morse":
        if not is_valid_text(value):
            await ctx.respond(
                "The text contains unsupported characters. Please use only letters, numbers, and basic punctuation.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
        result = encode(value)
    elif mode == "morse to text":
        if not is_valid_morse(value):
            await ctx.respond(
                "The Morse code contains unsupported characters. Please use only '.', '-', '/', and spaces.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
        result = decode(value)

    if len(result) <= 480:
        await ctx.respond(f"```{result}```", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        try:
            await ctx.author.send(f"```{result}```", flags=hikari.MessageFlag.EPHEMERAL)
            await ctx.respond(
                "The output was too large, so I sent it to your DMs!",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        except Exception as e:
            from bot import logger

            logger.error(
                f"An error occurred in /converter_morse during sending to author: {e}"
            )
            await ctx.respond(
                "There was a problem and I could not send the output",
                flags=hikari.MessageFlag.EPHEMERAL,
            )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
