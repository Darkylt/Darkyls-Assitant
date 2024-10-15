"""
A template so I can remember how to write new captchas
"""

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

from typing import Tuple

import hikari


async def make_embed(embed: hikari.Embed) -> hikari.Embed:

    # Edit this
    task = "DESCRIBE WHAT THE USER HAS TO DO"

    embed.add_field("Task:", task, inline=True)
    return embed


async def generate(embed: hikari.Embed, captcha_id: str) -> Tuple[hikari.Embed, str]:
    """
    This is the function that gets called when generating the captcha

    It needs to:
        Be asynchronous
        Generate an embed
        Return first embed and then the solution string
    """

    # Perform whatever code to make the captcha
    solution = "Whatever the solution is"

    embed = await make_embed(embed)
    return embed, str(solution)
