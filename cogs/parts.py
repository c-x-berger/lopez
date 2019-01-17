import aiohttp
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
from typing import List, Optional


class HTTPError(Exception):
    def __init__(self, response, message):
        self.response = response
        self.status = response.status
        if isinstance(message, dict):
            self.code = message.get("code", 0)
            base = message.get("message", "")
            errors = message.get("errors")
            if errors:
                errors = flatten_error_dict(errors)
                helpful = "\n".join("In %s: %s" % t for t in errors.items())
                self.text = base + "\n" + helpful
            else:
                self.text = base
        else:
            self.text = message
            self.code = 0

        fmt = "{0.reason} (status code: {0.status})"
        if len(self.text):
            fmt = fmt + ": {1}"

        super().__init__(fmt.format(self.response, self.text))


class NotFound(HTTPError):
    pass


class InternalServerError(HTTPError):
    pass


class parts:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.aio_client = aiohttp.ClientSession(loop=self.bot.loop)

    @staticmethod
    def is_vexpro(num: str) -> bool:
        s = num.split("-")
        return (len(s) == 2) and (len(s[0]) == 3) and (len(s[1]) == 4)

    @staticmethod
    def mcmaster_part(part_num: str) -> str:
        return "https://www.mcmaster.com/{}".format(part_num.lower())

    @staticmethod
    def part_url(part_num: str) -> str:
        if parts.is_vexpro(part_num):
            return "https://www.vexrobotics.com/{}.html".format(part_num)
        elif part_num.startswith("am-"):
            return "https://andymark.com/{}".format(part_num)

    async def get_part_page(self, url: str) -> BeautifulSoup:
        async with self.aio_client.get(url) as resp:
            if 300 > resp.status >= 200:
                data = await resp.text()
                return BeautifulSoup(data, features="html5lib")
            elif resp.status == 404:
                raise NotFound(resp, "Not found")
            else:
                raise InternalServerError(resp, "Server error at {}".format(url))

    @commands.command(aliases=["parts"])
    async def part(self, ctx: commands.Context, *part_numbers):
        """
        Look up a part by number/ID. Supports AndyMark and VexPro.
        """
        r = {}
        s = ""
        await ctx.message.add_reaction(self.bot.get_emoji(393852367751086090))
        async with ctx.typing():
            for p in part_numbers:
                _p = None
                try:
                    _p = await self.get_part_page(parts.part_url(p))
                except (NotFound, InternalServerError):
                    r[p] = "Could not find part `{}`".format(p)
                else:
                    r[_p.title.contents[0]] = parts.part_url(p)
            for key, value in r.items():
                await ctx.send("{}: {}\n".format(key, value))
        await ctx.message.remove_reaction(
            self.bot.get_emoji(393852367751086090), ctx.guild.me
        )
        await ctx.message.add_reaction(self.bot.get_emoji(314349398811475968))
        await ctx.send(s)

    @commands.command(
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
            _p = None
            try:
                _p = await self.get_mcmaster_part_page(p)
            except (NotFound, InternalServerError):
                r[p] = "Could not find part `{}`".format(p)
            else:
                r[_p.title.contents[0]] = self.mcmaster_part(p)
        for key, value in r.items():
            s += "{}: {}\n".format(key, value)
        await ctx.send(s)


def setup(bot):
    bot.add_cog(parts(bot))
