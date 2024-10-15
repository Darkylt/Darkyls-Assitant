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

import json
import os

import bot_utils as utils
import buttons
import config_reader as config
import database_interaction
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("Report", "Allows users to report members")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "The user that is to be reported", type=hikari.Member, required=True
)
@lightbulb.option("reason", "Why are you reporting this user?", type=str, required=True)
@lightbulb.command("report", "Report a user to the mods.")
@lightbulb.implements(lightbulb.SlashCommand)
async def report_command(ctx: lightbulb.SlashCommand):
    """
    A command used to report a user.

    Processing:
        Fetches provided info
        Checks if the info is valid
        Creates the report card embed
        Sends to the reports channel with the buttons
        Responds
        Adds the new report to the database of reports
    """
    if not await utils.validate_command(ctx, report=True, extra_xp=10):
        return
    try:
        reason = getattr(ctx.options, "reason", None)
        user = getattr(ctx.options, "user", None)

        if user.id == ctx.author.id:
            await ctx.respond(
                embed=hikari.Embed(
                    title="❌ Huh?",
                    description="I'm confused...are you self reporting?",
                    color=hikari.Color.from_hex_code("#fc0000"),
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
        elif user.is_bot or user.is_system:
            await ctx.respond(
                embed=hikari.Embed(
                    title="❌ Huh?",
                    description="I'm confused...you can't report bots...",
                    color=hikari.Color.from_hex_code("#fc0000"),
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        report_embed = hikari.Embed(
            title="**Report**",
            description=f"{ctx.member.mention} has reported {user.mention}.",
            color=hikari.Color.from_hex_code("#fc0000"),
        )
        report_embed.set_thumbnail(user.make_avatar_url())
        report_embed.add_field(
            "**Reported User:**", value=f"{user.mention} `({user.id})`"
        )
        report_embed.add_field("**Reason:**", value=reason)

        view = buttons.Report()

        message = await plugin.bot.application.app.rest.create_message(
            channel=config.Bot.report_channel, embed=report_embed, components=view
        )

        await ctx.respond(
            "User has been reported. Your report will be reviewed by a moderator as soon as possible.\nThank you for your service 🫡",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

        database_path = os.path.join(
            config.Paths.data_folder, "Database", "reports.json"
        )
        report_data = {}

        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    report_data = json.load(file)
                except json.JSONDecodeError:
                    pass

        user_id = str(user.id)
        if user_id not in report_data:
            report_data[user_id] = {"reasons": {}}

        report_data[user_id]["reasons"][reason] = {
            "reporter": str(ctx.author.id),
            "report_message": message.id,
        }

        with open(database_path, "w") as file:
            json.dump(report_data, file, indent=4)

        database_interaction.Users.update_user_entry(
            user_id, increment=True, been_reported=1
        )

    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while reporting: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
