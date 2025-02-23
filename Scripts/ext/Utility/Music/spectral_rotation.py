import os

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb
import numpy as np
import soundfile as sf
from scipy.fftpack import fft, ifft

plugin = lightbulb.Plugin(
    "Music Spectral Rotation", "Rotate an audio file in the spectral domain."
)


def rotate_signal(signal, flip):
    if flip:
        signal = signal[::-1]

    x = np.concatenate((signal, signal[1:][::-1]))
    rotSig = ifft(x)
    rotSig = np.real(rotSig[: len(rotSig) // 2 + 1])  # Extract real part

    energy_ratio = np.sqrt(np.sum(np.abs(signal) ** 2) / np.sum(np.abs(rotSig) ** 2))
    rotSig *= energy_ratio

    return rotSig


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("file", "The audio file to rotate", type=hikari.OptionType.ATTACHMENT)
@lightbulb.option(
    "flip", "Flip the signal before rotation", type=bool, default=True, required=False
)
@lightbulb.command(
    "music_spectral_rotation",
    "Rotate an audio file in the spectral domain.",
    pass_options=True,
    auto_defer=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def spectral_rotation_command(
    ctx: lightbulb.SlashContext, file: hikari.Attachment, flip: bool
):
    if not await utils.validate_command(ctx):
        return

    try:
        if not file.filename.lower().endswith((".wav", ".flac")):
            await ctx.respond("Only WAV and FLAC files are supported.", ephemeral=True)
            return

        input_path = os.path.join(
            config.Paths.data_folder,
            "Downloaded Content",
            f"temp_{ctx.author.id}_{file.filename}.wav",
        )
        output_path = os.path.join(
            config.Paths.data_folder,
            "Downloaded Content",
            f"temp_{ctx.author.id}_{file.filename}_rotated.wav",
        )

        await file.save(input_path)

        try:
            signal, sample_rate = sf.read(input_path, dtype="float64")
        except Exception as e:
            from bot import logger

            await ctx.respond(
                f"Error while reading the audio file: {e}", ephemeral=True
            )
            logger.error(f"Error while reading the audio file: {e}")
            return

        if signal.ndim not in [1, 2]:
            await ctx.respond(
                "Only mono and stereo audio files are supported.", ephemeral=True
            )
            return

        if signal.ndim == 1:
            rot_signal = rotate_signal(signal, flip)
        else:
            rot_signal = np.column_stack(
                (rotate_signal(signal[:, 0], flip), rotate_signal(signal[:, 1], flip))
            )

        sf.write(
            output_path,
            rot_signal.astype(np.float64),
            sample_rate,
            format="WAV",
            subtype="FLOAT",
        )

        if (
            os.path.getsize(output_path) > 25 * 1024 * 1024
        ):  # Check if the file is larger than 25 MB
            await ctx.respond("The rotated audio file is too large to send.")
            return

        await ctx.respond(
            "Here is the rotated audio file:", attachment=hikari.File(output_path)
        )
    except Exception as e:
        from bot import logger

        logger.error(f"Error during spectral rotation command: {e}")
    finally:
        # Cleanup
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
