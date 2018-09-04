import discord
from discord.ext import commands
import random

class roller():
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def to_int(number: str) -> int:
        '''Really bad str -> int function not to be used outside this file.'''
        try:
            return int(number)
        except ValueError:
            return 1

    def ndn(amount: str) -> list:
        d = amount.split('d')
        num_roll = roller.to_int(d[0])
        die_size = roller.to_int(d[1])
        return [num_roll, die_size]

    @commands.command()
    async def roll(self, ctx: commands.Context, dice: ndn):
        '''Straight rolls a die (no ability scores applied.)'''
        rolls = []
        for i in range(dice[0]):
            rolls.append(random.randint(1, dice[1])) # 1 to size of dice, inclusive
        message = "**Your rolls:**\n"
        total = 0
        for i in range(len(rolls)):
            roll = rolls[i]
            total += roll
            message += "{} + ".format(roll) if i is not len(rolls) - 1 else "{} = ".format(roll)
        message += "**{0!s}**".format(total)
        await ctx.send(message)

def setup(bot: commands.Bot):
    bot.add_cog(roller(bot))
