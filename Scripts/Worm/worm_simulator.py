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

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=400,400")

    driver = webdriver.Chrome(options=chrome_options)

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

    driver.get(f"file://{file_path}")

    def take_screenshot():
        timestamp = int(time.time())
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
        img = Image.open(image_path)

        max_width = int((max_chars / 1.8) ** 0.5)
        aspect_ratio = img.height / img.width
        new_width = min(max_width, img.width) - 1
        new_height = int(new_width * aspect_ratio * 0.55)

        img = img.resize((new_width, new_height))

        img = img.convert("L")

        ascii_chars = "@%#*+=-:. "

        ascii_art = ""
        for pixel_value in img.getdata():
            pixel_index = min(pixel_value // 10, len(ascii_chars) - 1)
            ascii_art += ascii_chars[pixel_index]

            if len(ascii_art) % new_width == 0:
                ascii_art += "\n"

        return ascii_art

    while not stop_worm:
        image = take_screenshot()
        # text = image_to_ascii(image_path=image)
        yield image
        time.sleep(1)


async def stop_the_worm():
    global stop_worm
    stop_worm = True
