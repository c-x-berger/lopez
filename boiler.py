"""
Util functions. Cuts down on boilerplate code, ideally.
"""

import discord

def embed_template():
    em = discord.Embed()
    em.set_footer(icon_url="https://i.imgur.com/j1bnW3q.png")
    em.colour = discord.Colour.gold()
    return em
