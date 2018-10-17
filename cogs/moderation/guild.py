import asyncpg
import discord
from discord.ext import commands


class guild:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def __local_check(self, ctx: commands.Context) -> bool:
        return ctx.guild is not None

    async def get_guild_data(self, guild_id: int) -> asyncpg.Record:
        async with self.bot.connect_pool.acquire() as conn:
            g_row = await conn.fetchrow(
                """SELECT * FROM guild_table WHERE guild_id = $1""", guild_id
            )
            if g_row is None:
                await conn.execute(
                    """INSERT INTO guild_table(guild_id, esrb) VALUES($1, $2)""",
                    guild_id,
                    "e10",
                )
                g_row = await conn.fetchrow(
                    """SELECT * FROM guild_table WHERE guild_id = $1""", guild_id
                )
            return g_row

    @commands.command()
    @commands.has_permissions(manage_server=True)
    async def set_rating(self, ctx: commands.Context, esrb_rating: str):
        """Set your server's "ESRB" rating for quotes."""
        if esrb_rating.lower() not in ["e", "e10", "t", "m", "ao"]:
            return await ctx.send(
                "<:xmark:314349398824058880> `{}` is not a valid ESRB-style rating!".format(
                    esrb_rating
                )
            )
        else:
            async with self.bot.connect_pool.acquire() as conn:
                await conn.execute(
                    """UPDATE guild_table SET esrb = $1 WHERE guild_id = $2""",
                    esrb_rating.lower(),
                    ctx.guild.id,
                )
            await ctx.send(
                "<:check:314349398811475968> Set rating to `{}`".format(esrb_rating)
            )

    @commands.command()
    async def get_rating(self, ctx: commands.Context):
        row = await self.get_guild_data(ctx.guild.id)
        await ctx.send(
            "This guild has its rating set at `{}`.".format(row["esrb"].upper())
        )


def setup(bot):
    bot.add_cog(guild(bot))
