import bot_utils as utils
import config_reader as config
import hikari
import miru


class RenameTempVC(miru.Modal, title="Rename"):

    new_name = miru.TextInput(
        label="New Name",
        style=hikari.TextInputStyle.SHORT,
        min_length=1,
        max_length=100,
        required=True,
    )

    async def callback(self, ctx: miru.ModalContext) -> None:
        new_name = self.new_name.value
        channel: hikari.GuildVoiceChannel = await ctx.client.app.rest.fetch_channel(
            ctx.channel_id
        )

        old_name = channel.name

        await channel.edit(name=new_name)

        await ctx.respond(
            embed=utils.EmbedMaker.generate_success_embed(
                f"Renamed Channel",
                f"'{old_name}' was renamed to '{new_name}'!",
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )


class ChangeUserLimitTempVC(miru.Modal, title="Change User Limit"):

    new_limit = miru.TextInput(
        label="New Limit",
        style=hikari.TextInputStyle.SHORT,
        min_length=1,
        max_length=2,
        required=True,
        placeholder="Type 0 to disable a user limit.",
    )

    async def callback(self, ctx: miru.ModalContext) -> None:
        new_limit: str = self.new_limit.value

        if not new_limit.isdigit():
            await ctx.respond(
                embed=utils.EmbedMaker.generate_error_embed(
                    "Error.", "The Limit must be a natural number."
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        new_limit: int = int(new_limit)

        if new_limit < 0 or new_limit > 99:
            await ctx.respond(
                embed=utils.EmbedMaker.generate_error_embed(
                    "Error.", "The Limit must be between `0` and `99`."
                ),
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        channel: hikari.GuildVoiceChannel = await ctx.client.app.rest.fetch_channel(
            ctx.channel_id
        )

        await channel.edit(user_limit=new_limit)

        await ctx.respond(
            embed=utils.EmbedMaker.generate_success_embed(
                f"Changed channel Limit",
                f"The limit was set to `{new_limit}`!",
            ),
            flags=hikari.MessageFlag.EPHEMERAL,
        )
