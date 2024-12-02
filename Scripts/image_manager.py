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

import bot_utils as utils
import config_reader as config
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


async def download_image(image_url, id, path=None):

    clean_image_url = str(image_url).split("?")[0]  # Remove the ?size=4096 from the url

    if clean_image_url.endswith(".png"):
        file_extention = "png"
    elif clean_image_url.endswith(".gif"):
        file_extention = "gif"
    elif clean_image_url.endswith(".gifv"):
        file_extention = "gifv"
    elif clean_image_url.endswith(".jpeg"):
        file_extention = "jpeg"
    elif clean_image_url.endswith(".jpg"):
        file_extention = "jpg"
    else:
        from bot import logger

        logger.error("Invalid image extension during download")
        return None

    if path is None:
        image_path = os.path.join(
            config.Paths.data_folder, "Downloaded Content", f"{id}.{file_extention}"
        )
    else:
        image_path = os.path.join(path, f"{id}.{file_extention}")

    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, "wb") as file:
            file.write(response.content)
        return image_path
    else:
        return None


async def gif_to_png(gif_file) -> str:
    gif_image = Image.open(gif_file)

    png_path = os.path.splitext(gif_file)[0] + ".png"
    with gif_image as img:
        img.save(png_path)

    os.remove(gif_file)

    return png_path


async def resize_image(image_path, res=500):
    """
    A function to resize a square image
    """
    try:
        with Image.open(image_path) as img:
            resized_img = img.resize((res, res))

            resized_img.save(image_path)
    except Exception as e:
        from bot import logger

        logger.error(f"Error resizing image: {e}")


async def make_card(
    background_path, scale_factor=config.Join.welcome_card_scale_factor
):
    background = Image.open(background_path)
    overlay = Image.open(config.Join.overlay_path)

    overlay_width, overlay_height = overlay.size
    canvas = Image.new("RGBA", (overlay_width, overlay_height), (0, 0, 0, 0))

    bg_width, bg_height = background.size
    new_bg_width = int(bg_width * scale_factor)
    new_bg_height = int(bg_height * scale_factor)

    background = background.resize((new_bg_width, new_bg_height))

    position = (
        (overlay_width - new_bg_width) // 2,
        (overlay_height - new_bg_height) // 2,
    )

    canvas.paste(background, position)

    canvas.paste(overlay, (0, 0), overlay)

    canvas.save(background_path)


async def delete(image: str) -> bool:
    """
    A function that deletes an Image/file

    Args:
        image (str): The path to an image
    Returns:
        True: Image successfully deleted
        False: An Error occurred
    """

    try:
        os.remove(image)
        return True
    except Exception as e:
        from bot import logger

        logger.error(
            f"Following error occurred while attempting to delete an image: {e}"
        )
        return False


async def make_love_images(user1_path, user2_path, user1_id, user2_id) -> str:
    user1_img = Image.open(user1_path).convert("RGBA")
    user2_img = Image.open(user2_path).convert("RGBA")

    width = user1_img.width // 2
    user1_half = user1_img.crop((0, 0, width, user1_img.height))
    user2_img.paste(user1_half, (0, 0))

    png_overlay_folder_path = os.path.join(config.Paths.assets_folder, "Love images")
    png_overlay_path = await utils.choose_random_file(png_overlay_folder_path)

    overlay_img = Image.open(png_overlay_path).convert("RGBA")
    overlay_img = overlay_img.resize(user2_img.size)

    combined_img = Image.alpha_composite(user2_img, overlay_img)

    overlayed_image_path = str(
        os.path.join(
            config.Paths.data_folder, "Downloaded Content", f"{user1_id}_{user2_id}.png"
        )
    )
    combined_img.save(overlayed_image_path)

    return overlayed_image_path


async def quote_generator(message: str, username: str, pfp: str, date: str) -> str:
    """
    A function that generates a quote image.

    Args:
        message (str): The content of the quote
        username (str): The one who said the quote
        pfp (str): The path to the profile picture (Make sure the image is resized to 150x150)
        date (str): When was the quote made?
    Returns:
        path (str): The path to the quote image
    """

    profile_picture_enabled = True

    background_image = await utils.choose_random_file(
        os.path.join(config.Paths.assets_folder, "Quote Images")
    )

    image = Image.open(background_image)

    draw = ImageDraw.Draw(image)

    font_path = os.path.join(config.Paths.assets_folder, "Fonts", "Heavitas.ttf")
    font_size = 200
    font = ImageFont.truetype(font_path, font_size)

    if profile_picture_enabled:
        pfp_size = (150, 150)
        pfp_image = Image.open(pfp).convert("RGBA")

        # Apply circular mask
        mask = Image.new("L", pfp_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + pfp_size, fill=255)
        pfp_image = Image.composite(
            pfp_image, Image.new("RGBA", pfp_size, (255, 255, 255, 0)), mask
        )

        # Calculate position to place profile picture at the top center
        pfp_x = (image.width - pfp_size[0]) // 2
        pfp_y = 45

        image.paste(pfp_image, (pfp_x, pfp_y), pfp_image)

    draw_text = ImageDraw.Draw(image)

    words = message.split()
    words_per_lines = 5
    formatted_message = "\n".join(
        [" ".join(words[i : i + 5]) for i in range(0, len(words), words_per_lines)]
    )

    text = f"{formatted_message}\n\n- @{username} ({date})"

    region = (15, 230, 785, 585)
    anchor = "mm"

    x = int((region[2] - region[0]) / 2) + region[0]
    y = int((region[3] - region[1]) / 2) + region[1]
    while font_size > 1:
        bbox = draw_text.textbbox((x, y), text, font=font, anchor=anchor)
        if (
            bbox[0] > region[0]
            and bbox[1] > region[1]
            and bbox[2] < region[2]
            and bbox[3] < region[3]
        ):
            break
        font_size -= 1
        font = font.font_variant(size=font_size)

    draw_text.text((x, y), text, font=font, fill="white", anchor=anchor)

    id = await utils.generate_id(
        os.path.join(config.Paths.data_folder, "Generated Quotes")
    )

    if id is None:
        from bot import logger

        logger.warning(f"No image id could be generated")
        id = ""

    quote_image_path = os.path.join(
        config.Paths.data_folder, "Generated Quotes", f"{username}_{id}.png"
    )
    image.save(quote_image_path)

    return quote_image_path


def average_color(image_path):
    image = Image.open(image_path)

    image.thumbnail((100, 100))

    image = image.convert("RGB")

    pixels = list(image.getdata())

    avg_red = int(sum(pixel[0] for pixel in pixels) / len(pixels))
    avg_green = int(sum(pixel[1] for pixel in pixels) / len(pixels))
    avg_blue = int(sum(pixel[2] for pixel in pixels) / len(pixels))

    return avg_red, avg_green, avg_blue
