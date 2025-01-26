import os
import random

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

ENABLED = False

plugin = lightbulb.Plugin("Wordle", "Play wordle")

ATTEMPTS = 6


def load_word_list(filename):
    with open(filename, "r") as file:
        words = [line.strip().upper() for line in file.readlines()]
    return words


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "starting_guess",
    "What is your first guess?",
    type=str,
    min_length=5,
    max_length=5,
    required=True,
)
@lightbulb.command(
    "wordle", "Play wordle with the bot.", auto_defer=True, pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def wordle_command(ctx: lightbulb.SlashContext):
    """
    A command used to test the bot.
    It performs some basic checks and then executes the test() function
    """

    if not await utils.validate_command(ctx):
        return

    word_list = load_word_list(
        os.path.join(config.Paths.assets_folder, "Text", "wordle_possible.txt")
    )

    target_word = random.choice(word_list)


def load(bot):
    if ENABLED:
        bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
