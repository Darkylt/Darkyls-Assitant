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
import random

import config_reader as config
import hikari
import lightbulb
import requests
from flask import Flask, request

plugin = lightbulb.Plugin("youtube", "Announce latest YouTube videos")
app = Flask(__name__)


async def wait_until_initialized():
    while not (
        hasattr(plugin.bot, "application")
        and getattr(plugin.bot.application, "app", None)
    ):
        await asyncio.sleep(1)


async def announce_latest_video(video_id: str, video_title: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    messages = [
        "**Darkyl** uploaded: {}",
        "NEW UPLOAD: {}",
        "We got a new video from **Darkyl**: {}",
    ]
    formatted_url = f"[{video_title}]({url})"
    content = f"{str(random.choice(messages)).format(formatted_url)}\n\n<@&{config.YouTube.ping_role}>"
    await plugin.app.rest.create_message(
        channel=config.YouTube.discord_channel, content=content, role_mentions=True
    )


def subscribe_to_youtube_channel(channel_id):
    hub_url = "https://pubsubhubbub.appspot.com/"
    topic_url = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}"
    callback_url = "http://yourdomain.com/webhook"

    response = requests.post(
        hub_url,
        data={
            "hub.mode": "subscribe",
            "hub.topic": topic_url,
            "hub.callback": callback_url,
            "hub.lease_seconds": 864000,
        },
    )

    if response.status_code == 202:
        print("Successfully subscribed to the channel.")
    else:
        print(f"Failed to subscribe: {response.content}")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    video_id = data["video_id"]
    video_title = data["video_title"]
    asyncio.run(announce_latest_video(video_id, video_title))
    return "", 200


async def run():
    youtube_channel = config.YouTube.channel
    subscribe_to_youtube_channel(youtube_channel)


@plugin.listener(hikari.StartedEvent)
async def on_startup(event: hikari.StartedEvent):
    await wait_until_initialized()
    asyncio.create_task(run())


if __name__ == "__main__":
    app.run(port=5000)
