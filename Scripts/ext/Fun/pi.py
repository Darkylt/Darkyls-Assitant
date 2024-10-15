"""
todo: Pls organize...i have low standards but...this is atrocious
"""

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

import asyncio
import json
import os
import random
from collections import Counter
from statistics import StatisticsError, mean, median, mode

import bot_utils as utils
import config_reader as config
import hikari
import lightbulb

# import numpy as np
import matplotlib.pyplot as plt

plugin = lightbulb.Plugin("pi", "Pi related commands")


pi_length = 1_000_000_000

calculated_pi_length = None


def formatted_number():
    if calculated_pi_length is None:
        return "{:,}".format(pi_length).replace(",", ".")
    else:
        return "{:,}".format(calculated_pi_length).replace(",", ".")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.GlobalBucket)
@lightbulb.option(
    "number", "The number you want to search for", type=int, required=True
)
@lightbulb.command("pi_search", "Search for a number in pi.", pass_options=True)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def searchpi_command(ctx: lightbulb.context.SlashContext, number) -> None:
    if not await utils.validate_command(ctx):
        return

    pi_file = os.path.join(config.Paths.assets_folder, "Text", "pi.txt")

    number_str = str(number)
    number_len = len(number_str)

    # Define chunk size (10MB)
    chunk_size = 10 * 1024 * 1024

    message = await ctx.respond("Searching...")

    try:
        with open(pi_file, "r", encoding="utf-8") as f:
            overlap = number_len - 1
            position = 0
            chunk = f.read(chunk_size)

            while chunk:
                # Search for the number in the current chunk
                index = chunk.find(number_str)

                if index != -1:
                    await message.edit(
                        f"The number {number_str} was found at position **{position + index}** of pi."
                    )
                    return

                # Read the next chunk, including overlap
                position += chunk_size - overlap
                f.seek(position)
                chunk = f.read(chunk_size)

                # Combine the end of the previous chunk with the new chunk to handle overlaps
                if len(chunk) > 0:
                    combined_chunk = chunk[-overlap:] + chunk[:overlap]
                    index = combined_chunk.find(number_str)
                    if index != -1:
                        # Adjust the index based on the actual position in the file
                        await message.edit(
                            f"The number {number_str} was found at position **{position - overlap + index}** of pi."
                        )
                        return

            pi_jokes_file = os.path.join(
                config.Paths.assets_folder, "Text", "pijokes.json"
            )

            with open(pi_jokes_file, "r") as jf:
                jokes = json.load(jf)

            joke = random.choice(jokes)

            await message.edit(
                f"The number {number_str} was not found in the first {formatted_number()} digits of pi.\n\nHere's a joke about pi instead:\n{joke['setup']}\n||{joke['punchline']}||"
            )

    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during pi_search command: {e}")
        await message.edit(f"An error occurred! {utils.error_fun}")


@plugin.command
@lightbulb.command("pi_fact", "Get a random fact about pi.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def pi_fact_command(ctx: lightbulb.context.SlashContext) -> None:
    if not await utils.validate_command(ctx):
        return

    facts_file = os.path.join(config.Paths.assets_folder, "Text", "pifacts.txt")

    try:
        with open(facts_file, "r", encoding="utf-8") as file:
            facts = file.readlines()
            random_fact = random.choice(facts)
            # Splitting the first sentence
            sentences = random_fact.split(".")
            first_sentence = sentences[0] + "."
            rest_of_the_line = ".".join(
                sentences[1:]
            ).strip()  # Joining the remaining sentences

        await ctx.respond(f"**{first_sentence}** {rest_of_the_line}")
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during pi_fact command: {e}")
        await ctx.respond(
            f"An error occurred! {utils.error_fun}", flags=hikari.MessageFlag.EPHEMERAL
        )


def get_segment_statistic(segment: int, total_digits: int):
    str_segment = str(segment)

    frequency = {}
    even_count = 0
    odd_count = 0
    positions = {}
    total_gaps = 0
    total_gap_count = 0
    digits_list = []

    for index, digit in enumerate(str_segment):
        if digit in frequency:
            frequency[digit] += 1
            positions[digit].append(index)
        else:
            frequency[digit] = 1
            positions[digit] = [index]

        if int(digit) % 2 == 0:
            even_count += 1
        else:
            odd_count += 1

    for digit in str_segment:
        digits_list.append(int(digit))

    sorted_frequency = dict(
        sorted(frequency.items(), key=lambda item: item[1], reverse=True)
    )

    formatted_string = "**Number stats:**\n"
    for digit, count in sorted_frequency.items():
        percentage = (count / total_digits) * 100
        if count == 1:
            formatted_string += (
                f"**{digit}**: *{count} time,* {percentage:.4f}% of segment\n"
            )
        else:
            formatted_string += (
                f"**{digit}**: *{count} times,* {percentage:.4f}% of segment\n"
            )

    # List numbers not in the segment
    all_digits = set("0123456789")
    present_digits = set(str_segment)
    missing_digits = all_digits - present_digits

    formatted_string += "\n**Missing Digits:**\n"
    if missing_digits:
        formatted_string += f"{', '.join(sorted(missing_digits))}\n"
    else:
        formatted_string += "None (all digits 0-9 are present)\n"

    even_percentage = (even_count / total_digits) * 100
    odd_percentage = (odd_count / total_digits) * 100

    formatted_string += f"\n**Even / Odd stats:**\nEven digits: {even_count} times, {even_percentage:.2f}% of segment\n"
    formatted_string += (
        f"Odd digits: {odd_count} times, {odd_percentage:.2f}% of segment"
    )

    # Calculate mean, median, and mode
    mean_value = mean(digits_list)
    median_value = median(digits_list)

    try:
        mode_value = mode(digits_list)
    except StatisticsError:
        mode_value = "No unique mode"

    formatted_string += f"\n\n**Mean, Median, Mode:**\nMean: {mean_value:.2f}\n"
    formatted_string += f"Median: {median_value:.2f}\n"
    formatted_string += f"Mode: {mode_value}\n"

    longest_repeating_sequence = find_longest_repeating_sequence(str_segment)
    formatted_string += (
        f"\n**Longest Repeating Sequence:**\n```{longest_repeating_sequence}```"
    )

    formatted_string += "\n**Gap Analysis:**\n"
    for digit, pos_list in positions.items():
        if len(pos_list) > 1:
            gaps = [pos_list[i] - pos_list[i - 1] for i in range(1, len(pos_list))]
            total_gaps += sum(gaps)
            total_gap_count += len(gaps)

    if total_gap_count > 0:
        overall_avg_gap = total_gaps / total_gap_count
        formatted_string += (
            f"Overall average gap between the same number: {overall_avg_gap:.2f}\n"
        )
    else:
        formatted_string += "Overall average gap between the same number: No gaps (all digits appear only once)\n"

    mean_around_4_5 = False
    even_percentage_around_50 = False

    if isinstance(mode_value, int) and 3.5 <= mean_value <= 6.5:
        mean_around_4_5 = True

    if 40 <= even_percentage <= 60:
        even_percentage_around_50 = True

    if total_digits >= 200 and mean_around_4_5 and even_percentage_around_50:
        formatted_string += f"\n*With a length as large as {total_digits}, this data shows how random π really is. Notice how the digit frequencies are fairly close together and the even/odd split is around 50%, as well as the mean/median being around 4.5. This randomness is what makes π so fascinating! There are no patterns.*"

    # Removed because the formatting is off and it looks weird
    #
    #    transitions = transition_matrix(str(segment))
    #
    #    formatted_string += f"\n**Transition Matrix (Rows: From, Columns: To):**\n(For the non nerds, a transition matrix shows the probability of transitioning from one digit to another)\n```{transitions}```"

    return formatted_string


def find_longest_repeating_sequence(segment: str) -> str:
    max_length = 0
    longest_sequence = ""
    current_sequence = segment[0]

    for i in range(1, len(segment)):
        if segment[i] == segment[i - 1]:
            current_sequence += segment[i]
        else:
            if len(current_sequence) > max_length:
                max_length = len(current_sequence)
                longest_sequence = current_sequence
            current_sequence = segment[i]

    if len(current_sequence) > max_length:
        longest_sequence = current_sequence

    return longest_sequence


def generate_pie_chart(number, filename="pie_chart.png"):
    # Convert the number to a string to iterate over each digit
    number_str = str(number)

    # Count the frequency of each digit using Counter
    digit_counts = Counter(number_str)

    # Prepare data for the pie chart
    labels = list(digit_counts.keys())
    sizes = list(digit_counts.values())
    colors = plt.cm.tab20c.colors  # Use a colormap for colors

    # Generate the pie chart
    fig, ax = plt.subplots(
        figsize=(8, 8), facecolor="#171717"
    )  # Set figure background color
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors
    )
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Customize font properties
    plt.setp(texts, size=12, weight="bold", color="#e8e8e8")
    plt.setp(autotexts, size=10, weight="bold", color="#0d0d0d")

    # Set title with custom font
    plt.title("Frequency of Each Digit", fontsize=16, weight="bold", color="#e8e8e8")

    # Set the background color for the axes
    ax.set_facecolor("#171717")

    # Save the pie chart as an image
    plt.savefig(filename, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


# def transition_matrix(segment: str):
#    # Initialize the transition matrix (10x10 for digits 0-9)
#    transition_matrix = np.zeros((10, 10))
#
#    # Count transitions
#    for i in range(len(segment) - 1):
#        current_digit = int(segment[i])
#        next_digit = int(segment[i+1])
#        transition_matrix[current_digit][next_digit] += 1
#
#    # Normalize the matrix to get probabilities
#    row_sums = transition_matrix.sum(axis=1)
#    transition_matrix = transition_matrix / row_sums[:, np.newaxis]
#
#    return np.round(transition_matrix, decimals=3)


@plugin.command
@lightbulb.option(
    "start", "Where should the segment start", type=int, required=True, min_value=1
)
@lightbulb.option(
    "length",
    "The length of the segment",
    type=int,
    required=True,
    max_value=1500,
    min_value=1,
)
@lightbulb.command(
    "pi_segment", "Get a segment of pi with stats about it.", pass_options=True
)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def pi_segment_command(
    ctx: lightbulb.context.SlashContext, start, length
) -> None:
    if not await utils.validate_command(ctx):
        return

    pi_file = os.path.join(config.Paths.assets_folder, "Text", "pi.txt")

    global calculated_pi_length
    global pi_length

    if calculated_pi_length:
        pi_length = calculated_pi_length

    if start < 1 or start > (pi_length - 1):
        await ctx.respond(
            f"Please enter a start position between 1 and {formatted_number()}.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    if length < 1 or start + length - 1 > pi_length:
        await ctx.respond(
            f"I can only calculate pi up to {pi_length}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    try:

        with open(pi_file, "r") as file:
            file.seek(start - 1)
            segment = file.read(length)
            segment = segment.replace(".", "")
            segment = int(segment)

        stats = get_segment_statistic(segment, length)

        stats_image_path = os.path.join(
            config.Paths.data_folder,
            "Generated Statistics",
            f"{await utils.generate_id()}.png",
        )

        generate_pie_chart(segment, stats_image_path)

        embed = hikari.Embed(
            title="Here are some statistics about your segment:", description=stats
        )

        embed.set_author(
            name="Darkyl's Assistants PI segment command",
            icon=hikari.File(os.path.join(config.Paths.assets_folder, "pfp.png")),
        )

        embed.set_thumbnail(
            hikari.File(os.path.join(config.Paths.assets_folder, "pi.png"))
        )

        embed.set_image(hikari.File(stats_image_path))

        await ctx.respond(
            f"Your segment of pi at {start} is:\n```{segment}```", embed=embed
        )

        os.remove(stats_image_path)

    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred in /pi_segment command: {e}")
        await ctx.respond(
            f"An error occurred! {utils.error_fun}", flags=hikari.MessageFlag.EPHEMERAL
        )


async def count_characters_in_file(file_path, chunk_size=1024 * 1024):
    """
    Counts the number of characters in a file without loading the entire file into memory.

    Args:
        file_path (str): The path to the file.
        chunk_size (int): The size of the chunks to read the file in bytes. Default is 1MB.

    Returns:
        int: The total number of characters in the file.
    """
    total_characters = 0

    with open(file_path, "r") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            total_characters += len(chunk)

    return total_characters


async def count_pi():
    global calculated_pi_length

    from bot import logger

    logger.info("Counting pi.txt")

    pi_file = os.path.join(config.Paths.assets_folder, "Text", "pi.txt")
    calculated_pi_length = await count_characters_in_file(pi_file)

    logger.info("Finished counting pi.txt")


def load(bot):

    asyncio.run(count_pi())

    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
