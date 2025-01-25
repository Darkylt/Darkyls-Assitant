import re

import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("secret api add account", "Only for admins")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.option(
    "username", "The ID to identify the user by.", type=str, required=True
)
@lightbulb.option(
    "passhprase", "The passphrase they can log on with.", type=str, required=True
)
@lightbulb.option("files", "What files they can access.", type=str, required=True)
@lightbulb.option("active", "Should the account be enabled?", type=bool, default=True)
@lightbulb.command(
    "secret_api_add_account",
    "Add an account to the database.",
    auto_defer=True,
    ephemeral=True,
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def ping_command(
    ctx: lightbulb.SlashContext,
    username: str,
    passphrase: str,
    files: str,
    active: bool,
) -> None:
    if not await utils.validate_command(ctx):
        return

    if ctx.author.id != config.Bot.owner_id:
        await ctx.respond("No. Fuck you.")
        return

    "File2.wav, Fil3.mp3, Fee3.wav"
    "File2.wav"

    file_pattern = r"^([\w\-.]+\.(wav|mp3))(, *[\w\-.]+\.(wav|mp3))*$"

    if not re.fullmatch(file_pattern, files):
        await ctx.respond("Invalid format for 'files'.")
        return


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
