import aiohttp
from bs4 import BeautifulSoup
import discord
from discord.ext import commands


class parts():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.aio_client = aiohttp.ClientSession(loop=self.bot.loop)

    @staticmethod
    def andy_part(part_num: str) -> str:
        return "https://www.andymark.com/product-p/{}.htm".format(part_num)

    @staticmethod
    def mcmaster_part(part_num: str) -> str:
        return "https://www.mcmaster.com/{}".format(part_num.lower())

    async def get_anymark_part_page(self, part_num: str) -> BeautifulSoup:
        url = parts.andy_part(part_num)
        async with self.aio_client.get(url) as resp:
            if 300 > resp.status >= 200:
                data = await resp.text()
                return BeautifulSoup(data)

    async def get_mcmaster_part_page(self, part_num: str) -> BeautifulSoup:
        url = parts.mcmaster_part(part_num)
        async with self.aio_client.get(url) as resp:
            if 300 > resp.status >= 200:
                data = await resp.text()
                return BeautifulSoup(data)

    @commands.group(invoke_without_command=True)
    async def part(self, ctx: commands.Context):
        """
        Look up a part by part number/ID. Supports AndyMark and McMaster Carr.
        """
        return await ctx.invoke(self.bot.get_command('help'), "part")

    @part.command(aliases=['andymark', 'am'])
    async def andy(self, ctx: commands.Context, *part_numbers):
        r = {}
        s = ""
        for p in part_numbers:
            r[p] = parts.andy_part(p)
        for key, value in r.items():
            s += "{}: {}\n".format(key, value)
        await ctx.send(s)

    @part.command(aliases=['mc', 'mmc', 'mcmastercarr'])
    async def mcmaster(self, ctx: commands.Context, *part_numbers):
        r = {}
        s = ""
        for p in part_numbers:
            r[p] = parts.mcmaster_part(p)
        for key, value in r.items():
            s += "{}: {}\n".format(key, value)
        await ctx.send(s)


def setup(bot):
    bot.add_cog(parts(bot))
