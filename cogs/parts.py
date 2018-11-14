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
    def andy_part(part_num: str) -> str:
        return "https://andymark.com/{}".format(part_num)

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
                raise NotFound(resp, "Not found")
            else:
                raise InternalServerError(resp, "AndyMark is bad")

    async def get_mcmaster_part_page(self, part_num: str) -> BeautifulSoup:
        url = parts.mcmaster_part(part_num)
        async with self.aio_client.get(url) as resp:
            if 300 > resp.status >= 200:
                data = await resp.text()
                return BeautifulSoup(data, features="html5lib")
            elif resp.status == 404:
                raise NotFound(resp, "Not found")
            else:
                raise InternalServerError(resp, "Something went wrong at McMaster Carr")

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
            _p = None
            try:
                _p = await self.get_anymark_part_page(p)
            except (NotFound, InternalServerError):
                r[p] = "Could not find part `{}`".format(p)
            else:
                if _p.title.contents[0].lower() == "not found - andymark inc.":
                    # for some god-forsaken reason AM doesn't properly 404
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
