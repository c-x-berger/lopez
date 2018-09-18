import asyncio
import asyncpg
import boiler
import config
import datetime
import discord
from discord.ext import commands
import json
import logging
import math
import os
import random
import subprocess
import time
from typing import Union

prefixes = ['[] ', 'lopez pls ', 'lopez, please ', 'lopez, ', 'hey lopez, ', 'hey lopez ', 'hey, lopez ']


def get_pre(bot: commands.Bot, message: discord.Message) -> Union[str, list]:
    lowercased = message.content.lower()
    for prefix in prefixes:
        if lowercased.startswith(prefix):
            return message.content[:len(prefix)]
    return prefixes


logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='logs/lopez_{}.log'.format(datetime.datetime.today()), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(get_pre, None, "A bot created for team 3494.",
                   True, owner_id=164342765394591744)
botstart = time.time()


async def open_conn(b: commands.Bot):
    b.connect_pool = await asyncpg.create_pool(config.postgresql)


async def watchdog():
    await bot.wait_until_ready()
    while True:
        subprocess.call(['/bin/systemd-notify', '--pid=' +
                         str(os.getpid()), 'WATCHDOG=1'])
        await asyncio.sleep(15)


@bot.event
async def on_ready():
    logging.info(
        '\n'.join(['Logged in as', bot.user.name, str(bot.user.id), '------']))
    subprocess.call(['/bin/systemd-notify', '--pid=' +
                     str(os.getpid()), '--ready'])


@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)
    if not (message.author == bot.user):
        if (bot.user.mentioned_in(message) and not message.mention_everyone):
            await message.add_reaction(bot.get_emoji(406171759365062656))


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
    send += "\nThese are case insensitive, so `{} ` is a valid command prefix (please don't shout at me!)".format(random.choice(prefixes[1:]).upper())
    fix = random.choice(prefixes)
    send += "\nAlso, a prefix must be followed by a space to work (e.g. `{0}1d20` is valid while `{1}roll 1d20` is not.)".format(fix, fix.strip())
    await ctx.send(send)


@bot.command()
async def quote(ctx: commands.Context):
    '''Quotes are fun!'''
    await ctx.send(random.choice(boiler.quotes))


@bot.command()
async def uptime(ctx: commands.Context):
    '''Tells how long the bot has been online.'''
    delta = datetime.timedelta(seconds=int(time.time() - botstart))
    await ctx.send("**Uptime:** {}".format(str(delta)))


@bot.command()
async def invite(ctx: commands.Context):
    '''Gets a link to invite Lopez.'''
    await ctx.send("Use this link to invite Lopez into your Discord server!\n" + discord.utils.oauth_url("436251140376494080", discord.Permissions(335899840)))

bot.loop.create_task(watchdog())
bot.loop.run_until_complete(open_conn(bot))

cogs = ["git_update", "roles", "moderate", "modi_bot", "developer", "roller"]
for cog in cogs:
    bot.load_extension("cogs." + cog)

token = None
with open("creds.txt") as creds:
    token = creds.read().strip()
bot.run(token)
