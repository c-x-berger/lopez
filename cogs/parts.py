import aiohttp
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from typing import List, Optional


class parts:
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
                return BeautifulSoup(data, features="html5lib")
            elif resp.status == 404:
                raise discord.NotFound(resp, "Not found")

    async def get_mcmaster_part_page(self, part_num: str) -> BeautifulSoup:
        url = parts.mcmaster_part(part_num)
        async with self.aio_client.get(url) as resp:
            if 300 > resp.status >= 200:
                data = await resp.text()
                return BeautifulSoup(data, features="html5lib")

    @commands.group(
        invoke_without_command=True, aliases=["parts"], case_insensitive=True
    )
    async def part(self, ctx: commands.Context, *part_num):
        """
        Look up a part by part number/ID. Supports AndyMark and McMaster Carr.
        """
        if part_num is not None:
            await ctx.message.add_reaction(self.bot.get_emoji(393852367751086090))
            async with ctx.typing():
                for num in part_num:
                    if num.startswith("am-"):
                        await ctx.invoke(self.andy, num)
            await ctx.message.remove_reaction(
                self.bot.get_emoji(393852367751086090), ctx.guild.me
            )
            await ctx.message.add_reaction(self.bot.get_emoji(314349398811475968))
        else:
            return await ctx.invoke(self.bot.get_command("help"), "part")

    @part.command(
        description="Looks up a part on AndyMark. Supports part names and 404s.",
        aliases=["andymark", "am"],
    )
    async def andy(self, ctx: commands.Context, *part_numbers):
        """
        Looks up a part on AndyMark.
        """
        r = {}
        s = ""
        for p in part_numbers:
            _p = await self.get_anymark_part_page(p)
            if (
                _p.title.contents[0].lower()
                == "andymark robot parts kits mecanum omni wheels"
            ):
                # for some god-forsaken reason AM doesn't properly 404
                # i guess it's for thier meme not found page but it's really annoying
                r[p] = "Could not find part `{}`".format(p)
            else:
                r[_p.title.contents[0]] = self.andy_part(p)
        for key, value in r.items():
            s += "{}: {}\n".format(key, value)
        await ctx.send(s)

    @part.command(
        description="Looks up a part on McMaster Carr. Doesn't support part names or 404s.",
        aliases=["mc", "mmc", "mcmastercarr"],
    )
    async def mcmaster(self, ctx: commands.Context, *part_numbers):
        """
        Looks up a part on McMaster Carr.
        """
        r = {}
        s = ""
        for p in part_numbers:
            r[p] = parts.mcmaster_part(p)
        for key, value in r.items():
            s += "{}: {}\n".format(key, value)
        await ctx.send(s)


def setup(bot):
    bot.add_cog(parts(bot))
