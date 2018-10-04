"""
Util functions. Cuts down on boilerplate code, ideally.
"""

import discord
import json
import random

quotes = []
with open("footers.json", encoding="utf-8") as f:
    quotes = json.load(f)


def embed_template(title: str = "Someone messed up!") -> discord.Embed:
    em = discord.Embed(title=title).set_footer(
        text=random.choice(quotes), icon_url="https://i.imgur.com/2VepakW.png"
    )
    em.colour = discord.Colour.gold()
    return em


def comma_sep(values: str) -> list:
    r = []
    for value in values.split(","):
        r.append(value.strip())
    return r
