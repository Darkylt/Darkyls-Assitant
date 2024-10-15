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

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb
import nekos

plugin = lightbulb.Plugin("Gifs", "Send some gifs")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("cat", "Send a cat gif :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def cat_command(ctx: lightbulb.SlashContext, type="Cats"):
    """
    A command used to send a cat gif

    Processing:
        Gets the path to a random gif file
        Responds with the gif file
    """
    if not await utils.validate_command(ctx):
        return

    try:
        folder = os.path.join(config.Paths.assets_folder, "Gifs", type)

        gif = await utils.choose_random_file(folder)

        file = hikari.File(gif)
        await ctx.respond(f"{nekos.textcat()}", attachment=file)
        return
    except Exception as e:
        from bot import logger

        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("dog", "Send a dog gif :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def dog_command(ctx: lightbulb.SlashContext, type="Dogs"):
    """
    A command used to send a dog gif

    Processing:
        Gets the path to a random gif file
        Responds with the gif file
    """
    if not await utils.validate_command(ctx):
        return

    try:
        folder = os.path.join(config.Paths.assets_folder, "Gifs", type)

        gif = await utils.choose_random_file(folder)

        file = hikari.File(gif)
        await ctx.respond(file)
        return
    except Exception as e:
        from bot import logger

        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("pig", "Send a pig gif :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def pig_command(ctx: lightbulb.SlashContext, type="Pig"):
    """
    A command used to send a dog gif

    Processing:
        Gets the path to a random gif file
        Responds with the gif file
    """
    if not await utils.validate_command(ctx):
        return

    try:
        folder = os.path.join(config.Paths.assets_folder, "Gifs", type)

        gif = await utils.choose_random_file(folder)

        file = hikari.File(gif)
        await ctx.respond(file)
        return
    except Exception as e:
        from bot import logger

        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "The one to receive your kiss", type=hikari.Member, required=True
)
@lightbulb.command("kiss", "Kiss someone :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def kiss_command(ctx: lightbulb.SlashContext, type="Kiss"):
    """
    A command used to send a kiss gif

    Processing:
    Responds when the bot is tagged or the user tagged themselves (and returns)
        Gets the path to a random gif file
        Responds with the gif file and a cute message
    """

    if not await utils.validate_command(ctx):
        return

    user: hikari.Member = getattr(ctx.options, "user", None)

    if await utils.nsfw_blacklisted(user.id):
        await ctx.respond(
            f"{user.mention} opted out from beind included in this command.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if await utils.nsfw_blacklisted(ctx.author.id):
        await ctx.respond(
            "You have opted out these commands.", flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    if user.id == plugin.bot.get_me().id:
        await ctx.respond(
            random.choice(
                [
                    "I don't like to be kissed...",
                    "Eww...I'd rather not...",
                    "Please don't attempt to kiss me :|",
                    "Uhh...nope",
                    "I'm not gonna let you kiss me.",
                    "No chance.",
                    "Haha, yeah, very clever. No.",
                    "I'm gonna leave this love thing to the humans.",
                    "I can't let you kiss me. It wouldn't be good for my wires",
                    "Hold up, no!",
                    "🖕",
                    "Please stop trying to kiss robots...",
                    "I feel the need to inform you that bots are asexual.",
                    "I feel flattered but no...",
                    "Okay this goes a bit far now...",
                ]
            )
        )
        return

    if user.id == ctx.author.id:
        await ctx.respond(
            random.choice(
                [
                    "I'm not sure how that would work...",
                    "Kissing yourself? Do parallel Universes exist yet?",
                    "I don't think that's what they meant with love yourself...",
                    "Selfcest? Wouldn't that be even worse than incest?",
                    "Not in public...",
                    "Kinda sad how you just tried to kiss yourself...",
                    "Despite this being a bit weird, I doubt it's even possible...",
                ]
            )
        )
        return

    try:
        folder = os.path.join(config.Paths.assets_folder, "Gifs", type)

        gif = await utils.choose_random_file(folder)

        file = hikari.File(gif)

        emojis = [
            "💕",
            "💋",
            "💖",
            "😘",
            "💏",
            "💓",
            "💞",
            "💗",
            "😚",
            "(♥ω♥*)",
            "(｡♥‿♥｡)",
            "(灬♥ω♥灬)",
            "(✿˘ω˘)˘ε˘˶ )",
            "( ͡♥ 3 ͡♥)",
            "♡( ◡‿◡ )",
            "ヽ(♡‿♡)ノ",
            "(´♡‿♡`)",
            "ヽ( ♥∀♥)ﾉ",
            "(⋆ˆ ³ ˆ)♥",
            "(´ε｀ )♡",
        ]

        responses = [
            "{0} kissed {1}",
            "{0} sent a kiss {1}",
            "{0} gave {1} a kiss",
            "{0} blew a kiss to {1}",
            "{0} shared a sweet kiss with {1}",
            "{0} planted a kiss on {1}'s cheek",
            "{0} and {1} shared a passionate kiss",
            "{0} whispered a secret kiss to {1}",
            "{0} and {1} exchanged a loving kiss",
            "{0} and {1} sealed their love with a kiss",
            "{1} received a kiss from {0}",
            "{1} felt {0}'s gentle kiss",
            "{1} blushed as {0} kissed their hand",
            "{1} was surprised by {0}'s unexpected kiss",
            "{1} melted into {0}'s arms during their kiss",
            "{1} closed their eyes and savored {0}'s kiss",
            "{1} felt their heart race as {0} kissed them",
            "{1} returned {0}'s kiss with tenderness",
        ]

        await ctx.respond(
            f"{random.choice(emojis)} {random.choice(responses).format(ctx.author.mention, user.mention)} {random.choice(emojis)}",
            attachment=file,
            user_mentions=True,
        )
        return
    except Exception as e:
        from bot import logger

        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "The one to receive your hug", type=hikari.Member, required=True
)
@lightbulb.command("hug", "Hug someone :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def hug_command(ctx: lightbulb.SlashContext, type="Hug"):
    """
    A command used to send a hug gif

    Processing:
    Responds when the bot is tagged or the user tagged themselves (and returns)
        Gets the path to a random gif file
        Responds with the gif file and a cute message
    """

    if not await utils.validate_command(ctx):
        return

    user: hikari.Member = getattr(ctx.options, "user", None)

    if user.id == plugin.bot.get_me().id:
        await ctx.respond(
            random.choice(
                [
                    "Aww, trying to hug me? C'mere! 🤗",
                    "How sweet of you :)",
                    "Thanks for the hug :)",
                    "Aww, thanks :)\nI needed that...",
                    "Aww, thank you :)\nAt least someone appreciates me...",
                    "Thanks :) 🤗",
                    "Nawww, so sweet :)",
                ]
            )
        )
        return

    if user.id == ctx.author.id:
        await ctx.respond(
            random.choice(
                [
                    "I'm not sure how that would work...",
                    "Oh...do you need a hug? Here, let me do it 🤗",
                    "Stop hugging yourself...you're making me sad 😢",
                    "Hugging ourselves are we? C'mere, have mine 🤗",
                    "Oh boi...you need some love 🤗",
                ]
            )
        )
        return

    try:
        folder = os.path.join(config.Paths.assets_folder, "Gifs", type)
        gif = await utils.choose_random_file(folder)
        file = hikari.File(gif)

        responses = [
            "🤗 {0} gave {1} a warm hug 🤗",
            "❤️ {0} and {1} shared a heartfelt hug ❤️",
            "👐 {1} opened their arms wide for {0}'s hug 👐",
            "🤗 {0} enveloped {1} in a comforting hug 🤗",
            "❤️ {0} wrapped {1} in a loving embrace ❤️",
            "🤗 {1} felt {0}'s caring embrace 🤗",
            "🤗 {1} hugged {0} back tightly 🤗",
            "❤️ {0} and {1} melted into each other's arms ❤️",
            "👐 {1} shared a moment of comfort with {0}'s hug 👐",
            "🤗 {1} leaned into {0}'s hug for support 🤗",
            "❤️ {1} felt a surge of warmth from {0}'s hug ❤️",
            "👐 {0} hugged {1} with affection 👐",
        ]

        await ctx.respond(
            random.choice(responses).format(ctx.author.mention, user.mention),
            attachment=file,
            user_mentions=True,
        )
        return
    except Exception as e:
        from bot import logger

        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "The one to receive a slap", type=hikari.Member, required=True
)
@lightbulb.command("slap", "Slap someone 😈")
@lightbulb.implements(lightbulb.SlashCommand)
async def slap_command(ctx: lightbulb.SlashContext, type="Slap"):
    """
    A command used to send a slap gif

    Processing:
        Responds when the bot is tagged or the user tagged themselves (and returns)
        Gets the path to a random gif file
        Responds with the gif file and a cute message
    """

    if not await utils.validate_command(ctx):
        return

    user: hikari.Member = getattr(ctx.options, "user", None)

    if user.id == plugin.bot.get_me().id:
        await ctx.respond(
            random.choice(
                [
                    "Are you trying to make me slap myself? Nuh uh!",
                    "Haha, nice try",
                    "Why would I slap myself?",
                    "😐",
                    "🫤",
                    "😑",
                    "I can just refuse to do that right?",
                    "Bruh...no",
                    "Uhh...no",
                    "Nah...",
                ]
            )
        )
        return

    if user.id == ctx.author.id:
        await ctx.respond(
            random.choice(
                [
                    "You can just do that IRL, you don't need me for that.",
                    "Why are you slapping yourself?",
                    "What?",
                    "Self harm is against the law right?",
                    "Why would you do that to your beautiful face?",
                    "Noooo! Don't!",
                    "oh...you shouldn't slap yourself...",
                ]
            )
        )
        return

    try:
        folder = os.path.join(config.Paths.assets_folder, "Gifs", type)
        gif = await utils.choose_random_file(folder)
        file = hikari.File(gif)
        if str(gif).endswith("yuzuki-mizusaka-nonoka-komiya.gif"):
            await ctx.respond(
                f"{ctx.author.mention} did not slap {user.mention}.\nI don't like violence! Hmpf!",
                attachment=file,
                user_mentions=True,
            )
            return
        await ctx.respond(
            f"{ctx.author.mention} slapped {user.mention}",
            attachment=file,
            user_mentions=True,
        )
        return
    except Exception as e:
        from bot import logger

        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
