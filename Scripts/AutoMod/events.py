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

import auto_mod
import buttons
import config_reader as config
import hikari
import lightbulb
import member_managment

plugin = plugin = lightbulb.Plugin("automod_events", "Handles events")


@plugin.listener(hikari.GuildMessageDeleteEvent)
async def on_guild_msg_delete(event: hikari.GuildMessageDeleteEvent):

    if event.guild_id != config.Bot.server:
        return

    msg = event.old_message

    if msg is None:
        channel = await event.app.rest.fetch_channel(event.channel_id)
        from bot import logger

        logger.info(f"Message deleted in {channel.mention}.")
        return

    try:
        if msg.author.is_bot or msg.author.is_system:
            return

        if not msg.guild_id == config.Bot.server:
            return

        name = msg.author.username
        mention = msg.author.mention
        content = msg.content
        try:
            attach = msg.attachments[0]
            attachment_file = attach.url or attach.proxy_url
        except (IndexError, KeyError):
            attachment_file = None

        embed = hikari.Embed(
            title="A message has been deleted.",
            description=f"{mention}'s message has been deleted.",
            color=(hikari.Color.from_rgb(255, 0, 0)),
        )
        embed.add_field(name="Author:", value=name)
        embed.add_field(name="Content:", value=content)

        if attachment_file is None:
            # await plugin.bot.application.app.rest.create_message(channel=config.Bot.logs_channel, embed=embed)
            await plugin.bot.application.app.rest.create_message(
                channel=config.Bot.logs_channel, embed=embed
            )
        else:
            # await plugin.bot.application.app.rest.create_message(channel=config.Bot.logs_channel, embed=embed, attachments=attachment_file)
            await plugin.bot.application.app.rest.create_message(
                channel=config.Bot.logs_channel,
                embed=embed,
                attachments=attachment_file,
            )
    except Exception as e:
        from bot import logger

        logger.error(f"Error while logging deleted message: {e}")
        return


async def handle_dm(event: hikari.MessageCreateEvent):
    """Handles direct messages."""

    # Ignore bots
    if event.author.is_bot or event.author.is_system:
        return

    # Make sure it doesn't interfere with the verification process
    from Verification.captcha_db import get_id_from_user

    if await get_id_from_user(event.author_id):
        return

    # await event.message.respond(
    #    "Heya! There are no DM features yet.\nIf you have an idea for DM interactions, tell it Darkyl!"
    # )


async def handle_guild_text(event: hikari.MessageCreateEvent, nsfw: bool):
    """Handles messages in guild text channels."""

    async def send_report(
        event: hikari.MessageCreateEvent, report_embed: hikari.Embed
    ) -> hikari.Message:
        """Sends the violation report to the designated channel."""
        view = buttons.Report()
        message = await event.app.rest.create_message(
            channel=config.Bot.report_channel, embed=report_embed, components=view
        )
        return message

    try:
        if event.message.guild_id != config.Bot.server:
            return

        if event.author.is_bot or event.author.is_system:
            return

        attachments = event.message.attachments

        if attachments:
            problematic_file = await auto_mod.check_attachments(attachments)
            if problematic_file:
                allowed_files = config.AutoMod.allowed_files
                supported_files = ", ".join(allowed_files)
                await event.message.respond(
                    f"Your file '{problematic_file}' is not allowed. Supported file types are: {supported_files}"
                )
                await event.message.delete()

        if event.message.content:
            violations, flagged_strings = await auto_mod.check_message(
                content=event.message.content, nsfw=nsfw
            )

            if violations:
                report_embed = await auto_mod.handle_violations(
                    event, violations, flagged_strings
                )
                await send_report(event, report_embed)
                auto_mod.update_report_data(
                    event.author_id, event.message.id, violations
                )
                await event.message.delete()
                return

        await member_managment.update_user_stats(
            user_id=int(event.author_id), msg=True, cmd=False, rep=False
        )
    except Exception as e:
        from bot import logger

        logger.error(f"Error during handle_guild_text: {e}")


@plugin.listener(hikari.MessageCreateEvent)
async def message(event: hikari.MessageCreateEvent):
    """Gets called whenever a message is sent."""
    try:
        channel = await plugin.bot.application.app.rest.fetch_channel(
            event.message.channel_id
        )
        channel_type = str(channel.type)

        if channel_type == "DM":
            await handle_dm(event)
        elif channel_type == "GUILD_TEXT":
            await handle_guild_text(event, nsfw=channel.is_nsfw)
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred while handling a message: {e}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
