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
import re
from io import BytesIO

import aiohttp
import bot_utils as utils
import config_reader as config
import hikari
import lightbulb
import PIL
import segno
from bot_utils import QRCode
from PIL import Image

plugin = lightbulb.Plugin("QRCode", "Generate QR Code")


async def parse_color(color_str):
    """
    Parses a color string and returns a tuple if it's an RGB value,
    otherwise returns the string as is.

    Args:
        color_str (str): The color string to parse.

    Returns:
        str or tuple: The parsed color.
    """
    rgb_pattern = re.compile(r"^\s*(\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\s*$")
    match = rgb_pattern.match(color_str)

    if match:
        r, g, b = map(int, match.groups())
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            return (r, g, b)

    return color_str


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "data", "The data that the QR code should contain", type=str, required=True
)
@lightbulb.option(
    "scale",
    "The scale of each pixel in pixels",
    type=int,
    min_value=1,
    max_value=100,
    required=False,
    default=8,
)
# Colors don't work with icons sadly and I'm too tired to fix rn
# @lightbulb.option("color_background", "The background color (CSS color code, hex (6char and 8char), RGB)", type=str, required=False, default="white")
# @lightbulb.option("color_data", "The color of the data (CSS color code, hex (6char and 8char), RGB)", type=str, required=False, default="black")
# @lightbulb.option("color_outline", "The color of the outline (CSS color code, hex (6char and 8char), RGB)", type=str, required=False, default="white")
@lightbulb.option(
    "image",
    "A background image/gif (doesn't allow for colors)",
    type=hikari.OptionType.ATTACHMENT,
    required=False,
    default=None,
)
@lightbulb.option(
    "icon",
    "Put an icon in the middle (doesn't work with image)",
    type=hikari.OptionType.ATTACHMENT,
    required=False,
    default=None,
)
@lightbulb.command(
    "qrcode", "Generate QR Code", pass_options=True, auto_defer=True, ephemeral=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def qrcode_command(
    ctx: lightbulb.SlashContext,
    data: str,
    scale: int,
    image: hikari.Attachment,
    icon: hikari.Attachment,
    color_background: str = "white",
    color_data: str = "black",
    color_outline: str = "white",
) -> None:
    if not await utils.validate_command(ctx):
        return

    qr_codes_folder = os.path.join(config.Paths.data_folder, "Generated QRCodes")

    id = await utils.generate_id(qr_codes_folder)

    if image and icon:
        image = None

    if image:
        allowed_files = [".png", ".jpg", ".jpeg", ".gif"]
        image_extension = os.path.splitext(image.filename)[1].lower()

        if image_extension not in allowed_files:
            await ctx.respond(
                f"The image file must be one of the following types: {', '.join(allowed_files)}."
            )
            return

        import image_manager

        image = await image_manager.download_image(image.url, id)

        if image_extension == ".gif":
            # Gifs take longer, so some immediate feedback is probably nice
            msg = await ctx.respond("Generating QR code...")

    else:
        color_background = await parse_color(color_background)
        color_data = await parse_color(color_data)
        color_outline = await parse_color(color_outline)

        # Validate colors
        if not await QRCode.validate_colors(
            color_background, color_data, color_outline
        ):
            await ctx.respond(
                "One or more colors are invalid. Please provide valid CSS color codes, hex values, or RGB values."
            )
            return

    icon_img = None
    if icon:
        if os.path.splitext(icon.filename)[1].lower() not in [".png", ".jpg", ".jpeg"]:
            await ctx.respond(
                "Your icon file is not supported. Please upload either .png, .jpg or .jpeg"
            )
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(icon.url) as resp:
                if resp.status == 200:
                    icon_bytes = await resp.read()
                    icon_img = Image.open(BytesIO(icon_bytes))
                else:
                    await ctx.respond(
                        f"Couldn't download your icon. Error code: {resp.status}"
                    )
                    return

    try:
        qrcode = await QRCode.generate_qrcode(
            data=data,
            filename=id,
            scale=scale,
            color_background=color_background,
            color_data=color_data,
            color_outline=color_outline,
            image=image,
            icon=icon_img,
        )
    except segno.encoder.DataOverflowError:
        await ctx.respond(
            "Data too large. No (Micro) QR Code can handle the provided data"
        )
        return
    except ValueError as e:
        # This error is thrown if the image is corrupted. According to my tests at least.
        if str(e) == "cairosvg is required for SVG support":
            await ctx.respond("Cannot identify image file.")
        else:
            await ctx.respond("An unexpected error occurred.")
        return

    embed = hikari.Embed(
        title="Here's your QR Code",
        description=f"Here's your generated QR code with the data:\n```{data}```",
    )
    embed.set_image(hikari.File(qrcode))

    if image:
        if image_extension == ".gif":
            await msg.edit("", embed=embed)

    await ctx.respond(embed=embed)

    os.remove(qrcode)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
