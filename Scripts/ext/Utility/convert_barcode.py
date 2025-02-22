import base64
import io

import barcode
import hikari
import lightbulb
from barcode.writer import ImageWriter

plugin = lightbulb.Plugin("Converter Barcode", "Convert text to barcode image")


def generate_barcode(value: str) -> io.BytesIO:
    """Generates a barcode image from the given value."""
    barcode_class = barcode.get_barcode_class("code128")  # Use Code 128 format
    barcode_instance = barcode_class(value, writer=ImageWriter())
    output = io.BytesIO()
    barcode_instance.write(output)
    output.seek(0)
    return output


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("value", "The value to encode as a barcode", str, required=True)
@lightbulb.command(
    "converter_barcode",
    "Convert text to a barcode image",
    pass_options=True,
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_barcode_command(ctx: lightbulb.SlashContext, value: str) -> None:
    barcode_image = generate_barcode(value)
    file = hikari.Bytes(barcode_image.getvalue(), "barcode.png")
    await ctx.respond("Here is your barcode:", attachment=file)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
