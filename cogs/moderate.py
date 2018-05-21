import discord
import boiler
from discord.ext import commands


class moderate():
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Enables a user with Manage Messages to bulk delete the last `amount` messages.", pass_context=True)
    async def purge(self, ctx: commands.Context, amount: int):
        '''Bulk remove messages.'''
        channel = ctx.message.channel
        author = ctx.message.author 
        if (channel.permissions_for(author).manage_messages):
            i = 0
            await self.bot.delete_message(ctx.message)
            async for m in self.bot.logs_from(channel, limit=amount):
                await self.bot.delete_message(m)
                i += 1
            em = boiler.embed_template()
            em.title = "Purged {} messages".format(i)
            if (author.nick is not None):
                em.set_footer(text="Requested by {}".format(
                    author.nick), icon_url="https://i.imgur.com/2VepakW.png")
            else:
                em.set_footer(text="Requested by {}".format(
                    author.name), icon_url="https://i.imgur.com/2VepakW.png")
            await self.bot.say(None, embed=em)
        else:
            await self.bot.say("Purge not performed because you ain't got the power.")


def setup(bot):
    bot.add_cog(moderate(bot))
