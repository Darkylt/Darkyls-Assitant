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

import asyncio
import os

import bot_utils as utils
import buttons
import config_reader as config
import hikari
import image_manager
import lightbulb
import vars
from Worm import worm_simulator

plugin = lightbulb.Plugin("Worm", "Worm matrix")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("worm", "Watch a simulated worm", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def worm_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return

    if vars.worm_is_running:
        await ctx.respond(
            "There's already a simulation running. And I don't have the ressources to simulate it twice, so you'll have to wait."
        )
        return

    vars.worm_is_running = True

    view = buttons.Worm()

    # Get the message object for updating
    message = await ctx.respond("Initializing worm simulator...", components=view)

    # Get text output generator from simulator
    image_generator = worm_simulator.run_worm_simulator()

    embed = hikari.Embed(
        title="Worm simulator",
        description="This is a digital simulation of the brain of the Caenorhabditis elegans worm. In 1963, Sydney Brenner proposed research into C. elegans primarily in neural development. The worm was the first organism to have it's connectome (neuronal 'wiring diagram') completed. This is a simulation of this diagram meaning every neuron and neuron connection is simulated here. (And surprisingly it is only 260 KB)\n\nThe matrix is one step closer.",
    )
    thumbnail = hikari.File(
        os.path.join(config.Paths.assets_folder, "Caenorhabditis elegans.jpg")
    )
    embed.set_thumbnail(thumbnail)
    embed.set_author(
        name="Seth Miller",
        url="https://heyseth.github.io",
        icon="https://avatars.githubusercontent.com/u/8293842",
    )
    await message.edit(
        embed=embed,
        content="",
    )

    # Continuously update the response message
    async for image in image_generator:
        try:
            file = hikari.File(image)
            await message.edit(attachment=file)
            await image_manager.delete(image)
            await asyncio.sleep(2)
        except Exception as e:
            from bot import logger

            logger.error(f"Error in /worm command: {e}")
            await message.edit(
                f"An error occurred!{await utils.error_fun()}", components=[]
            )
            return


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
