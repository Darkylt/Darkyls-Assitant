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
from random import choice

import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("Socials", "A socials command")

SOCIAL_LINKS = {
    "Website": "https://darkylmusic.com",
    "YouTube": "https://www.youtube.com/channel/UC1vqivmEx6wSMN3GGzdMM4A",
    "Twitch": "https://www.twitch.tv/darkyltv",
    "Spotify": "https://open.spotify.com/artist/3uSjSaWZrsNy7PK11dA74N?si=7W6Sx04IT6aHKPOfxq0X5g",
    "Twitter/X": "https://twitter.com/DarkylMusic",
    "TikTok": "https://www.tiktok.com/@darkyltv",
    "SoundCloud": "https://soundcloud.com/darkylmusic",
    "Apple Music": "https://music.apple.com/us/artist/dark-pranking/1544211920",
    "Tidal": "https://tidal.com/browse/artist/35890590",
    "Amazon Music": "https://music.amazon.de/artists/B0BNNQB85B/darkyl",
    "Deezer": "https://www.deezer.com/de/artist/191835557",
    "iHeart Radio": "https://www.iheart.com/artist/id-39272554/",
    "Bluesky": "https://bsky.app/profile/darkylmusic.bsky.social",
}


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("socials", "Get links to all socials of Darkyl")
@lightbulb.implements(lightbulb.SlashCommand)
async def socials_command(ctx: lightbulb.SlashContext):
    """
    A command used to get the social media info of darkyl

    Processing:
        Creates the Embed
        Sends the Embed as Ephemeral
    """

    if not await utils.validate_command(ctx):
        return
    try:
        thumbnail = hikari.File(
            os.path.join(config.Paths.assets_folder, "logo_300x300.png")
        )

        random_text = [
            "dubstep",
            "heavy metal",
            "chill",
            "melodic",
            "experimental",
            "dark",
            "epic",
            "dubstep",
        ]

        links_text = "\n".join(
            [f"[{name}]({url})" for name, url in SOCIAL_LINKS.items()]
        )

        embed = hikari.Embed(
            title="**Darkyl's Social Media Profiles:**",
            description=(
                f"Hi, I am Darkyl. Your gateway to a spectrum of {choice(random_text)} vibes straight outta Germany!\n\n"
                f"Links:\n{links_text}"
            ),
            color=0x9900FF,
        )
        embed.set_thumbnail(thumbnail)

        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during the /socials command: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
