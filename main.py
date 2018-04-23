import boiler
import json
import random
import discord
from discord.ext import commands

bot = commands.Bot('[] ', None, "A bot created for team 3494.", True)

announcment_channels = ["286175809130201088"]

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    if (bot.user.mention in message.content):
        await bot.add_reaction(message, discord.utils.get(bot.get_all_emojis(), name="pingsock"))
    elif ("LOPEZ" in message.content.upper() and not (message.channel.id in announcment_channels)):
        await bot.send_message(message.channel, "Hi!")
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if (message in bot.messages):
        print("removing message with content \"{}\" from deque".format(message.content))
        bot.messages.remove(message)

token = None
with open("creds.txt") as creds:
    token = creds.read().strip()

@bot.command(description="Quotes are fun!")
async def quote():
    await bot.say(random.choice(boiler.quotes))

bot.load_extension("roles")
bot.load_extension("moderate")
bot.load_extension("modi_bot")
bot.run(token)
