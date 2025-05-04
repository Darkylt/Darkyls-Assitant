import bot_utils as utils
import buttons
import config_reader as config
import hikari
import lightbulb
from voice_cache import created_channels, voice_state_cache

plugin = lightbulb.Plugin("VoiceListener", "Listen to voice channels")


async def create_voice_channel(member: hikari.Member, guild_id):
    """Create a new voice channel and move the member into it."""
    try:
        channel = await plugin.app.rest.create_guild_voice_channel(
            guild_id,
            f"🔊┊{member.username}'s Channel",
            category=config.Channels.temp_voice_category,
        )
        created_channels[channel.id] = member.id
        try:
            await member.edit(voice_channel=channel)
        except hikari.ForbiddenError:
            embed = utils.EmbedMaker.generate_error_embed(
                "Error: No permission",
                f"I do not have permission to move {member.mention} to {channel.mention}.",
            )
            await plugin.app.rest.create_message(config.Channels.admin, embed=embed)
        except Exception as e:
            from bot import logger

            logger.error(f"Error moving member to new channel: {e!r}")
            embed = utils.EmbedMaker.generate_error_embed(
                "Error moving member to new channel",
                f"An unexpected error occurred while moving {member.mention} to {channel.mention}: {e!r}",
            )
            await plugin.app.rest.create_message(config.Channels.admin, embed=embed)

        embed = hikari.Embed(
            title="TempVC Control Panel",
            description="Manage your TempVoice Channel from here.",
            color="#4287f5",
        )

        view = buttons.TempVoiceChatView()

        await plugin.app.rest.create_message(
            channel=channel,
            embed=embed,
            components=view,
            flags=hikari.MessageFlag.SUPPRESS_NOTIFICATIONS,
        )

    except Exception as e:
        logger.error(f"Error creating voice channel: {e!r}")
        embed = utils.EmbedMaker.generate_error_embed(
            "Error creating voice channel",
            f"An unexpected error occurred while creating a voice channel for {member.mention}: {e!r}",
        )
        await plugin.app.rest.create_message(
            config.Channels.admin,
            embed=embed,
        )


async def delete_voice_channel(channel_id):
    """Delete a voice channel if it exists."""
    try:
        await plugin.app.rest.delete_channel(channel_id)
        del created_channels[channel_id]
    except Exception as e:
        from bot import logger

        logger.error(f"Error deleting channel {channel_id}: {e!r}")
        embed = utils.EmbedMaker.generate_error_embed(
            "Error deleting voice channel",
            f"An unexpected error occurred while deleting the voice channel {channel_id}: {e!r}",
        )
        await plugin.app.rest.create_message(config.Channels.admin, embed=embed)


@plugin.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
    member = event.state.member
    if not member:
        return

    user_id = member.id
    guild_id = event.guild_id
    old_channel_id = voice_state_cache.get(user_id)
    new_channel_id = event.state.channel_id

    # Update the cache
    if new_channel_id:
        voice_state_cache[user_id] = new_channel_id
    elif user_id in voice_state_cache:
        del voice_state_cache[user_id]

    # Handle user joining the "create channel" VC
    if new_channel_id == config.Channels.temp_voice_channel:
        await create_voice_channel(member, guild_id)

    # Handle user leaving a VC
    if old_channel_id and old_channel_id != new_channel_id:
        if old_channel_id in created_channels and not any(
            cid == old_channel_id for cid in voice_state_cache.values()
        ):
            await delete_voice_channel(old_channel_id)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
