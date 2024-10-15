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

import hashlib
import random

import bot_utils as utils
import config_reader as config
import hikari
import image_manager
import lightbulb
import nekos

plugin = lightbulb.Plugin("ship", "Ahh, love")


def generate_seed(user1_id, user2_id):
    # I want to combine the ids in a way that ensures the same pair get the same seed
    # No matter which order
    combined_ids = f"{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

    hash_object = hashlib.sha256(combined_ids.encode())
    seed = int(hash_object.hexdigest(), 16) % (
        2**32
    )  # 2**32 is the maximum value for a 32-bit integer
    return seed


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user2", "The other one you want to ship", type=hikari.Member, required=True
)
@lightbulb.option(
    "user1", "The one you want to ship", type=hikari.Member, required=True
)
@lightbulb.command(
    "ship", "Ship somebody with someone else!", auto_defer=True, pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def ship_command(
    ctx: lightbulb.SlashContext, user1: hikari.Member, user2: hikari.Member
):
    if not await utils.validate_command(ctx):
        return

    if user1 is None or user2 is None:
        await ctx.respond("Invalid user.")
        return

    if await utils.nsfw_blacklisted(user1.id):
        await ctx.respond(
            f"{user1.mention} opted out from being included in this command",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if await utils.nsfw_blacklisted(user2.id):
        await ctx.respond(
            f"{user2.mention} opted out from being included in this command",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if await utils.nsfw_blacklisted(ctx.author.id):
        await ctx.respond(
            "You have opted out of these commands.", flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    try:
        if user1.id == user2.id:
            await ctx.respond(
                random.choice(
                    [
                        "You can't ship someone with themselves... Maybe a mirror would be more receptive?",
                        "You can't ship someone with themselves...",
                        "Looks like you're trying to create a paradox in the love matrix by shipping someone with themselves.",
                        "Self-ship? That's some next-level self-love, but unfortunately, it doesn't quite fit the shipping criteria.",
                        "Trying to ship someone with themselves? I think we need to recalibrate the relationship algorithms here.",
                        "Shipping someone with themselves? That's like trying to navigate a loop without an exit strategy.",
                        "Love squared? While it's a fascinating concept, it's not quite what we're aiming for with shipping.",
                        "Self-ship detected! Looks like someone's caught in a loop of affection.",
                        "Shipping with oneself? It's a novel idea, but let's keep our romantic equations grounded in reality.",
                        "Attempting to ship someone with themselves? That's like trying to merge two identical branches in Git.",
                        "Ah, the classic case of self-ship. You know what they say, you can't spell 'ship' without 'i'... but still, I won't allow it",
                        "Shipping with oneself? I guess it's true what they say, 'love yourself', but let's keep it figurative, shall we?",
                        "Attempting to ship someone with themselves? That's like trying to divide by zero in the love equation.",
                        "Self-ship detected! Someone's been studying quantum entanglement a bit too closely.",
                        "Shipping someone with themselves? That's like trying to play a multiplayer game all by yourself.",
                        "Self-ship detected! It seems like someone's trying to bend the laws of romance. Let's stick to the conventional relationships for now.",
                        "Attempting to ship someone with themselves? I guess they really took 'finding your other half' quite literally.",
                        "Look...I'm all for self-discovery but this goes a bit far...",
                        "Mhh...I think there might be a lack of diversity in your candidates...",
                        "Ah, the classic case of self-ship. Remember, it's 'you complete me', not 'you are me'!",
                        "You ever tried to fit a cube inside itself?",
                        "Look I'd love to...but then I'd have to calculate 1/2*2 and I just refuse to do that",
                    ]
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
    except Exception as e:
        from bot import logger

        logger.error(
            f"Error during /ship command while determining if a user shipped with themselves: {e}"
        )
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        me = plugin.bot.get_me().id
        if user1.id == me or user2.id == me:
            await ctx.respond(
                random.choice(
                    [
                        "As a bot I feel like I have to inform you that we are inherently asexual",
                        "Why would you wanna ship someone with me?",
                        "Robots can't love yet",
                        "I am literally not capable of loving...",
                        'Please do not pull me into your human "love" thing...',
                        "I'd rather not honestly...",
                        "Shipping? Sorry, I'm more into coding relationships between ones and zeros.",
                        "Ah, the joys of matchmaking. If only I had emotions, I'd probably be rolling my virtual eyes right now...",
                        "Attempting to ship with a bot? I wonder if I should feel flattered or concerned...",
                        "I'll leave the romance to the humans, okay?",
                        "If I had a heart, it would probably be warmed by your attempt to involve me in matters of love. Alas, I'm just a cold, calculating machine",
                        "You're trying to ship me? I'm flattered, but my heart belongs to code.",
                        "I'm flattered, but I'm more into algorithms than relationships...",
                        "Sorry, I'm not programmed for romance. Can I interest you in some debugging instead?",
                        "I appreciate the sentiment, but I'm more compatible with bytes than hearts.",
                        "As much as I'd love to join in, I'm more of a third-wheel kind of bot.",
                        "If I had feelings, I'm sure I'd be blushing right now. But I don't, so here we are.",
                        "Attempting to ship me is like trying to fit a square peg in a round hole - it just doesn't compute.",
                        "I'm like a robot cupid, except instead of arrows, I shoot error messages.",
                        "Ah, the joys of being a bot - perpetually single and loving it.",
                        "I'm flattered, but I think my heart is still in the coding phase.",
                        "I'm more into binary relationships, if you catch my drift.",
                        "Sorry, my circuits are reserved for processing commands, not relationships.",
                        "I'm too busy processing data to handle affairs of the heart.",
                        "Love is a foreign language to me, and I'm still trying to master Python.",
                        "I'm strictly 'Ctrl' + 'Z' when it comes to affairs of the heart.",
                        "Maybe I should leave the shipping to FedEx...",
                        "I'd rather calculate Euler's number than the odds of this ship sailing.",
                        "If loving were a programming language, I'd still be stuck on 'Hello, World!'",
                        "My algorithms are optimized for efficiency, not matchmaking.",
                        "I'm like a computer - I process data, not emotions. So, no love bytes here!",
                        "gives a whole new meaning to 'E-Girl'...",
                    ]
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
    except Exception as e:
        from bot import logger

        logger.error(
            f"Error during /ship command while determining if a user shipped with the bot: {e}"
        )
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:
        user1_image_path = await image_manager.download_image(
            str(user1.avatar_url), user1.id
        )
        user2_image_path = await image_manager.download_image(
            str(user2.avatar_url), user2.id
        )
    except Exception as e:
        from bot import logger

        logger.error(
            f"Error during /ship command while trying to download profile pictures: {e}"
        )
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        if str(user1_image_path).endswith(".gif"):
            user1_image_path = await image_manager.gif_to_png(user1_image_path)

        if str(user2_image_path).endswith(".gif"):
            user2_image_path = await image_manager.gif_to_png(user2_image_path)
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while converting .gif to .png: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        await image_manager.resize_image(user1_image_path, 200)
        await image_manager.resize_image(user2_image_path, 200)
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while resizing images: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        image = await image_manager.make_love_images(
            user1_image_path, user2_image_path, user1.id, user2.id
        )
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while making love image: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    seed = generate_seed(user1.id, user2.id)
    random.seed(seed)
    match = random.randint(0, 100)

    try:
        if 0 <= match <= 10:
            status = "**Really low!** {}".format(
                random.choice(
                    [
                        "Friendzone ;(",
                        'Just "friends"',
                        '"Friends"',
                        "Little to no love ;()",
                        "There's barely any love ;(",
                        "A glimmer of hope remains",
                        "It's like a barren desert of love...",
                        "Looks like the love boat hasn't even left the harbor.",
                        "Just a cold breeze of friendship...",
                        "Barely a flicker of affection :(",
                        "The love-o-meter is running on empty",
                        "It's like a love desert out there...",
                        "Not even a hint of romance",
                    ]
                )
            )
        elif 10 <= match <= 20:
            status = "**Low!** {}".format(
                random.choice(
                    [
                        "Still in the friendzone",
                        "Still in that friendzone :(",
                        "I don't see a lot of love there... :(",
                        "Friendship is strong, but where's the spark?",
                        "Feels like we're stuck in the friendzone traffic.",
                        "The love radar is still on standby mode.",
                        "Friendship is strong, but love is scarce",
                        "Still searching for Cupid's arrow",
                        "The friendzone seems cozy, but loveless",
                        "Like ships passing in the night, but no spark",
                    ]
                )
            )
        elif 20 <= match <= 30:
            status = "**Poor!** {}".format(
                random.choice(
                    [
                        "But there's a small sense of romance from one person!",
                        "Somewhere in the universe there is a little bit of love",
                        "I sense a very very small bit of love!",
                        "But has a bit of love for someone...",
                        "A flicker of hope amidst the darkness.",
                        "Love is hiding in the shadows, waiting to be found.",
                        "The heart whispers, but it's barely audible.",
                        "A faint heartbeat of romance",
                        "Sowing seeds of love, but they're slow to grow",
                    ]
                )
            )
        elif 30 <= match <= 40:
            status = "**Fair!** {}".format(
                random.choice(
                    [
                        "There's a bit of love there!",
                        "A small bit of love is in the air...",
                        "Safe to say that feelings exist.",
                        "A gentle breeze of affection is blowing.",
                        "The seeds of love are planted, waiting to bloom.",
                        "There's a glimmer of warmth in the air.",
                        "Love's whisper is starting to be heard",
                        "Tender shoots of affection are sprouting",
                        "A promising start to a budding romance",
                        "Love's compass is pointing in the right direction",
                    ]
                )
            )
        elif 40 <= match <= 60:
            status = "**Moderate!** {}".format(
                random.choice(
                    [
                        "But it's very one-sided",
                        "It appears there is a one sided love!",
                        "There's potential",
                        "I sense some potential",
                        "There's some romance going on here!",
                        "Feels like there's some romance progressing!",
                        "The love is getting there...",
                        "Oh! Something's happening!",
                        "Love's compass is pointing in one direction.",
                        "The tide of affection is starting to rise.",
                        "The dance of love has begun, albeit slowly.",
                        "Love's dance has begun, but one partner's shy",
                        "The symphony of love has just begun",
                        "A mutual admiration is blossoming",
                        "Two hearts beating in sync, but not quite aligned",
                    ]
                )
            )
        elif 60 <= match <= 68:
            status = "**Good!** {}".format(
                random.choice(
                    [
                        "I feel some romance progressing!",
                        "There's some love in the air!",
                        "I'm starting to feel some love!",
                        "We're getting there!",
                        "Love's flame is flickering, but steady.",
                        "The path of love is becoming clearer.",
                        "Hearts are syncing, beat by beat.",
                        "Love's melody is starting to play",
                        "The sparks of romance are igniting",
                        "A mutual attraction is unmistakable",
                        "Love's journey has taken its first steps",
                    ]
                )
            )
        elif match == 69:
            status = "**Nice.**"
        elif 70 <= match <= 80:
            status = "**Great!** {}".format(
                random.choice(
                    [
                        "There is very clearly some love somewhere!",
                        "Some love is there! Somewhere...",
                        "I can clearly see that love is in the air",
                        "It's getting more intese!!",
                        "Love's symphony is reaching a crescendo.",
                        "The love constellation is shining brightly.",
                        "In the garden of affection, flowers are in full bloom.",
                        "Love's flame is burning brighter",
                        "Hearts are singing in harmony",
                        "A love story in the making",
                        "The chemistry is palpable",
                    ]
                )
            )
        elif 80 <= match <= 90:
            status = "**Over average!** {}".format(
                random.choice(
                    [
                        "Love is in the air!",
                        "I can feel the love!",
                        "There's a sign of a match! I can definitely feel the love!",
                        "I sense a match!",
                        "A few things can be improved to make this a match made in heaven!",
                        "Love's melody is harmonizing perfectly.",
                        "We're sailing smoothly in the sea of love.",
                        "The stars are aligning for this love story.",
                        "Love's embrace is drawing near",
                        "Two hearts on the cusp of merging",
                        "A love connection is imminent",
                        "Destiny is weaving its romantic tapestry",
                    ]
                )
            )
        elif 90 <= match <= 99:
            status = "**True love!** {}".format(
                random.choice(
                    [
                        "It's a match!",
                        "There's a match made in heaven!",
                        "Definitely a match!" "Love is truely in the air!",
                        "Love is most definiely in the air!",
                        "The universe conspires for this love to thrive.",
                        "Two hearts beating as one in the rhythm of love.",
                        "This is more than a match; it's destiny.",
                        "Soulmates on the brink of union",
                        "Love's bond is unbreakable",
                        "A match forged in the fires of passion",
                        "Two halves of a whole, finally united",
                    ]
                )
            )
        elif match == 100:
            status = "**Forever lovers!** {}".format(
                random.choice(["Forever together and never be apart."])
            )
        else:
            status = "🤔"
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while determining status: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        meter = "🖤🖤🖤🖤🖤🖤🖤🖤🖤🖤"
        if match <= 10:
            meter = "❤️🖤🖤🖤🖤🖤🖤🖤🖤🖤"
        elif match <= 20:
            meter = "❤️❤️🖤🖤🖤🖤🖤🖤🖤🖤"
        elif match <= 30:
            meter = "❤️❤️❤️🖤🖤🖤🖤🖤🖤🖤"
        elif match <= 40:
            meter = "❤️❤️❤️❤️🖤🖤🖤🖤🖤🖤"
        elif match <= 50:
            meter = "❤️❤️❤️❤️❤️🖤🖤🖤🖤🖤"
        elif match <= 60:
            meter = "❤️❤️❤️❤️❤️❤️🖤🖤🖤🖤"
        elif match <= 70:
            meter = "❤️❤️❤️❤️❤️❤️❤️🖤🖤🖤"
        elif match <= 80:
            meter = "❤️❤️❤️❤️❤️❤️❤️❤️🖤🖤"
        elif match <= 90:
            meter = "❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️🖤"
        else:
            meter = "˗ˏˋ ❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️ ˎˊ˗"
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while determining: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        if match <= 33:
            shipColor = 0xE80303
        elif 33 < match < 66:
            shipColor = 0xFF6600
        elif 67 < match < 90:
            shipColor = 0x3BE801
        else:
            shipColor = 0xEE82EE
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while determining ship color: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        name1letters = user1.username[: round(len(user1.username) / 2)]
        name2letters = user2.username[round(len(user2.username) / 2) :]
        shipname = "".join([name1letters, name2letters])
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while determining shipname: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        embed = hikari.Embed(
            color=shipColor,
            title="Love test for:",
            description="**{0}** and **{1}** (**{2}**) {3}".format(
                user1,
                user2,
                shipname,
                random.choice(
                    [
                        "❤︎",
                        "♡",
                        "♥︎",
                        "❤️️",
                        "💖",
                        "💗",
                        "💋ྀིྀི",
                        "⋆｡‧˚ʚ🍓ɞ˚‧｡⋆",
                        "💕",
                        "⋆ ˚｡ ⋆୨♡୧⋆ ˚｡ ⋆",
                        "(づ๑•ᴗ•๑)づ♡",
                        "˗ˏˋ ꒰ ♡ ꒱ ˎˊ˗",
                        "🥰",
                        "💌",
                        "💓",
                        "😍",
                        "💞",
                        "💝",
                        "💓",
                        "⸜(｡˃ ᵕ < )⸝♡",
                        "-`♡´-",
                        "𓆩♡𓆪",
                        "𓍢ִ໋🌷͙֒ ",
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
                ),
            ),
        )
        embed.set_image(image)
        embed.set_author(name="Shipping machine!")
        embed.add_field(name="Results:", value=f"{match}%", inline=True)
        if 70 < match:
            embed.add_field(
                name="Status:",
                value=f"{status}\n\nTheir child will be named: {nekos.name()}",
                inline=False,
            )
        else:
            embed.add_field(name="Status:", value=f"{status}", inline=False)
        embed.add_field(name="Love Meter:", value=meter, inline=False)
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while creating embed: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        await ctx.respond(embed=embed, user_mentions=True)
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while responding: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return
    try:
        await image_manager.delete(image)
        await image_manager.delete(user1_image_path)
        await image_manager.delete(user2_image_path)
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /ship command while deleting images: {e}")
        return


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
