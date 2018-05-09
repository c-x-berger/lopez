import discord
import boiler
from discord.ext import commands


class moderate():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Enables a user with Manage Messages to bulk delete the last `amount` messages.", pass_context=True)
    async def purge(self, ctx, amount: int):
        '''Bulk remove messages.'''
        if (ctx.message.channel.permissions_for(ctx.message.author).manage_messages):
            i = 0
            j = -1
            messages = list(self.bot.messages)
            while (i < amount + 1):
                if (messages[j].channel.id == ctx.message.channel.id):
                    await self.bot.delete_message(messages[j])
                    messages.remove(messages[j])
                    j = -1
                    i += 1
                else:
                    j -= 1
            em = boiler.embed_template()
            em.title = "Purged {} messages".format(i)
            if (ctx.message.author.nick is not None):
                em.set_footer(text="Requested by {}".format(
                    ctx.message.author.nick), icon_url="https://i.imgur.com/2VepakW.png")
            else:
                em.set_footer(text="Requested by {}".format(
                    ctx.message.author.name), icon_url="https://i.imgur.com/2VepakW.png")
            await self.bot.say(None, embed=em)
        else:
            await self.bot.say("Purge not performed because you ain't got the power.")


def setup(bot):
    bot.add_cog(moderate(bot))
