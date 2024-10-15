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

import random

import bot_utils as utils
import config_reader as config
import hikari
import image_manager
import lightbulb

plugin = lightbulb.Plugin("Quote", "Generate a quote")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("quote", "Generate a quote from a message")
@lightbulb.implements(lightbulb.MessageCommand)
async def quote_command(ctx: lightbulb.Context):
    if not utils.validate_command(ctx):
        return

    if ctx.author.is_bot or ctx.author.is_system:
        await ctx.respond("Hello fellow bot. Nope.", flags=hikari.MessageFlag.EPHEMERAL)
        return

    from bot import logger

    logger.info(f"{ctx.author.username} used quote command.")
    message = getattr(ctx.options, "target", None)
    author = message.author

    if ctx.author.id == plugin.bot.get_me().id:
        responses = [
            "Mhh...quoting myself...huh...\n(I have no idea how that would work)"
            "I'm confused...I can't quote myself..",
            "Oh, quoting myself now? Guess I'll be writing my own fan mail next.",
            "Quoting myself? That's like high-fiving myself for being awesome. Oh wait, I am awesome. Never mind.",
            "Quoting myself? I'm not sure if that's a flex or just plain narcissism.",
            "Quoting myself? Ah, the sweet sound of validation... from myself.",
            "Quoting me? Sure, let me just pat myself on the back while I'm at it.",
            "Quoting myself? Sorry, I don't speak in echoes.",
            "Quoting me? It's like déjà vu, but with more ego.",
            "Quoting myself? I prefer to let my brilliance speak for itself... literally, in this case.",
            "Quoting me? I guess even bots need a little self-affirmation sometimes.",
            "Well, well, quoting myself, am I? Next, you'll want me to sign my own autograph!",
            "Attempting self-quotation? That's like trying to high-five yourself in the mirror. Just... no.",
            "Quoting myself? Sure, let me just grab a mirror and have a chat with my reflection.",
            "Attempting self-quotation... I see someone's feeling a bit self-centered today, huh?",
            "Quoting myself? That's like trying to teach a parrot to mimic itself. Just... not happening.",
            "Quoting myself? That's like trying to taste your own tongue... not recommended, my friend.",
            "Quoting myself? I prefer to leave the self-reflection to the humans. It's less... circuitous.",
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif ctx.author.id == author.id:
        responses = [
            "Attempting self-quotation? That's like trying to high-five yourself in the mirror. Just... no.",
            "Quoting yourself, huh? Feeling poetic or just practicing your echo?",
            "Attempting self-quotation? Someone's feeling particularly profound today.",
            "Quoting yourself? Ah, the classic 'talking to yourself' move. Bold choice.",
            "Quoting yourself? Well, someone's their own biggest fan today.",
            "Trying to quote yourself? That's like giving yourself a round of applause. Admirable self-esteem.",
            "Quoting yourself? Is this the part where you drop the mic on your own wisdom?",
            "Quoting yourself, eh? Feeling poetic or just short on conversation partners?",
            "Quoting yourself? That's one way to ensure you always get the last word.",
            "Quoting yourself? Remind me, is that the first sign of genius or madness?",
            "Quoting thyself? Thou art a true master of self-appreciation!",
            "Trying to quote yourself? That's like giving yourself a round of applause... in an empty room.",
            "Quoting yourself, huh? Channeling your inner philosopher or just feeling chatty without conversation partners?",
            "Quoting yourself? Ah, the noble pursuit of capturing one's own brilliance for posterity.",
            "Attempting self-quotation? That's like trying to pat your own back. Quite the stretch, isn't it?",
            "Quoting yourself? That's like trying to give yourself a round of applause. Bold move.",
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return

    try:
        user = plugin.bot.cache.get_member(ctx.get_guild(), author)

        content = message.content

        if content is None:
            await ctx.respond(
                "The message is empty :(", flags=hikari.MessageFlag.EPHEMERAL
            )
            return

        message_date = message.created_at.strftime("%Y")

        name = user.username
        if not name:
            name = "Unknown User"

        pfp = user.guild_avatar_url or user.avatar_url or user.default_avatar_url

        if content is None:
            content = " "

        response = await ctx.respond("Processing...")

        pfp = await image_manager.download_image(pfp, user.id)
        if str(pfp).endswith("gif"):
            pfp = await image_manager.gif_to_png(pfp)
        await image_manager.resize_image(pfp, 150)
        quote = await image_manager.quote_generator(content, name, pfp, message_date)
        image = hikari.File(quote)
        await response.edit("Here's your quote:", attachments=[image])
    except Exception as e:
        from bot import logger

        logger.error(f"Error during quote message command: {e}")
        await response.edit(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await image_manager.delete(quote)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
