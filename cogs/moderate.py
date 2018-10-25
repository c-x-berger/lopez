import discord
import boiler
from discord.ext import commands


class moderate:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.command(
        description="Enables a user with Manage Messages to bulk delete the last `amount` messages.",
        aliases=["delete"],
    )
    async def purge(self, ctx: commands.Context, amount: int):
        """Bulk remove messages."""
        async with ctx.typing():
            deleted = await ctx.channel.purge(limit=amount + 1)
        em = boiler.embed_template(
            "Purged {} messages".format(len(deleted)), ctx.me.color
        )
        em.set_footer(
            text="Requested by {}".format(ctx.author.display_name),
            icon_url="https://i.imgur.com/2VepakW.png",
        )
        await ctx.send(None, embed=em, delete_after=5 if len(deleted) <= 5 else None)


def setup(bot):
    bot.add_cog(moderate(bot))
