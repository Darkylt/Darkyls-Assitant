import json
import os

import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("Warn", "Warn a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option("user", "The user that should be warned", type=hikari.OptionType.USER)
@lightbulb.option("reason", "Warning", type=str)
@lightbulb.command("warn", "Warn a member", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def warn_command(
    ctx: lightbulb.SlashContext, user: hikari.OptionType.USER, reason: str
):
    """
    A command to warn a user.

    It processes the provided info and then warns the user.

    Processing:
        Retrieve provided information
        Fetch the user
        Read the existing warnings
        Add the new reason
        Update the file
        Check if the user is to be banned or kicked
        Perform these actions, respond with success if not
    """
    try:
        # Load existing data from the JSON file if it exists and is not empty
        database_path = os.path.join(
            config.Paths.data_folder, "Database", "warnings.json"
        )
        data = {}

        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                data = json.load(file)

        user_id = str(user.id)

        if user_id in data:
            data[user_id].append(reason)
        else:
            data[user_id] = [reason]

        with open(database_path, "w") as file:
            json.dump(data, file, indent=4)

        warnings_count = len(data.get(user_id, []))

        if 2 < warnings_count < 4:
            await plugin.bot.rest.kick_user(
                ctx.guild_id, user_id, reason="Too many warnings."
            )
            await ctx.respond(
                f"Warned <@{user_id}> for '{reason}'.\n\n(User was kicked for too many warnings)",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        elif warnings_count >= 4:
            await plugin.bot.rest.ban_user(
                ctx.guild_id, user_id, reason="Too many warnings."
            )
            await ctx.respond(
                f"Warned <@{user_id}> for '{reason}'.\n\n(User was banned for too many warnings)",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        else:
            await ctx.respond(
                f"Warned <@{user_id}> for '{reason}'.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while warning a user: {e}")
        await ctx.respond(
            f"An error occurred! {await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option(
    "user", "The user that should have their warning cleared", type=hikari.Member
)
@lightbulb.command("clear_warnings", "Remove all warnings of someone")
@lightbulb.implements(lightbulb.SlashCommand)
async def clear_warnings_command(ctx: lightbulb.SlashContext):
    """
    A command to clear all warnings of a user.

    Processing:
        It fetches the provided user
        Reads the existing entries
        Deletes all warnings
        Writes the updated file
        Responds
    """

    if not await utils.validate_command(ctx):
        return

    try:
        provided_user = getattr(ctx.options, "user", None)

        user = await plugin.bot.application.app.rest.fetch_user(provided_user)

        user_id = str(user.id)

        database_path = os.path.join(
            config.Paths.data_folder, "Database", "warnings.json"
        )
        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        if user_id in data:
            del data[user_id]
        else:
            await ctx.respond(
                f"{user.mention} has no warnings.", flags=hikari.MessageFlag.EPHEMERAL
            )
            return

        with open(database_path, "w") as file:
            json.dump(data, file, indent=4)

        await ctx.respond(
            f"Successfully removed all warnings for {user.username}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        from bot import Logging

        await Logging.log_message(
            f"User <@{user_id}> has had all their warnings removed."
        )
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while clearing warnings: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option("user", "The user that should have their warning cleared", type=int)
@lightbulb.command(
    "clear_warnings_by_id", "Remove all warnings of someone with their ID"
)
@lightbulb.implements(lightbulb.SlashCommand)
async def clear_warnings_command(ctx: lightbulb.SlashContext):
    """
    A command to clear all warnings of a user.

    Processing:
        It fetches the provided user
        Reads the existing entries
        Deletes all warnings
        Writes the updated file
        Responds
    """

    if not await utils.validate_command(ctx):
        return

    user_id = str(getattr(ctx.options, "user", None))

    try:

        database_path = os.path.join(
            config.Paths.data_folder, "Database", "warnings.json"
        )
        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        if user_id in data:
            del data[user_id]
        else:
            await ctx.respond(
                f"The user '{user_id}' has no warnings.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        with open(database_path, "w") as file:
            json.dump(data, file, indent=4)

        await ctx.respond(
            f"Successfully removed all warnings for '{user_id}'",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        from bot import Logging

        await Logging.log_message(
            f"User <@{user_id}> has had all their warnings removed."
        )
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while clearing warnings: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
