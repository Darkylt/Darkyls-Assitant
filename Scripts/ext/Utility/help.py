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

import bot_utils as utils
import buttons
import config_reader as config
import hikari
import lightbulb
import miru

plugin = lightbulb.Plugin("Help", "Get help with the bot.")

help_options = [
    "All Commands",
    "Fun Commands",
    "Utility Commands",
    "Terms of Service",
    "Privacy",
    "Confessions",
]


async def get_help_message(category: str, ctx) -> hikari.Embed:

    color = hikari.Color.from_hex_code("#5e03fc")

    thumbnail = os.path.join(config.Paths.assets_folder, "pfp.png")

    if category is None:

        message = config.HelpMessage.message
        lines = message.split("\n")
        title = lines[0] if lines else ""
        message_without_title = "\n".join(lines[1:]) if len(lines) > 1 else ""
        embed = hikari.Embed(
            title=title, description=message_without_title, color=color
        )
        embed.set_thumbnail(thumbnail)
        roles = ctx.member.role_ids
        all_commands = config.HelpMessage.message_all
        if config.Bot.admin_role in roles or config.Bot.mod_role in roles:
            all_commands += f"\n{config.HelpMessage.message_all_admin}"
        # embed.add_field(name="Here's a list of all the commands I have:", value=all_commands)

    elif category == "All Commands":

        message = config.HelpMessage.message_all
        roles = ctx.member.role_ids
        if config.Bot.admin_role in roles or config.Bot.mod_role in roles:
            message += f"\n{config.HelpMessage.message_all_admin}"
        embed = hikari.Embed(
            title="A list of all my commands:", description=message, color=color
        )
        embed.set_thumbnail(thumbnail)

    elif category == "Fun Commands":

        message = config.HelpMessage.message_fun
        lines = message.split("\n")
        title = lines[0] if lines else ""
        message_without_title = "\n".join(lines[1:]) if len(lines) > 1 else ""
        embed = hikari.Embed(
            title=title, description=message_without_title, color=color
        )
        embed.set_thumbnail(thumbnail)

    elif category == "Utility Commands":

        message = config.HelpMessage.message_utility
        lines = message.split("\n")
        title = lines[0] if lines else ""
        message_without_title = "\n".join(lines[1:]) if len(lines) > 1 else ""
        embed = hikari.Embed(
            title=title, description=message_without_title, color=color
        )
        embed.set_thumbnail(thumbnail)

    elif category == "Privacy":

        message = config.HelpMessage.message_privacy
        lines = message.split("\n")
        title = lines[0] if lines else ""
        message_without_title = "\n".join(lines[1:]) if len(lines) > 1 else ""
        embed = hikari.Embed(
            title=title, description=message_without_title, color=color
        )
        embed.set_thumbnail(thumbnail)

    elif category == "Confessions":
        message = config.HelpMessage.message_confessions
        lines = message.split("\n")
        title = lines[0] if lines else ""
        message_without_title = "\n".join(lines[1:]) if len(lines) > 1 else ""
        embed = hikari.Embed(
            title=title, description=message_without_title, color=color
        )
        embed.set_thumbnail(thumbnail)

    elif category == "Terms of Service":
        message = config.HelpMessage.tos
        lines = message.split("\n")
        title = lines[0] if lines else ""
        message_without_title = "\n".join(lines[1:]) if len(lines) > 1 else ""
        embed = hikari.Embed(
            title=title, description=message_without_title, color=color
        )
        embed.set_thumbnail(thumbnail)

    return embed


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "category",
    "Which category of commands are you interested in?",
    required=False,
    choices=help_options,
)
@lightbulb.command("help", "Get help with the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def help_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return

    try:
        category = ctx.options.category

        embed = await get_help_message(category, ctx)

        if category is None:

            view = buttons.HelpMenu()
            await ctx.respond(
                embed=embed, flags=hikari.MessageFlag.EPHEMERAL, components=view
            )

        else:

            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        from bot import logger

        logger.error(f"Error during /help command: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
