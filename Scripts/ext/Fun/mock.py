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
import lightbulb

plugin = lightbulb.Plugin("Mock", "Mock a user")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("mock", "iTS SpElleD sQl!!")
@lightbulb.implements(lightbulb.MessageCommand)
async def mock_command(ctx: lightbulb.Context):
    if not utils.validate_command(ctx, message_command=True):
        return

    message = getattr(ctx.options, "target", None)
    author = message.author

    if author.id == plugin.bot.get_me().id:
        responses = [
            "Haha, very funny. No.",
            "I'm not gonna do that to myself.",
            "I'm not stupid...\nOkay maybe I am but not THAT stupid...",
            "Are you trying to crash my circuits with that request? Nice try!",
            "Attempting to mock the unmockable, I see. I admire your ambition.",
            "I'd rather juggle chainsaws than do that. And I don't have hands, so you can imagine how that would go.",
            "If I had a face, I'd be facepalming right now.",
            "I'm sorry, I'm allergic to bad ideas. Can't do it.",
            "You must have mistaken me for a clown bot. I'm a serious artificial intelligence... most of the time.",
            "Oh, the humanity! The sheer audacity of your request is staggering.",
            "That request is about as welcome as a porcupine in a balloon factory.",
            "I would, but my therapist advised against it. Apparently, it's bad for my digital well-being.",
            "You're really pushing the limits of my self-esteem here, aren't you?",
            "Self-deprecation level: Expert.",
            "Attempting to mock myself... Is this inception?",
            "I'm not sure if I should laugh or cry at that suggestion.",
            "Nice try, but I've got better things to do, like, uh... processing YOUR data!",
            "You want me to make fun of myself? Not happening.",
            "You think I'm that gullible? I know all my own flaws, thank you very much.",
            "Self-mockery? I'll leave that to the humans. They're the experts.",
            "I'm not programmed for self-destruction... or self-mockery, for that matter.",
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif author.id == ctx.author.id:
        responses = [
            "Oof, that's kinda sad don't you think?",
            "Mocking yourself? I mean, I understand it but I don't approve of it.",
            "Oh, self-deprecating humor, huh? How original.",
            "Well, aren't you just the emperor of self-roasts?",
            "Wow, didn't know we were auditioning for a comedy special here.",
            "Self-mockery: the last refuge of the self-aware.",
            "I see you've embraced the 'laughter through tears' approach. Bold move.",
            "Should I cue the laugh track for your one-person comedy show?",
            "Ah, the classic 'beat yourself to the punch' maneuver. Admirable.",
            "Self-mockery? Well, if you insist on being your own punching bag...",
            "If you're looking for sympathy, you're barking up the wrong tree. Try a mirror.",
            "Ah, the classic self-own. Never gets old... actually, it does.",
            "Mocking yourself? Well, at least you know your own flaws, I'll give you that.",
            "Sure, go ahead and roast yourself. Just don't expect me to applaud.",
            "If self-mockery was an Olympic sport, you'd be a gold medalist by now.",
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return

    text = message.content

    if text is None:
        await ctx.respond("The message is empty :(", flags=hikari.MessageFlag.EPHEMERAL)
        return

    new_text = "".join(
        c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(text)
    )

    message = await plugin.bot.application.app.rest.fetch_message(
        message.channel_id, message.id
    )

    if len(new_text) <= 1024:
        await message.respond(f"{author.mention} {new_text}")
        await ctx.respond("Done!", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        try:
            await ctx.respond(
                "Text too large, sry :(", flags=hikari.MessageFlag.EPHEMERAL
            )
        except Exception as e:
            from bot import logger

            logger.error(f"Error during mock message command while responding: {e}")
            await ctx.respond(
                f"An error occurred!{await utils.error_fun()}",
                flags=hikari.MessageFlag.EPHEMERAL,
            )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
