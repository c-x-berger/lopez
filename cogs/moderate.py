import discord
import boiler
from discord.ext import commands


class moderate():
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Enables a user with Manage Messages to bulk delete the last `amount` messages.")
    async def purge(self, ctx: commands.Context, amount: int):
        '''Bulk remove messages.'''
        channel = ctx.message.channel
        author = ctx.message.author 
        if (!channel.permissions_for(self.bot).manage_messages):
            await ctx.send("I am not allowed to do that!")
            return
        elif (channel.permissions_for(author).manage_messages):
            i = 0
            await ctx.message.delete()
            async with ctx.typing():
                async for m in ctx.history(limit=amount):
                    await m.delete()
                    i += 1
            em = boiler.embed_template()
            em.title = "Purged {} messages".format(i)
            if (author.nick is not None):
                em.set_footer(text="Requested by {}".format(
                    author.nick), icon_url="https://i.imgur.com/2VepakW.png")
            else:
                em.set_footer(text="Requested by {}".format(
                    author.name), icon_url="https://i.imgur.com/2VepakW.png")
                await ctx.send(None, embed=em, delete_after=5 if i <= 5 else None)
        else:
            await ctx.send("Purge not performed because you ain't got the power.")


def setup(bot):
    bot.add_cog(moderate(bot))
