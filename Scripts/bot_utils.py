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

import datetime
import math
import os
import random
import re
import tempfile
import typing as t
from io import BytesIO

import aiohttp
import config_reader as config
import database_interaction
import hikari
import hikari.errors
import lightbulb
import member_managment
import segno
from PIL import Image

"""
A collection of useful utility functions
"""


async def generate_id(folder=None):
    """
    Generates a uuid

    Args:
        folder: If provided, checks if the id is already contained in a folder
    Returns:
        id (str): The generated uuid
        None: If an error occurred
    """
    from uuid import uuid4

    while True:
        try:
            id = str(uuid4())

            # Checks if the ID is already contained in a folders filenames
            if folder:
                if not any(id in filename for filename in os.listdir(folder)):
                    return id
            else:
                return id
        except Exception as e:
            from bot import logger

            logger.error(f"Error during ID Generation: {e}")
            return None


async def choose_random_file(folder_path: str):
    """
    Takes in a path and returns the path to a random file in that directory
    """
    # Check if the provided path is a directory
    if not os.path.isdir(folder_path):
        return "Error: The provided path is not a directory."

    # Get a list of all files in the directory
    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # Check if the directory is empty
    if not files:
        return "Error: The directory is empty."

    # Choose a random file from the list
    random_file = random.choice(files)

    # Return the path to the randomly chosen file
    return str(os.path.join(folder_path, random_file))


async def validate_command(
    ctx: lightbulb.Context,
    report: bool = False,
    nsfw: bool = False,
    message_command: bool = False,
    extra_xp: int = 0,
) -> bool:
    """
    Performs some initial processing of a command.

    Args:
        ctx: The context of the command
        report: Whether or not the command is a report
        nsfw: Whether or not the command is supposed to be NSFW
        message_command: Whether or not the command is a message command
    Returns:
        True: Command is free to be executed
        False: One of the checks failed

    Processing:
        1: Checks if the command executor is a real user
        2: If nsfw, performs checks to validate the usage of the command
        3: Adds the new info to the database
    """

    from bot import logger

    try:
        # Is command author human?
        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond(
                "This command cannot be executed by other bots.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return False

        if nsfw or ctx.command.nsfw:
            try:
                # Check if it's an nsfw channel
                channel = await ctx.app.rest.fetch_channel(ctx.channel_id)
                if not channel.is_nsfw:
                    await ctx.respond(
                        "This command can only be run in a channel marked as NSFW.",
                        flags=hikari.MessageFlag.EPHEMERAL,
                    )
                    return False

                # Check if the command author is nsfw blacklisted
                if await nsfw_blacklisted(ctx.author.id):
                    await ctx.respond(
                        "You opted out of NSFW commands.",
                        flags=hikari.MessageFlag.EPHEMERAL,
                    )
                    return False
            except hikari.errors.ForbiddenError:
                await ctx.respond(
                    "I do not have access to this channel.",
                    flags=hikari.MessageFlag.EPHEMERAL,
                )
                return False
            except hikari.errors.NotFoundError:
                await ctx.respond(
                    "The channel was not found.", flags=hikari.MessageFlag.EPHEMERAL
                )
                return False
            except Exception as e:

                logger.error(f"An error occurred during NSFW checks: {e}")
                await ctx.respond(
                    "An error occurred while performing checks.",
                    flags=hikari.MessageFlag.EPHEMERAL,
                )
                return False

        # if message_command:
        #    logger.info(
        #        f"{ctx.author.username}({ctx.author.id}) used {ctx.command.name} command"
        #    )
        # else:
        #    logger.info(
        #        f"{ctx.author.username}({ctx.author.id}) executed /{ctx.command.name}"
        #    )

        if ctx.guild_id == config.Bot.server:
            # Updating stats
            try:
                id = ctx.author.id.real

                await member_managment.update_user_stats(
                    user_id=int(id),
                    msg=False,
                    cmd=True,
                    rep=report,
                    extra_xp=extra_xp,
                )
            except Exception as e:
                logger.error(f"An error occurred while updating the user stats: {e}")
                await ctx.respond(
                    "An error occurred while updating the user stats.",
                    flags=hikari.MessageFlag.EPHEMERAL,
                )
                return False

            # Logging the command
            options = ctx.raw_options

            if options:
                result = []

                for key, value in options.items():
                    if isinstance(value, (hikari.Role, hikari.InteractionChannel)):
                        result.append(f"{key}({value.name})")
                    elif isinstance(value, hikari.InteractionMember):
                        result.append(f"{key}({value.user.username})")
                    elif isinstance(value, hikari.Attachment):
                        result.append(f"{key}({value.filename})")
                    elif isinstance(value, (bool, str, int, float)):
                        result.append(f"{key}({value})")

                options_str = ", ".join(result)

            else:
                options_str = "No options."

            if not nsfw or ctx.command.nsfw:
                database_interaction.Commands.create_command_entry(
                    ctx.author.id, ctx.command.name, options_str
                )

        return True
    except Exception as e:
        logger.error(f"Error while validating during /{ctx.command.name}: {e}")
        await ctx.respond("An error occurred.", flags=hikari.MessageFlag.EPHEMERAL)
        return False


async def uwu_maker(text: str):
    """
    A function for 'owoifying' text

    Args:
        text (str): The text that should be processed
    Returns:
        text (str): The processed text

    Example:
        Pre: Lorem ipsum dolor sit amet
        Post: Wowem ipsum dowow sit amet
    """

    faces = ["owo", "UwU", ">w<", "^w^"]
    v = text
    r = re.sub("[rl]", "w", v)
    r = re.sub("[RL]", "W", r)
    r = re.sub("ove", "uv", r)
    r = re.sub("n", "ny", r)
    r = re.sub("N", "NY", r)
    r = re.sub("[!]", " " + random.choice(faces) + " ", r + "~")
    return r


jargonWordPool = [
    [
        "TCP",
        "HTTP",
        "SDD",
        "RAM",
        "GB",
        "CSS",
        "SSL",
        "AGP",
        "SQL",
        "FTP",
        "PCI",
        "AI",
        "ADP",
        "RSS",
        "XML",
        "EXE",
        "COM",
        "HDD",
        "THX",
        "SMTP",
        "SMS",
        "USB",
        "PNG",
        "PHP",
        "UDP",
        "TPS",
        "RX",
        "ASCII",
        "CD-ROM",
        "CGI",
        "CPU",
        "DDR",
        "DHCP",
        "BIOS",
        "IDE",
        "IP",
        "MAC",
        "MP3",
        "AAC",
        "PPPoE",
        "SSD",
        "SDRAM",
        "VGA",
        "XHTML",
        "Y2K",
        "GUI",
    ],
    [
        "auxiliary",
        "primary",
        "back-end",
        "digital",
        "open-source",
        "virtual",
        "cross-platform",
        "redundant",
        "online",
        "haptic",
        "multi-byte",
        "bluetooth",
        "wireless",
        "1080p",
        "neural",
        "optical",
        "solid state",
        "mobile",
        "unicode",
        "backup",
        "high speed",
        "56k",
        "analog",
        "fiber optic",
        "central",
        "visual",
        "ethernet",
        "encrypted",
        "decrypted",
    ],
    [
        "driver",
        "protocol",
        "bandwidth",
        "panel",
        "microchip",
        "program",
        "port",
        "card",
        "array",
        "interface",
        "system",
        "sensor",
        "firewall",
        "hard drive",
        "pixel",
        "alarm",
        "feed",
        "monitor",
        "application",
        "transmitter",
        "bus",
        "circuit",
        "capacitor",
        "matrix",
        "address",
        "form factor",
        "array",
        "mainframe",
        "processor",
        "antenna",
        "transistor",
        "virus",
        "malware",
        "spyware",
        "network",
        "internet",
    ],
    [
        "back up",
        "bypass",
        "hack",
        "override",
        "compress",
        "copy",
        "navigate",
        "index",
        "connect",
        "generate",
        "quantify",
        "calculate",
        "synthesize",
        "input",
        "transmit",
        "program",
        "reboot",
        "parse",
        "shut down",
        "inject",
        "transcode",
        "encode",
        "attach",
        "disconnect",
        "network",
    ],
    [
        "backing up",
        "bypassing",
        "hacking",
        "overriding",
        "compressing",
        "copying",
        "navigating",
        "indexing",
        "connecting",
        "generating",
        "quantifying",
        "calculating",
        "synthesizing",
        "inputting",
        "transmitting",
        "programming",
        "rebooting",
        "parsing",
        "shutting down",
        "injecting",
        "transcoding",
        "encoding",
        "attaching",
        "disconnecting",
        "networking",
    ],
]

jargonConstructs = [
    "If we {3} the {2}, we can get to the {0} {2} through the {1} {0} {2}!",
    "We need to {3} the {1} {0} {2}!",
    "Try to {3} the {0} {2}, maybe it will {3} the {1} {2}!",
    "You can't {3} the {2} without {4} the {1} {0} {2}!",
    "Use the {1} {0} {2}, then you can {3} the {1} {2}!",
    "The {0} {2} is down, {3} the {1} {2} so we can {3} the {0} {2}!",
    "{4} the {2} won't do anything, we need to {3} the {1} {0} {2}!",
    "I'll {3} the {1} {0} {2}, that should {3} the {0} {2}!",
    "My {0} {2} is down, our only choice is to {3} and {3} the {1} {2}!",
    "They're inside the {2}, use the {1} {0} {2} to {3} their {2}!",
    "Send the {1} {2} into the {2}, it will {3} the {2} by {4} its {0} {2}!",
]


async def error_fun() -> str:
    """
    A function for spicing up error messages.
    Chooses either to generate random technobabble or a coding joke

    Returns:
        A string with either a joke or technobabble
        An empty string if an error occurred
    """
    try:
        choice = random.randint(0, 1)  # 0 means technobabble, 1 means joke

        if choice == 0:
            text = await technobabble()
        else:
            joke = await coding_joke()
            text = f"Let me lighten the mood with a coding joke:\n{joke}"

        if not text:
            return ""
        return f"\n{text}"
    except Exception as e:
        from bot import logger

        logger.error(f"Following error occurred during error_fun(): {e}")
        return ""


async def technobabble() -> str:
    """
    A function that does some complex stuff to generate technobabble

    Returns:
        A randomly generated sentence
        An empty string if an error occurred
    """
    try:
        h = []

        def j(b):
            c = jargonWordPool[b]
            e = math.floor(random.random() * len(c))
            f = c[e]
            while f in h:
                f = c[math.floor(random.random() * len(c))]
            h.append(f)
            return f

        rnd = math.floor(random.random() * len(jargonConstructs))
        construct = jargonConstructs[rnd]

        e = 0
        while e < len(jargonWordPool):
            f = "{" + str(e) + "}"
            while construct.find(f) > -1:
                construct = construct.replace(f, j(e), 1)
            e += 1

        construct = construct[0].upper() + construct[1:]
        return str(construct)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while generating technobabble: {e}")
        return ""


async def coding_joke() -> str:
    """
    A function to get a coding joke from jokeapi.dev

    Returns:
        The joke
        An empty string if an error occurred
    """
    url = "https://v2.jokeapi.dev/joke/Coding?blacklistFlags=political,racist,sexist"
    params = {"format": "json", "amount": 1, "lang": "en"}

    try:
        from bot import logger

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("error"):
                        return ""
                    if data["type"] == "twopart":
                        return f"{data['setup']}\n||{data['delivery']}||"
                    elif data["type"] == "single":
                        return data["joke"]
                else:
                    logger.error(
                        f"Failed to fetch joke during error_fun: {response.status}"
                    )
        return ""
    except aiohttp.ServerTimeoutError:
        logger.error(f"Failed to fetch coding joke: API timed out.")
        return ""
    except Exception as e:
        logger.error(f"Error during error_fun in coding_joke(): {e}")
        return ""


async def count_lines_in_files(
    directory,
    file_extensions: list[str] = [
        ".txt",
        ".py",
        "",
        ".yml",
        ".log",
        ".json",
        ".pxd",
        ".pxi",
        ".pyi",
        ".hash",
        ".pem",
        ".js",
        ".html",
        ".css",
    ],
):
    """
    A function that counts the lines in the files for a given directory

    Args:
        directory: The path to the directory that should be counted
        file_extensions (list): A list of file extensions that should by counted

    Returns:
        total_lines: The total number of counted lines
        file_count: The total number of counted files
    """
    total_lines = 0
    file_count = 0

    # List files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                # Count lines in each file
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    file_count += 1
            except UnicodeDecodeError:
                pass
            except Exception as e:
                pass

    return (total_lines), file_count


def format_dt(time: datetime.datetime, style: str | None = None) -> str:
    """Convert a datetime into a Discord timestamp.

    For styling see this link: https://discord.com/developers/docs/reference#message-formatting-timestamp-styles.
    """
    valid_styles = [
        "t",  # Short time (e.g 09:01)
        "T",  # Long time (e.g 09:01:00)
        "d",  # Short Date (e.g 28/11/2018)
        "D",  # Long Date (e.g 28 November 2018)
        "f",  # Short Date/Time (e.g 28 November 2018 09:01)
        "F",  # Long Date/Time (e.g Wednesday, 28 November 2018 09:01)
        "R",  # Relative Time (e.g 3 years ago)
    ]

    if style and style not in valid_styles:
        raise ValueError(
            f"Invalid style passed. Valid styles: {' '.join(valid_styles)}"
        )

    if style:
        return f"<t:{int(time.timestamp())}:{style}>"

    return f"<t:{int(time.timestamp())}>"


def iso_8601_to_discord_timestamp(time: str) -> str:
    created_at = datetime.datetime.fromisoformat(time)

    # Assume the datetime is in UTC and make it timezone-aware
    created_at = created_at.replace(tzinfo=datetime.timezone.utc)

    # Convert to Unix timestamp
    unix_timestamp = int(created_at.timestamp())

    # Format as Discord timestamp
    formatted_date = f"<t:{unix_timestamp}>"

    return formatted_date


BADGE_MAPPING = {
    hikari.UserFlag.BUG_HUNTER_LEVEL_1: "<:badge_bug_hunter_level_1:1265030107639316672>",
    hikari.UserFlag.BUG_HUNTER_LEVEL_2: "<:badge_bug_hunter_level_2:1265030128145272925>",
    hikari.UserFlag.DISCORD_CERTIFIED_MODERATOR: "<:badge_certified_moderator:1265030135912857641>",
    hikari.UserFlag.EARLY_SUPPORTER: "<:badge_early_supporter:1265030144431489155>",
    hikari.UserFlag.EARLY_VERIFIED_DEVELOPER: "<:badge_early_verified_developer:1265032683143303250>`",
    hikari.UserFlag.HYPESQUAD_EVENTS: "<:badge_hype_squad_events:1265030182117314613>",
    hikari.UserFlag.HYPESQUAD_BALANCE: "<:badge_hype_squad_balance:1265030157249544274>",
    hikari.UserFlag.HYPESQUAD_BRAVERY: "<:badge_hype_squad_bravery:1265030166493663242>",
    hikari.UserFlag.HYPESQUAD_BRILLIANCE: "<:badge_hype_squad_brilliance:1265030174240673864>",
    hikari.UserFlag.PARTNERED_SERVER_OWNER: "<badge_partner:1265030191928049741>",
    hikari.UserFlag.DISCORD_EMPLOYEE: "<:badge_staff:1265030200127918100>",
    hikari.UserFlag.ACTIVE_DEVELOPER: "<:badge_verified_developer:1265030206494740530>",
    hikari.UserFlag.VERIFIED_BOT: "<:badge_verified_bot:1265031791853699203>",
}


def get_badges(user: hikari.User) -> t.Sequence[str]:
    """Return a list of badge emojies that the user has."""
    return [emoji for flag, emoji in BADGE_MAPPING.items() if flag & user.flags]


def sort_roles(roles: t.Sequence[hikari.Role]) -> t.Sequence[hikari.Role]:
    """Sort a list of roles in a descending order based on position."""
    return sorted(roles, key=lambda r: r.position, reverse=True)


def get_color(member: hikari.Member) -> hikari.Color | None:
    """A function that gets the color of a profile from a hikari.Member object"""
    roles = sort_roles(member.get_roles())
    if roles:
        for role in roles:
            if role.color != hikari.Color.from_rgb(0, 0, 0):
                return role.color

    return None


async def nsfw_blacklisted(user_id: int) -> bool:
    """
    A helper function that checks if a user is NSFW blacklisted/opted out of NSFW

    Args:
        user_id (int): The id of the user you want to enter
    Returns:
        True: User is blacklisted
        False: User isn't blacklisted
    """

    entry = database_interaction.Users.get_user_entry(user_id, values=["nsfw_opt_out"])
    if entry is None:
        return False

    nsfw_opt_out = bool(entry[0])

    return nsfw_opt_out


class QRCode:
    supported_colors = [
        "aliceblue",
        "antiquewhite",
        "aqua",
        "aquamarine",
        "azure",
        "beige",
        "bisque",
        "black",
        "blanchedalmond",
        "blue",
        "blueviolet",
        "brown",
        "burlywood",
        "cadetblue",
        "chartreuse",
        "chocolate",
        "coral",
        "cornflowerblue",
        "cornsilk",
        "crimson",
        "cyan",
        "darkblue",
        "darkcyan",
        "darkgoldenrod",
        "darkgray",
        "darkgreen",
        "darkgrey",
        "darkkhaki",
        "darkmagenta",
        "darkolivegreen",
        "darkorange",
        "darkorchid",
        "darkred",
        "darksalmon",
        "darkseagreen",
        "darkslateblue",
        "darkslategray",
        "darkslategrey",
        "darkturquoise",
        "darkviolet",
        "deeppink",
        "deepskyblue",
        "dimgray",
        "dimgrey",
        "dodgerblue",
        "firebrick",
        "floralwhite",
        "forestgreen",
        "fuchsia",
        "gainsboro",
        "ghostwhite",
        "gold",
        "goldenrod",
        "gray",
        "green",
        "greenyellow",
        "grey",
        "honeydew",
        "hotpink",
        "indianred",
        "indigo",
        "ivory",
        "khaki",
        "lavender",
        "lavenderblush",
        "lawngreen",
        "lemonchiffon",
        "lightblue",
        "lightcoral",
        "lightcyan",
        "lightgoldenrodyellow",
        "lightgray",
        "lightgreen",
        "lightgrey",
        "lightpink",
        "lightsalmon",
        "lightseagreen",
        "lightskyblue",
        "lightslategray",
        "lightslategrey",
        "lightsteelblue",
        "lightyellow",
        "lime",
        "limegreen",
        "linen",
        "magenta",
        "maroon",
        "mediumaquamarine",
        "mediumblue",
        "mediumorchid",
        "mediumpurple",
        "mediumseagreen",
        "mediumslateblue",
        "mediumspringgreen",
        "mediumturquoise",
        "mediumvioletred",
        "midnightblue",
        "mintcream",
        "mistyrose",
        "moccasin",
        "navajowhite",
        "navy",
        "oldlace",
        "olive",
        "olivedrab",
        "orange",
        "orangered",
        "orchid",
        "palegoldenrod",
        "palegreen",
        "paleturquoise",
        "palevioletred",
        "papayawhip",
        "peachpuff",
        "peru",
        "pink",
        "plum",
        "powderblue",
        "purple",
        "red",
        "rosybrown",
        "royalblue",
        "saddlebrown",
        "salmon",
        "sandybrown",
        "seagreen",
        "seashell",
        "sienna",
        "silver",
        "skyblue",
        "slateblue",
        "slategray",
        "slategrey",
        "snow",
        "springgreen",
        "steelblue",
        "tan",
        "teal",
        "thistle",
        "tomato",
        "turquoise",
        "violet",
        "wheat",
        "white",
        "whitesmoke",
        "yellow",
        "yellowgreen",
    ]

    def validate_color(color):
        """
        Validates the color input.

        Supported color formats:
            - CSS color names
            - RGB as tuple (R, G, B)
            - Hexadecimal (6 char and 8 char with alpha)

        Args:
            color: The color input to be validated

        Returns:
            bool: True if the color is valid, False otherwise
        """

        if isinstance(color, str):
            # Check if it's a CSS color name
            if color.lower() in QRCode.supported_colors:
                return True
            # Check if it's a hex color code
            if re.fullmatch(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$", color):
                return True
        elif isinstance(color, tuple) and len(color) == 3:
            # Check if it's an RGB tuple
            if all(
                isinstance(component, int) and 0 <= component <= 255
                for component in color
            ):
                return True
        return False

    async def validate_colors(*colors):
        """
        Validates multiple color inputs.

        Args:
            colors: The color inputs to be validated

        Returns:
            bool: True if all colors are valid, False otherwise
        """

        return all(QRCode.validate_color(color) for color in colors)

    async def generate_qrcode(
        data,
        filename: str,
        scale: int = 1,
        color_background="white",
        color_data="black",
        color_outline=None,
        image: str = None,
        icon: Image.Image = None,
        margin: int = 7,
    ) -> str:
        """
        Generates a QR code

        Supported colors:
            CSS color codes
            RGB as tuple
            Hexadecimal (6 char and 8 char)

        Args:
            data: The contained data
            filename (str): The filename of the generated QR code
            scale (int): The size of each module in pixels
            color_background: The color of the background
            color_data: The color of the modules
            color_outline: The color of the quiet zone
            image: The background image / gif
            icon: The icon (do not use with image)
            margin: The margin in pixels around the icon background
        Returns:
            filepath (str): The path to the generated image file
        """
        if image and icon:
            raise ValueError(
                "Error during generate_qrcode: Image and Icon can't be used simultaneously"
            )

        if str(image).endswith(".gif"):
            extension = "gif"
        else:
            extension = "png"

        filepath = os.path.join(
            config.Paths.data_folder, "Generated QRCodes", f"{filename}.{extension}"
        )

        if image:
            qr = segno.make(data, error="h")
            qr.to_artistic(background=image, target=filepath, scale=scale)
        else:
            if not color_outline:
                color_outline = color_background

            qr = segno.make(data, error="h")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                tmp_filepath = tmp_file.name
                qr.save(
                    tmp_filepath,
                    scale=scale,
                    border=2,
                    light=color_background,
                    dark=color_data,
                    quiet_zone=color_outline,
                )

            qr_img = Image.open(tmp_filepath).convert("RGBA")

            if icon:
                icon_size = (
                    qr_img.size[0] // 4
                )  # Set the icon size relative to the QR code size
                icon_img = icon.copy().convert("RGBA")
                icon_img.thumbnail((icon_size, icon_size))

                # Calculate the size of the background with the margin
                bg_size = (icon_img.width + 2 * margin, icon_img.height + 2 * margin)
                background = Image.new("RGBA", bg_size, color_background)

                # Create a new image that will serve as the overlay with a transparent background
                overlay = Image.new("RGBA", qr_img.size, (255, 255, 255, 0))

                # Calculate the position of the background with margin
                bg_position = (
                    (qr_img.size[0] - bg_size[0]) // 2,
                    (qr_img.size[1] - bg_size[1]) // 2,
                )
                icon_position = (bg_position[0] + margin, bg_position[1] + margin)

                # Paste the solid color background onto the overlay at the icon position
                overlay.paste(background, bg_position)

                # Composite the overlay with the QR code image
                qr_img = Image.alpha_composite(qr_img, overlay)

                # Paste the icon on top of the modified QR code image
                qr_img.paste(icon_img, icon_position, icon_img)

            qr_img.save(filepath)
            os.remove(tmp_filepath)

        return filepath
