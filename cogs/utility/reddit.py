import aiohttp
from discord.ext import commands

import boiler


class reddit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["multi"])
    async def multireddit(self, ctx: commands.Context, owner: str, name: str):
        await ctx.send("https://www.reddit.com/u/{}/m/{}/".format(owner, name))

    @commands.command(aliases=["u"])
    async def userinfo(self, ctx: commands.Context, user: str):
        redditor = {}
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://reddit.com/u/{}/about.json".format(user)
            ) as resp:
                if 300 > resp.status >= 200:
                    redditor = (await resp.json())["data"]
                else:
                    return await ctx.send(
                        "Could not fetch information for user `{}`!".format(user)
                    )
        em = boiler.embed_template(
            title=redditor["subreddit"]["title"]
            if redditor["subreddit"] is not None
            else redditor["name"],
            color=ctx.me.color,
        )
        em.url = "https://reddit.com/u/{}".format(user)
        em.set_thumbnail(url=redditor["icon_img"])
        em.add_field(name="Post Karma", value=redditor["link_karma"], inline=True)
        em.add_field(name="Comment Karma", value=redditor["comment_karma"], inline=True)
        await ctx.send(embed=em)


def setup(bot: commands.Bot):
    bot.add_cog(reddit(bot))
