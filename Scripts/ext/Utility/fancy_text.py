# Copyright (C) 2025  Darkyl

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

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("Fancy Text", "Convert text to fancy text")

plain_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

fancy_letters = "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷"
fancy_dict = {fancy: plain for fancy, plain in zip(fancy_letters, plain_letters)}
plain_to_fancy = {plain: fancy for plain, fancy in zip(plain_letters, fancy_letters)}

bold_fancy_letters = "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟"
bold_fancy_dict = {
    fancy: plain for fancy, plain in zip(bold_fancy_letters, plain_letters)
}
plain_to_bold_fancy = {
    plain: fancy for plain, fancy in zip(plain_letters, bold_fancy_letters)
}


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("text", "The text to fancify", str, required=True)
@lightbulb.option("bold", "Would you like your text bold?", bool, required=True)
@lightbulb.command(
    "converter_fancy_text",
    "Convert text to fancy text",
    pass_options=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_fancy_text_command(
    ctx: lightbulb.SlashContext, text: str, bold: bool
):
    if not await utils.validate_command(ctx):
        return

    # Choose the right mapping
    mapping = plain_to_bold_fancy if bold else plain_to_fancy

    # Convert the text
    converted = "".join(mapping.get(c, c) for c in text)

    embed = hikari.Embed(
        title="Here is your fancy text!", description=f"```{converted}```"
    )

    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
