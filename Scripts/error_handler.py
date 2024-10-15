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

import datetime

import hikari
import hikari.errors
import lightbulb
from bot_utils import technobabble

error_message = {
    "CommandNotFound": "`{}` is an invalid command!",
    "MissingPermissions": "You dont have `{}` permission to run that command!",
    "MissingRequiredArgument": "You are missing required arguments: `{}`, Please refer to the help menu for more information.",
    "CommandOnCooldown": "That command is on cooldown. Please try again after `{}` seconds.",
    "BotMissingPermissions": "I don't have required permission `{}` to complete that command.",
    "NotOwner": "You are not my owner!",
    "ConversionError": "Converter failed for `{}`.",
    "NoPrivateMessage": "This command cannot be used in DMs!",
    "NSFWChannelRequired": "You can only use this command on channels that are marked as NSFW.",
    "CheckFailure": "Command Check Failure, You are not authorized to use this command!",
    "ForbiddenError": "I'm not allowed to perform that action! Permission Denied.",
    "ConcurrencyLimit": "Please wait until the previous command execution has completed!",
    "BadRequest": "Malformed Request! Please re-check your input for any errors and try again!",
    "DiscordError": "An error occurred on Discords side.",
}


async def send_embed(name, code, event, *args):
    message = error_message[name]
    if args:
        message = message.format(*args)
    err = hikari.Embed(
        description=f"**:warning: {message}**",
        timestamp=datetime.datetime.now().astimezone(),
        color=0xFF0000,
    )
    if code:
        err.set_image(f"https://http.cat/{code}.jpg")
    await event.context.respond(
        await technobabble(), embed=err, flags=hikari.MessageFlag.EPHEMERAL
    )


async def on_error(event: lightbulb.CommandErrorEvent):
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.errors.CommandNotFound):
        await send_embed("CommandNotFound", 404, event, exception.invoked_with)
    elif isinstance(exception, lightbulb.errors.MissingRequiredPermission):
        await send_embed("MissingPermissions", 403, event, exception.missing_perms.name)
    elif isinstance(exception, lightbulb.errors.NotEnoughArguments):
        await send_embed(
            "MissingRequiredArgument",
            410,
            event,
            ", ".join(arg.name for arg in exception.missing_options),
        )
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await send_embed("CommandOnCooldown", 420, event, int(exception.retry_after))
    elif isinstance(exception, lightbulb.errors.BotMissingRequiredPermission):
        await send_embed(
            "BotMissingPermissions", 403, event, exception.missing_perms.name
        )
    elif isinstance(exception, lightbulb.errors.NotOwner):
        await send_embed("NotOwner", 401, event)
    elif isinstance(exception, lightbulb.errors.ConverterFailure):
        await send_embed("ConversionError", 400, event, exception.option.name)
    elif isinstance(exception, lightbulb.OnlyInGuild):
        await send_embed("NoPrivateMessage", 423, event)
    elif isinstance(exception, lightbulb.errors.NSFWChannelOnly):
        await send_embed("NSFWChannelRequired", 423, event)
    elif isinstance(exception, lightbulb.errors.CheckFailure):
        await send_embed("CheckFailure", 401, event)
    elif isinstance(exception, lightbulb.errors.MaxConcurrencyLimitReached):
        await send_embed("ConcurrencyLimit", 429, event)
    elif isinstance(event.exception.__cause__, hikari.ForbiddenError):
        await send_embed("ForbiddenError", 403, event)
        from bot import logger

        logger.error(event.exception.__cause__)
    elif isinstance(event.exception.__cause__, hikari.BadRequestError):
        await send_embed("BadRequest", 400, event)
        from bot import logger

        logger.error(event.exception.__cause__)
    elif isinstance(event.exception.__cause__, hikari.errors.InternalServerError):
        await send_embed("DiscordError", 500, event)
        from bot import logger

        logger.error(event.exception.__cause__)
    else:
        if isinstance(event.exception, lightbulb.CommandInvocationError):
            errormsg = hikari.Embed(
                title=f"🛑 An error occurred with the `{event.context.command.name}` command.",
                color=0xFF0000,
                timestamp=datetime.datetime.now().astimezone(),
            )
            errormsg.set_image("https://http.cat/500.jpg")
            # errormsg.add_field(name="📜 **__Error Log__**:", value=f"```py\n{exception}```")
            await event.context.respond(content=await technobabble(), embed=errormsg)
            from bot import logger

            logger.error(event.exception)
            raise (event.exception)
