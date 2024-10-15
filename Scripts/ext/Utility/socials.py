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

        text = "[Website](https://darkylmusic.com)\n[YouTube](https://www.youtube.com/channel/UC1vqivmEx6wSMN3GGzdMM4A)\n[Twitch](https://www.twitch.tv/darkyltv)\n[Spotify](https://open.spotify.com/artist/3uSjSaWZrsNy7PK11dA74N?si=7W6Sx04IT6aHKPOfxq0X5g)\n[Twitter/X](https://twitter.com/DarkylMusic)\n[TikTok](https://www.tiktok.com/@darkyltv)\n[SoundCloud](https://soundcloud.com/darkylmusic)\n[Apple Music](https://music.apple.com/us/artist/dark-pranking/1544211920)\n[Tidal](https://tidal.com/browse/artist/35890590)\n[Amazon Music](https://music.amazon.de/artists/B0BNNQB85B/darkyl)\n[Deezer](https://www.deezer.com/de/artist/191835557)\n[iHeart Radio](https://www.iheart.com/artist/id-39272554/)"

        embed = hikari.Embed(
            title="**Darkyl's Social Media Profiles:**",
            description=f"Hi, I am Darkyl. Your gateway to a spectrum of {choice(random_text)} vibes straight outta Germany!\n\nLinks:\n{text}",
            color=0x9900FF,
        )
        embed.set_thumbnail(thumbnail)
        # embed.add_field(name="Website:", value="https://darkylmusic.com", inline=False)
        # embed.add_field(name="YouTube:", value="https://www.youtube.com/channel/UC1vqivmEx6wSMN3GGzdMM4A", inline=False)
        # embed.add_field(name="Twitch:", value="https://www.twitch.tv/darkyltv", inline=False)
        # embed.add_field(name="Spotify:", value="https://open.spotify.com/artist/3uSjSaWZrsNy7PK11dA74N?si=7W6Sx04IT6aHKPOfxq0X5g", inline=False)
        # embed.add_field(name="Twitter/X:", value="https://twitter.com/DarkylMusic", inline=False)
        # embed.add_field(name="TikTok:", value="https://www.tiktok.com/@darkyltv", inline=False)
        # embed.add_field(name="SoundCloud:", value="https://soundcloud.com/darkylmusic", inline=False)
        # embed.add_field(name="Apple Music:", value="https://music.apple.com/us/artist/dark-pranking/1544211920", inline=False)
        # embed.add_field(name="Tidal:", value="https://tidal.com/browse/artist/35890590", inline=False)
        # embed.add_field(name="Amazon Music:", value="https://music.amazon.de/artists/B0BNNQB85B/darkyl", inline=False)
        # embed.add_field(name="Deezer:", value="https://www.deezer.com/de/artist/191835557", inline=False)
        # embed.add_field(name="iHeart Radio:", value="https://www.iheart.com/artist/id-39272554/", inline=False)

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
