import json
import random
import discord
from discord.ext import commands

bot = commands.Bot('[] ', None, "A bot created for team 3494.", True)
quotes = []
with open("footers.json") as f:
    quotes = json.load(f)

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
    await bot.process_commands(message)

token = None
with open("creds.txt") as creds:
    token = creds.read().strip()

@bot.command(description="Quotes are fun!")
async def quote():
    await bot.say(random.choice(quotes))

@bot.command(description="Reload a bot module.", pass_context=True)
async def reload(ctx, module: str):
    if (ctx.message.author.id == "164342765394591744"):
        if (module != "main"):
            bot.unload_extension(module)
            bot.load_extension(module)
            await bot.say("Reloaded module `{}`.".format(module))
        else:
            await bot.say("Cannot reload `main`.")
    else:
        await bot.say("Did not reload module `{}`. Are you my maker?".format(module))

bot.load_extension("roles")
bot.load_extension("moderate")
bot.run(token)
