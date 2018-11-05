import boiler
from discord.ext import commands


class timeclock:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        description="Get the QR code you use to clock in/out. To prevent someone else from clocking you out, the message will autodelete after five (5) seconds.",
        aliases=["badge"],
    )
    async def get_badge(self, ctx: commands.Context):
        """Get the QR code you use to clock in/out."""
        em = boiler.embed_template("", ctx.me.color)
        em.set_image(
            url="https://api.qrserver.com/v1/create-qr-code/?data=" + str(ctx.author.id)
        )
        em.description = "Here's your badge, {}! [Get it as a vector here.]({})".format(
            ctx.author.mention,
            "https://api.qrserver.com/v1/create-qr-code/?data="
            + str(ctx.author.id)
            + "&format=svg",
        )
        await ctx.send(None, embed=em, delete_after=5)


def setup(bot: commands.Bot):
    bot.add_cog(timeclock(bot))
