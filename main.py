import asyncio
import boiler
import datetime
import json
import logging
import math
import os
import random
import subprocess
import time
import discord
from discord.ext import commands

bot = commands.Bot('{} ', None, "A bot created for team 3494.", True)
announcment_channels = [286175809130201088]
botstart = time.time()

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs/lopez_{}.log'.format(datetime.datetime.today()), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


async def watchdog():
    await bot.wait_until_ready()
    while True:
        subprocess.call(['/bin/systemd-notify', '--pid=' +
                         str(os.getpid()), 'WATCHDOG=1'])
        await asyncio.sleep(15)


@bot.event
async def on_ready():
    logging.info('\n'.join(['Logged in as', bot.user.name, str(bot.user.id), '------']))
    subprocess.call(['/bin/systemd-notify', '--pid=' +
                     str(os.getpid()), '--ready'])


@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)
    if not (message.author == bot.user):
        if (bot.user.mentioned_in(message) and not message.mention_everyone):
            await message.add_reaction(discord.utils.get(bot.get_all_emojis(), name='pingsock', guild__id=286174293006745601))
        elif ("LOPEZ" in message.content.upper() and not (message.channel.id in announcment_channels)):
            await message.channel.send('Hi!', delete_after=2.0)


@bot.command(description="Quotes are fun!")
async def quote(ctx: commands.Context):
    await ctx.send(random.choice(boiler.quotes))


@bot.command()
async def uptime(ctx: commands.Context):
    '''Tells how long the bot has been online.'''
    delta = datetime.timedelta(seconds=int(time.time() - botstart))
    await ctx.send("**Uptime:** {}".format(str(delta)))


@bot.command()
async def invite(ctx: commands.Context):
    '''Gets a link to invite Lopez.'''
    await ctx.send("Use this link to invite Lopez into your Discord server!\n" + discord.utils.oauth_url("436251140376494080"))

bot.loop.create_task(watchdog())

cogs = ["git_update", "roles", "moderate", "modi_bot"]
for cog in cogs:
    bot.load_extension("cogs." + cog)

token = None
with open("creds.txt") as creds:
    token = creds.read().strip()
bot.run(token)
