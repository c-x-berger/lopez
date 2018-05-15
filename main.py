import asyncio
import boiler
import datetime
import json
import math
import os
import random
import subprocess
import time
import discord
from discord.ext import commands

bot = commands.Bot('[] ', None, "A bot created for team 3494.", True)
announcment_channels = ["286175809130201088"]
botstart = time.time()


async def watchdog():
    await bot.wait_until_ready()
    while True:
        subprocess.call(['/bin/systemd-notify', '--pid=' +
                         str(os.getpid()), 'WATCHDOG=1'])
        await asyncio.sleep(15)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    subprocess.call(['/bin/systemd-notify', '--pid=' +
                     str(os.getpid()), '--ready'])


@bot.event
async def on_message(message):
    if not (message.author == bot.user):
        if (bot.user.mentioned_in(message) and not message.mention_everyone):
            await bot.add_reaction(message, discord.utils.get(bot.get_all_emojis(), name="pingsock", server__id="286174293006745601"))
        elif ("LOPEZ" in message.content.upper() and not (message.channel.id in announcment_channels)):
            await bot.send_message(message.channel, "Hi!")
    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    if (message in bot.messages):
        print("removing message with content \"{}\" from deque".format(message.content))
        bot.messages.remove(message)


@bot.command(description="Quotes are fun!")
async def quote():
    await bot.say(random.choice(boiler.quotes))


@bot.command()
async def uptime():
    '''Tells how long the bot has been online.'''
    delta = datetime.timedelta(seconds=int(time.time() - botstart))
    await bot.say("**Uptime:** {}".format(str(delta)))


@bot.command()
async def invite():
    '''Gets a link to invite Lopez.'''
    await bot.say("Use this link to invite Lopez into your Discord server!\n" + discord.utils.oauth_url("436251140376494080"))

bot.loop.create_task(watchdog())

cogs = ["git_update", "roles", "moderate", "modi_bot"]
for cog in cogs:
    bot.load_extension("cogs." + cog)

token = None
with open("creds.txt") as creds:
    token = creds.read().strip()
bot.run(token)
