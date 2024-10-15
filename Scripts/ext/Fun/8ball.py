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

plugin = lightbulb.Plugin("8Ball", "The all mighty 8Ball!")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("question", "The question you want to ask", type=str, required=True)
@lightbulb.command("8ball", "Ask a question to the 8Ball!", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def eightball_command(ctx: lightbulb.SlashContext, question: str):
    if not await utils.validate_command(ctx):
        return

    answers = {
        "psgood": [
            "Yes",
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes - definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Signs point to yes",
            "Count on it",
            "May be",
            "You're hot",
            "Absolutely",
            "Wait for it",
        ],
        "psbad": [
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
            "No",
            "It will pass",
            "Ask again",
            "Absolutely not",
            "I don't think so",
            "Absolutely not",
            "You may not like it",
            "The world may end because of it",
            "The newspaper will spread lies about you because of it",
            "You're hot.",
        ],
    }

    choices = random.choice(random.choice(list(answers.values())))
    if choices in answers["psbad"]:
        color = hikari.Color(0xFF0000)
    else:
        color = hikari.Color(0x26D934)
    eightball = hikari.Embed(color=color)
    eightball.add_field(name="Question:", value=question.capitalize())
    eightball.add_field(name="Anser:", value=f"{choices}")
    eightball.set_author(name="The all knowing 8-Ball")
    eightball.set_footer(
        f"Requested by: {ctx.author.username}", icon=ctx.author.avatar_url
    )
    eightball.set_thumbnail("https://c.tenor.com/43PtWN4D5E8AAAAC/tenor.gif")
    await ctx.respond(embed=eightball, user_mentions=True)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
