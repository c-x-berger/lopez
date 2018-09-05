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

    @staticmethod
    def roll_ndn(dice: list) -> list:
        rolls = []
        for i in range(dice[0]):
            rolls.append(random.randint(1, dice[1]))
        return rolls

    @commands.command()
    async def roll(self, ctx: commands.Context, dice: ndn):
        '''Straight rolls a die (no ability scores applied.)'''
        rolls = roller.roll_ndn(dice)
        message = "**Your rolls:**\n"
        for i in range(len(rolls)):
            roll = rolls[i]
            message += "{} + ".format(roll) if i is not len(rolls) - 1 else "{} = ".format(roll)
        message += "**{0!s}**".format(sum(rolls))
        await ctx.send(message)

    @commands.command()
    async def skill_check(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await ctx.send("Come back when you have things to work with!")
            return
        bonus = roller.to_int(args[0])
        message = "**You rolled:**\n"
        roll = roller.roll_ndn([1, 20])
        total = sum(roll) + bonus
        message += "{0} {3} {1} = **{2}**\n".format(sum(roll), abs(bonus), total, "+" if bonus >= 0 else "-")
        try:
            dc = roller.to_int(args[1])
        except IndexError:
            pass
        else:
            message += "{} {} {}: {}".format(total, "passes DC" if total >= dc else "fails DC", dc, "Success!" if total >= dc else "You fail!")
        await ctx.send(message)

def setup(bot: commands.Bot):
    bot.add_cog(roller(bot))
