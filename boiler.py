"""
Util functions. Cuts down on boilerplate code, ideally.
"""

import discord
import footers
import json
import random
from typing import Dict


def embed_template(
    title: str = "Someone messed up!", color: discord.Color = discord.Color.gold
) -> discord.Embed:
    em = discord.Embed(title=title).set_footer(
        text=random.choice(footers.quotes_e10),
        icon_url="https://i.imgur.com/2VepakW.png",
    )
    em.colour = color
    return em


def comma_sep(values: str) -> list:
    r = []
    for value in values.split(","):
        r.append(value.strip())
    return r


def cleanup_code(content: str) -> str:
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    # remove `foo`
    return content.strip("` \n")


def bot_and_invoke_hasperms(**perms):
    def predicate(ctx):
        msg = ctx.message
        ch = msg.channel
        permissions_invoker = ch.permissions_for(msg.author)
        permissions_bot = ch.permissions_for(ctx.me)
        bot_has = all(
            getattr(permissions_bot, perm, None) == value
            for perm, value in perms.items()
        )
        invoke_has = all(
            getattr(permissions_invoker, perm, None) == value
            for perm, value in perms.items()
        )
        return bot_has and invoke_has

    return discord.ext.commands.check(predicate)


def perms_todict(perms: discord.PermissionOverwrite) -> Dict[str, bool]:
    r = {}
    for key, value in iter(perms):
        if value is not None:
            r[key] = value
    return r


def perms_tojson(perms: discord.PermissionOverwrite) -> str:
    return json.dumps(perms_todict(perms))


def perms_fromjson(j: str) -> discord.PermissionOverwrite:
    return discord.PermissionOverwrite(**(json.loads(j)))
