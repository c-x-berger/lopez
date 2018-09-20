from discord.ext import commands
import random
from wcm import wild_comp


class wild_speller():
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def spell(self, ctx: commands.Context, *, seed: str = None):
        random.seed(seed)
        await ctx.send(wild_comp.get_spell_string())


def setup(bot):
    bot.add_cog(wild_speller(bot))
