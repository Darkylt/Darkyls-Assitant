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
import hikari
import image_manager
import lightbulb

plugin = lightbulb.Plugin("Confess", "Confess anonymously")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("text", "Your confession", str, required=True)
@lightbulb.option(
    "image",
    "An image to attach",
    hikari.OptionType.ATTACHMENT,
    required=False,
    default=None,
)
@lightbulb.command("confess", "Confess anonysmously", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def confess_command(ctx: lightbulb.SlashContext, text: str, image: hikari.File):
    if ctx.author.is_bot or ctx.author.is_system:
        await ctx.respond(
            "This command can not be executed by other bots.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    id = await utils.generate_id()

    image_path = None

    if image:
        supported_formats = ["jpg", "jpeg", "JPG", "JPEG", "png", "PNG", "gif", "gifv"]

        filetype = str(image.filename).split(".")[-1]

        if not filetype in supported_formats:
            txt = ""
            for format in supported_formats:
                txt += f"\n.{format}"

            await ctx.respond(
                f"Discord only supports the following filetypes:{txt}",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        image_path = await image_manager.download_image(
            image.url, id, os.path.join(config.Paths.data_folder, "Downloaded Content")
        )

        if image_path is None:
            await ctx.respond(
                "There was an error while attempting to download your image. Maybe it's in the wrong file format?",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

    if not id:
        await ctx.respond(
            f"An error occurred. {await utils.error_fun}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    embed = hikari.Embed(
        title=f"Confession {id}",
        description=text,
        color=hikari.Color.from_hex_code("#36ff6b"),
    )

    if image:
        embed.set_image(image)

    embed.set_author(name="An anonymous confession")

    view = buttons.Confess()

    message = await plugin.app.rest.create_message(
        channel=config.Channels.confession_approving_channel,
        embed=embed,
        components=view,
    )

    db_path = os.path.join(config.Paths.data_folder, "Database", "confessions.json")

    if os.path.exists(db_path):
        try:
            with open(db_path, "r") as file:
                confessions = json.load(file)
        except json.JSONDecodeError:
            confessions = {}
    else:
        confessions = {}

    if image_path is None:
        image_path = "None"

    confessions[id] = [text, message.id, str(image_path)]

    with open(db_path, "w") as file:
        json.dump(confessions, file, indent=4)

    await ctx.respond(
        f"Your confession has been submitted with the ID *{id}*. A moderator will either approve or deny the confession. This may take a little time.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
