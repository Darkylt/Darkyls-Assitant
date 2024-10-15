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

import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("suggest", "Suggest a feature anonymously")


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("suggestion", "The suggestion", type=str)
@lightbulb.command(
    "suggest",
    "Suggest something to the admins anonymously.",
    auto_defer=True,
    ephemeral=True,
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def suggest_command(ctx: lightbulb.SlashContext, suggestion: str) -> None:
    # Don't use validate command function for anonymity

    if ctx.author.is_bot or ctx.author.is_system:
        await ctx.respond("This command can not be executed by other bots.")
        return

    embed = hikari.Embed(
        title="Suggestion",
        description=f"An anonymous suggestion by a server member:\n\n{suggestion}",
        color=hikari.Color.from_rgb(255, 214, 33),
    )

    await plugin.app.rest.create_message(949315761791438939, embed=embed)

    await ctx.respond("Suggestion sent! :)")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
