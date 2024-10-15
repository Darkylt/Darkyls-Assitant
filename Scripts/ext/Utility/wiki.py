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

import aiohttp
import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Wiki", "Search Wikipedia for articles!")


@plugin.command
@lightbulb.option("query", "The query you want to search for on Wikipedia.")
@lightbulb.command(
    "wiki",
    "Search Wikipedia for articles!",
    auto_defer=True,
    pass_options=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def wiki(ctx: lightbulb.SlashContext, query: str) -> None:
    if not await utils.validate_command(ctx):
        return

    link = "https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=5"

    async with aiohttp.ClientSession() as session:
        async with session.get(link.format(query=query)) as response:
            results = await response.json()
            results_text = results[1]
            results_link = results[3]

            if results_text:
                desc = "\n".join(
                    [
                        f"[{result}]({results_link[i]})"
                        for i, result in enumerate(results_text)
                    ]
                )
                embed = hikari.Embed(
                    title=f"Wikipedia entries for: {query}",
                    description=desc,
                    color=0xC2C2C2,
                )
                # Switch to storing the image as a file if it becomes too annoying
                embed.set_thumbnail(
                    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAAM1BMVEUAAAD+/v41NTUBAQEAAABZWVknJycWFhaZmZmIiIjp6ellZWXMzMzX19eurq54eHhHR0dExXFyAAAAAXRSTlMAQObYZgAAAPtJREFUeAG8kAWOBDAMA9d1Sin+/7XXbpZZdBaURlMrhx28ycGCD/n0bvkBwJf8C+AoIvRAWGtMyHGtCWkfxW+DRopuuIjUtTQJDStevNoXWaRjRSllLd1O8FFhgEZx2BmkAmHC8HwpOUyxSA50VqOjXgAl50URvNWPBRcAnmwnhbcduthqQCO9KYTFBG7eDWoK1T47AZX9DuiUYT/TuhX3MGpnD51kPprSA9Dl+BCKl7jWHHEHmHsLWhNZZMxPQCLTEuy+cYF6D9i8Q5e2Lcyz4AGwKdJbX0p7AegC2qnvxAsAxQRAYH8J6Dg1a/lvpKRJinMW4cxLMPsDAJjSCaG8cPmnAAAAAElFTkSuQmCC"
                )
            else:
                embed = hikari.Embed(
                    title="❌ No results",
                    description="Could not find anything related to your query. :(",
                    color=0xFF0000,
                )
            await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
