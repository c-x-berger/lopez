import discord
from discord.ext import commands

bot = commands.Bot('[] ', None, "A bot created for team 3494.", True)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

token = None
with open("creds.txt") as creds:
    token = creds.read().strip()

bot.load_extension("roles")
bot.run(token)
