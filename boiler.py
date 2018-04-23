"""
Util functions. Cuts down on boilerplate code, ideally.
"""

import discord
import json
import random

quotes = []
with open("footers.json") as f:
    quotes = json.load(f)


def embed_template():
    em = discord.Embed(title="please change this title").set_footer(
        text=random.choice(quotes), icon_url="https://i.imgur.com/2VepakW.png")
    em.colour = discord.Colour.gold()
    return em
