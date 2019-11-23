import asyncio
import datetime
import logging
import os
import random
import subprocess
import sys
import time
import traceback
from typing import Union

import asyncpg
import discord
from discord.ext import commands

import config
import footers

prefixes = [
    "[] ",
    "[]",
    "lopez pls ",
    "lopez, please ",
    "lopez, ",
    "hey lopez, ",
    "hey lopez ",
    "hey, lopez ",
]


def get_pre(bot: commands.Bot, message: discord.Message) -> Union[str, list]:
    lowercased = message.content.lower()
    for prefix in prefixes:
        if lowercased.startswith(prefix):
            return commands.when_mentioned_or(message.content[: len(prefix)])(
                bot, message
            )
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(
    get_pre,
    description="A bot created for everybody",
    owner_id=164342765394591744,
    case_insensitive=True,
)

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename="logs/lopez_{}.log".format(datetime.datetime.today()),
    encoding="utf-8",
    mode="w",
)
handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s: %(name)s: %(message)s")
)
logger.addHandler(handler)
bot.log_handler = handler


async def open_conn(b: commands.Bot):
    b.connect_pool = await asyncpg.create_pool(config.postgresql)


bot.loop.run_until_complete(open_conn(bot))


@bot.event
async def on_ready():
    logger.info("\n".join(["Logged in as", bot.user.name, str(bot.user.id), "------"]))
    subprocess.call(["/bin/systemd-notify", "--pid=" + str(os.getpid()), "--ready"])


async def watchdog():
    await bot.wait_until_ready()
    while True:
        subprocess.call(
            ["/bin/systemd-notify", "--pid=" + str(os.getpid()), "WATCHDOG=1"]
        )
        await asyncio.sleep(15)


bot.loop.create_task(watchdog())


@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)
    if not (message.author == bot.user):
        if bot.user.mentioned_in(message) and not message.mention_everyone:
            await message.add_reaction(bot.get_emoji(406171759365062656))


@bot.event
async def on_command_completion(ctx: commands.Context):
    if ctx.command.name == "help":
        await ctx.message.add_reaction("\N{OPEN MAILBOX WITH RAISED FLAG}")


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Stock error handler (https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612)"""
    if hasattr(ctx.command, "on_error"):
        return

    ignore = (commands.CommandNotFound, commands.UserInputError)
    # get original error from things like ctx.invoke
    error = getattr(error, "original", error)
    if isinstance(error, ignore):
        return
    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send("{} has been disabled.".format(ctx.command))
    elif isinstance(error, commands.MissingPermissions):
        return await ctx.send(error.args[0])
    elif isinstance(error, commands.BotMissingPermissions):
        return await ctx.send(
            "I don't have the power to do that!\n{}".format(error.args[0])
        )
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.send("{} can't be used in DMs.".format(ctx.command))
        except:
            # dms off
            pass
    logger.error("Ignoring exception in command {}:".format(ctx.command))
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.command()
async def prefix(ctx: commands.Context):
    send = "*My prefixes are* "
    for i in range(len(prefixes)):
        if i is not len(prefixes) - 1 and i is not len(prefixes) - 2:
            send += "**{}**; ".format(prefixes[i])
        elif i is len(prefixes) - 2:
            send += "**{}**; *and* ".format(prefixes[i])
        else:
            send += "**{}**".format(prefixes[i])
    send += "\nThese are case insensitive, so `{} ` is a valid command prefix (please don't shout at me!)".format(
        random.choice(prefixes[1:]).upper()
    )
    fix = random.choice(prefixes)
    send += "\nAlso, a prefix must be followed by a space to work (e.g. `{0}roll 1d20` is valid while `{1}roll 1d20` is not.)".format(
        fix, fix.strip()
    )
    await ctx.send(send)


@bot.command()
async def quote(ctx: commands.Context):
    """Quotes are fun!"""
    g_rating = "e10"
    async with bot.connect_pool.acquire() as conn:
        val = await conn.fetchval(
            "SELECT esrb FROM guild_table WHERE guild_id = $1", ctx.guild.id
        )
        g_rating = g_rating if val is None else val
    await ctx.send(random.choice(footers.quotes[g_rating]))


@bot.command()
async def uptime(ctx: commands.Context):
    """Tells how long the bot has been online."""
    delta = datetime.timedelta(seconds=int(time.time() - botstart))
    await ctx.send("**Uptime:** {}".format(str(delta)))


@bot.command()
async def invite(ctx: commands.Context):
    """Gets a link to invite Lopez."""
    perms = discord.Permissions.none()
    perms.view_audit_log = True
    perms.manage_roles = True
    perms.manage_channels = True
    perms.create_instant_invite = True
    perms.send_messages = True
    perms.manage_messages = True
    perms.embed_links, perms.attach_files, perms.read_message_history = True, True, True
    perms.external_emojis, perms.add_reactions = True, True
    await ctx.send(
        "Use this link to invite Lopez into your Discord server!\n"
        + discord.utils.oauth_url("436251140376494080", perms)
    )


cogs = [
    "git_update",
    "roles",
    "moderate",
    "modi_bot",
    "developer",
    "roller",
    "wild_speller",
    "parts",
    "moderation.channels",
    "moderation.guild",
    "timeclock",
    "utility.reddit",
]
for cog in cogs:
    bot.load_extension("cogs." + cog)

token = None
with open("creds.txt") as creds:
    token = creds.read().strip()
logging.info("Starting Lopez...")
botstart = time.time()
bot.run(token, reconnect=True)
