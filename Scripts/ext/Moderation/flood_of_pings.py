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
import random

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Flood of Pings", "You're so doomed")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.option(
    "amount",
    "The amount of pings",
    type=int,
    required=False,
    default=5,
    min_value=1,
    max_value=200,
)
@lightbulb.option("user", "The target user", hikari.Member, required=True)
@lightbulb.command(
    "flood_of_pings", "Ping specified user number of times", pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def flood_of_pings(
    ctx: lightbulb.SlashContext, amount: int, user: hikari.Member
) -> None:
    if not await utils.validate_command(ctx):
        return

    if ctx.author.id != config.Bot.owner_id:
        await ctx.respond("No, you can't.", flags=hikari.MessageFlag.EPHEMERAL)

    if user.id == plugin.bot.get_me().id:
        resp = [
            "Using my own weapons against me huh?",
            "Nope",
            "Not a chance",
            "If you're trying to get me to notice you then here you go.",
        ]

        await ctx.respond(random.choice(resp), flags=hikari.MessageFlag.EPHEMERAL)
        return

    image = hikari.File(os.path.join(config.Paths.assets_folder, "Ping Flood.png"))

    embed_1 = hikari.Embed(
        title="Preparing for the flood of pings",
        description="**⚠️FLOOD OF PINGS IMMINENT⚠️**\n\nPlease evacuate the Area. Women and Children first!\n\nFlooding in 3 Seconds!",
        color=hikari.Color.from_rgb(255, 0, 0),
    )
    embed_1.set_image(image)

    embed_2 = hikari.Embed(
        title="Begin!",
        description="Beginning flood of pings!",
        color=hikari.Color.from_rgb(255, 0, 0),
    )
    embed_2.set_image(image)

    embed_3 = hikari.Embed(
        title="Finished",
        description="The flood of pings is over.",
        color=hikari.Color.from_rgb(60, 255, 0),
    )

    msg = await ctx.respond(embeds=[embed_1])
    await asyncio.sleep(3)
    await msg.edit(embeds=[embed_2])

    ping_count = 0
    for i in range(amount):
        await ctx.respond(
            f"{user.mention} - {ping_count + 1}/{amount}",
            delete_after=30,
            user_mentions=True,
        )
        ping_count += 1
        await asyncio.sleep(1)

    await msg.delete()

    await ctx.respond(embed=embed_3, delete_after=30)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
