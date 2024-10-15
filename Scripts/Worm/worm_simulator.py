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

import os
import random
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

stop_worm = False


async def run_worm_simulator():
    global stop_worm

    stop_worm = False  # Just to be safe...

    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument(
        "--window-size=400,400"
    )  # Set viewport size to a square

    # Initialize WebDriver with Chrome
    driver = webdriver.Chrome(options=chrome_options)

    # Get the absolute path to the index.html file
    file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            ),
            "Scripts",
            "Worm",
            "worm-sim",
            "index.html",
        )
    )

    # Open the worm simulator webpage
    driver.get(f"file://{file_path}")  # Replace with actual URL

    # Function to take screenshot
    def take_screenshot():
        # Generate a timestamp for the filename
        timestamp = int(time.time())
        # Save screenshot with timestamp as filename
        path = os.path.abspath(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                ),
                "Scripts",
                "Worm",
                "Screenshots",
                f"screenshot_{timestamp}.png",
            )
        )
        driver.save_screenshot(path)

        return path

    def image_to_ascii(image_path, max_chars=3000):
        # Open the image
        img = Image.open(image_path)

        # Calculate the maximum width based on the maximum character count and aspect ratio
        max_width = int((max_chars / 1.8) ** 0.5)
        aspect_ratio = img.height / img.width
        new_width = min(max_width, img.width) - 1
        new_height = int(new_width * aspect_ratio * 0.55)

        # Resize the image
        img = img.resize((new_width, new_height))

        # Convert image to grayscale
        img = img.convert("L")

        # Define ASCII characters to represent different shades of gray
        ascii_chars = "@%#*+=-:. "

        # Convert each pixel to ASCII character
        ascii_art = ""
        for pixel_value in img.getdata():
            # Adjust pixel value to ensure it falls within the range of ASCII characters
            pixel_index = min(pixel_value // 10, len(ascii_chars) - 1)
            ascii_art += ascii_chars[pixel_index]

            # Add newline character at the end of each row
            if len(ascii_art) % new_width == 0:
                ascii_art += "\n"

        return ascii_art

    # Continuously generate text output
    while not stop_worm:
        image = take_screenshot()
        # text = image_to_ascii(image_path=image)
        yield image
        time.sleep(1)


async def stop_the_worm():
    global stop_worm
    stop_worm = True
