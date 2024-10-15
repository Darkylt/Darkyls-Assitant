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

import os
import random
import string
from typing import Tuple

import bot_utils as utils
import config_reader as config
import hikari
from captcha.image import ImageCaptcha
from PIL import Image


async def get_all_file_paths(folder: str) -> list:
    """
    Gets all files paths within a given folder

    Args:
        folder (str): The path to the folder
    Returns:
        file_paths (list): The list of file paths
    """

    file_paths = []

    for root, _, files in os.walk(folder):
        for file in files:
            file_paths.append(os.path.join(root, file))

    return file_paths


async def generate_random_string(length: int) -> str:
    """
    Generates a random string of uppercase letters and digits.

    Args:
        length (int): Length of the generated string
    Returns:
        str: The generated random string
    """

    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(length)).replace("0", "O")


async def overlay_texture(image_path: str) -> str:
    # Choose a random texture file from the specified folder
    texture_path = await utils.choose_random_file(
        os.path.join(config.Paths.assets_folder, "Captcha Textures")
    )

    # Open the image and texture files
    image = Image.open(image_path).convert("RGBA")
    texture = Image.open(texture_path).convert("RGBA")

    # Ensure the texture has the same resolution as the image
    texture = texture.resize(image.size)

    # Randomize the opacity of the texture
    opacity = random.randint(20, 63)
    texture = texture.copy()
    texture.putalpha(opacity)

    # Overlay the texture onto the image
    combined = Image.alpha_composite(image, texture)

    # Save the result
    # output_path = os.path.splitext(image_path)[0] + "_with_texture.png"
    combined.save(image_path)

    return image_path


async def make_embed(embed: hikari.Embed, image) -> hikari.Embed:

    embed.set_image(hikari.File(image))

    # Edit this
    task = "Below is an image of letters. **Please send me the letters.**"

    embed.add_field("Task:", task, inline=True)
    return embed


async def generate(embed: hikari.Embed, captcha_id: str) -> Tuple[hikari.Embed, str]:

    fonts = await get_all_file_paths(
        "C:/Users/paul/OneDrive/Desktop/Coding/Discord Bots/DarkylAssistant/Assets/Fonts/captcha fonts"
    )

    text = await generate_random_string(6)

    captcha: ImageCaptcha = ImageCaptcha(
        width=400, height=220, fonts=fonts, font_sizes=(40, 70, 100, 60, 80, 90)
    )

    captcha_path = os.path.join(
        config.Paths.data_folder, "Generated Captchas", f"{captcha_id}.png"
    )

    captcha.write(chars=text, output=captcha_path)

    await overlay_texture(captcha_path)

    solution = text

    embed = await make_embed(embed, captcha_path)
    return embed, str(solution)
