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
import os
import random

import bot_utils as utils
import config_reader as config
import hikari
import hikari.messages
import lightbulb
import member_managment
import Verification.captcha_db as db


class Captcha:
    """
    Captcha type
    """

    def __init__(self, captcha_name: str, generator_func, captcha_index: int):
        self.name = captcha_name
        self.generator_func = generator_func
        self.captchas = []
        self.index = captcha_index

    async def generate(self, id):
        captcha = await self.generator_func(id)
        self.captchas.append(captcha)
        self.index += 1
        return captcha


import Verification.Generators
import Verification.Generators.image
import Verification.Generators.math

captchas = [
    Captcha("Image Captcha", Verification.Generators.image.generate, 1),
    Captcha("Math Captcha", Verification.Generators.math.generate, 1),
]


async def create_captcha(bot, user_id):

    user = await bot.rest.fetch_user(user_id)

    id = await utils.generate_id(
        os.path.join(config.Paths.data_folder, "Generated Captchas")
    )

    captcha: Captcha = random.choice(captchas)

    embed = hikari.Embed(
        title=f"Extra Verification ({captcha.name})",
        description=(
            "We require some extra Verification_Old at the moment to prove that you're a real user."
            if config.Verification.force_captcha
            else "We are experiencing high amounts of traffic at the moment. Due to this we need to perform some extra Verification_Old steps."
        ),
    )
    embed.set_author(name=id)

    result = await captcha.generate(embed, id)

    if result:
        embed: hikari.Embed = result[0]
        solution: str = result[1]

    embed.add_field(
        name="\nCan't get it?",
        value="Write 'Regenerate' to get a new captcha.",
        inline=False,
    )

    message = await user.send(embed)

    await db.register_captcha(id, user_id, captcha.index, solution, message.id)


async def regenerate(bot, user_id):
    message = await db.get_message_id_from_user(user_id)
    user = await bot.rest.fetch_user(user_id)
    channel = await user.fetch_dm_channel()

    await bot.rest.delete_message(channel, message)

    await db.delete_entries_from_user_id(user_id)

    await create_captcha(bot, user_id)


async def verify_solution(message: hikari.Message):
    """
    Seeing if the captcha is correct
    """

    author = message.author

    member = await message.app.rest.fetch_member(config.Bot.server, author.id)

    if not member:
        await message.respond("You are not a member of the Server.", reply=message)
        return

    captcha_id = await db.get_id_from_user(author.id)

    data = await db.read_db(captcha_id)
    if not data or len(data) < 3:
        from bot import logger

        logger.error("The read data was empty or incomplete")
        await message.respond("An error occurred on my end.", reply=message)
        return

    expected_solution = data[2]

    if message.content.lower().replace("0", "O") == str(expected_solution).lower():

        # Checking if the user already has the verified role
        if any(num == config.Bot.verified_role for num in member.role_ids):
            await message.respond("You are already verified :)")
            return

        await member.add_role(config.Bot.verified_role)
        await message.respond("You are now verified!\nHave fun :)")
        await db.delete_entries_from_user_id(author.id)
        await member_managment.new_member(member)

    else:

        await message.respond("Failed to verify.")
        msg = await db.get_message_id_from_user(author.id)
        await message.app.rest.delete_message(await author.fetch_dm_channel(), msg)
        await db.delete_entries_from_user_id(author.id)
