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
import os
import platform
import subprocess
import time

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb
import miru

plugin = lightbulb.Plugin("Stats", "Get fun stats on the bot")

bot_start_time = time.time()


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("stats", "Get statistics on me!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def stats_command(ctx: lightbulb.SlashContext):
    start = time.perf_counter()

    if not await utils.validate_command(ctx):
        return

    message = await ctx.respond(
        "Getting stats... *(This command takes some time to compute)*"
    )

    lines, file_count = await utils.count_lines_in_files(
        directory=config.Paths.root_folder
    )

    code_line_count = (
        lines + 27000000 + 50000000 + 350000 + 500 + 46000
    )  # +Linux kernel +Ubuntu +CPython +Python interpreter +Discord

    command_count = len(ctx.bot.slash_commands)

    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()

    # Calculate uptime
    uptime = time.time() - bot_start_time
    uptime_str = format_uptime(uptime)

    thumbnail = os.path.join(config.Paths.assets_folder, "pfp.png")

    embed = hikari.Embed(
        title="Bot statistics",
        description="Here are some fun stats about me!",
        timestamp=datetime.datetime.now().astimezone(),
    )
    embed.set_thumbnail(thumbnail)
    embed.add_field("File Count:", f"I have over **{file_count}** files!", inline=False)
    embed.add_field(
        "Code Lines:",
        f"I run on over **{code_line_count}** lines of code!",
        inline=False,
    )
    embed.add_field(
        "Commands Count:", f"I have **{command_count}** commands!", inline=False
    )
    embed.add_field(
        "User count:",
        f"I can see {len(ctx.bot.cache.get_users_view())} users at this moment.",
    )
    embed.add_field(
        "\nCPU Usage:", f"Current CPU usage is **{cpu_usage:.2f}%**", inline=False
    )
    embed.add_field(
        "Memory Usage:",
        f"Current memory usage is **{memory_usage:.2f}%**",
        inline=False,
    )
    embed.add_field(
        "Uptime:", f"I have been running for **{uptime_str}**", inline=False
    )
    embed.add_field("Latency:", f"{ctx.bot.heartbeat_latency * 1000:.0f}ms")
    embed.add_field("Platform:", f"I am running on '{platform.system()}'")
    embed.add_field(
        "Using:",
        f"**Hikari** {hikari.__version__}\n**Lightbulb** {lightbulb.__version__}\n**Miru** {miru.__version__}",
    )
    end = time.perf_counter()
    embed.add_field(
        "It took:", f"It took {(end-start)*1000:,.0f}ms to execute this command"
    )
    await message.edit("", embed=embed)


def get_cpu_usage():
    if platform.system() == "Linux":
        result = subprocess.run(
            ["grep", "cpu ", "/proc/stat"], capture_output=True, text=True
        )
        fields = result.stdout.split()
        idle_time = int(fields[4])
        total_time = sum(map(int, fields[1:8]))
        usage = 100 * (1 - (idle_time / total_time))
        return usage
    elif platform.system() == "Windows":
        result = subprocess.run(
            ["wmic", "cpu", "get", "loadpercentage"], capture_output=True, text=True
        )
        lines = result.stdout.split("\n")
        for line in lines:
            if line.strip().isdigit():
                return float(line.strip())
    else:
        return 0.0


def get_memory_usage():
    # Use subprocess to get memory usage from free command
    if platform.system() == "Linux":
        result = subprocess.run(["free", "-m"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        mem_line = lines[1].split()
        total_memory = int(mem_line[1])
        used_memory = int(mem_line[2])
        memory_usage = (used_memory / total_memory) * 100
        return memory_usage
    elif platform.system() == "Windows":
        result = subprocess.run(["systeminfo"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        total_memory = used_memory = 0
        for line in lines:
            if "Total Physical Memory" in line:
                total_memory = int(
                    line.split(":")[1].strip().replace(",", "").replace("MB", "")
                )
            elif "Available Physical Memory" in line:
                available_memory = int(
                    line.split(":")[1].strip().replace(",", "").replace("MB", "")
                )
                used_memory = total_memory - available_memory
                memory_usage = (used_memory / total_memory) * 100
                return memory_usage
    else:
        return 0.0


def format_uptime(seconds):
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
