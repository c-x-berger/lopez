import asyncpg
import boiler
import discord
from discord.ext import commands
import time
from typing import Dict


CLOCK_DESC = "Clock in or out. Note that if you're clocked in, running this without a subcommand will result in you being clocked out. In that event, simply clock back in and you won't miss any notable amount of time."
BADGE_DESC = "Get the QR code you use to clock in/out. To prevent someone else from clocking you out, the message will autodelete after five (5) seconds."
STATUS_DESC = "Show your current clock state. Includes total hours, if you're clocked in or out, and how many hours you've recorded in this session."


class timeclock:
    """
    Timeclock commands. Note that your recorded hours and clock state are GLOBAL, i.e. not per guild.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def remove_from_keeper(self, user: int):
        async with self.bot.connect_pool.acquire() as conn:
            await conn.execute("DELETE FROM timekeeper WHERE member = $1", user)

    async def add_to_keeper(self, user: int, guild_id: int, t_: int = None):
        t = time.time() if t_ is None else t_
        async with self.bot.connect_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO timekeeper(member, time_in, guild) VALUES ($1, $2, $3)",
                user,
                t,
                guild_id,
            )

    async def get_total_time(self, user: int) -> float:
        async with self.bot.connect_pool.acquire() as conn:
            rec = await conn.fetchrow(
                """SELECT seconds FROM timetable WHERE member = $1""", user
            )
            return float(rec["seconds"]) if rec is not None else 0

    @commands.command(aliases=["hours"])
    async def get_hours(self, ctx: commands.Context):
        """Display the number of hours you've reccorded."""
        seconds = await self.get_total_time(ctx.author.id)
        await ctx.send(
            "You have {:.2} hours on record, {}.".format(
                seconds / 3600.0, ctx.author.mention
            )
        )

    @commands.command(description=BADGE_DESC, aliases=["badge"])
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

    @commands.group(description=CLOCK_DESC, aliases=["in", "out"])
    async def clock(self, ctx: commands.Context):
        """Clock in/out."""
        if ctx.invoked_subcommand is not None:
            return
        elif ctx.subcommand_passed is None:
            u = ctx.author.id
            g = ctx.guild.id
            is_in = False
            async with self.bot.connect_pool.acquire() as conn:
                mem_rows = await conn.fetch(
                    "SELECT member FROM timekeeper WHERE member = $1", u
                )
                is_in = len(mem_rows) > 0
            if is_in:
                # clock out
                time_in = 0
                async with self.bot.connect_pool.acquire() as conn:
                    time_in = await conn.fetchval(
                        "SELECT time_in FROM timekeeper WHERE member = $1", u
                    )
                total = time.time() - float(time_in)
                async with self.bot.connect_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO timetable (member, seconds)
                        VALUES ($1, $2)
                        ON CONFLICT (member) DO UPDATE SET seconds = timetable.seconds + $2
                        """,
                        u,
                        total,
                    )
                await self.remove_from_keeper(u)
                await ctx.send(
                    "I have recorded {:.2} hours. You are now clocked out.".format(
                        total / 3600.0
                    )
                )
            else:
                # clock in
                await self.add_to_keeper(u, g, time.time())
                await ctx.send("You are now clocked in.")
        else:
            await ctx.invoke(self.bot.get_command("help"), "clock")

    @commands.group()
    async def force(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), "force")

    @force.command(name="in")
    @commands.has_permissions(kick_members=True)
    async def f_in(
        self, ctx: commands.Context, members: commands.Greedy[discord.Member]
    ):
        """Forcibly clock guild members in."""
        t = time.time()
        for member in members:
            try:
                await self.add_to_keeper(member.id, ctx.guild.id, t)
            except asyncpg.UniqueViolationError:
                await ctx.send("{} is already clocked in!".format(member.mention))
            else:
                await ctx.send("Clocked {} in.".format(member.mention))

    @force.command(name="out")
    @commands.has_permissions(kick_members=True)
    async def f_out(
        self, ctx: commands.Context, members: commands.Greedy[discord.Member]
    ):
        """Forcibly clock users out. They must have clocked in in this guild."""
        t = time.time()
        for member in members:
            # clock out
            time_in = 0
            async with self.bot.connect_pool.acquire() as conn:
                time_in = await conn.fetchrow(
                    "SELECT time_in, guild FROM timekeeper WHERE member = $1", member.id
                )
            if time_in["guild"] != ctx.guild.id:
                await ctx.send(
                    "Member {} didn't clock in in this guild!".format(member.mention)
                )
                continue
            total = time.time() - float(time_in["time_in"])
            async with self.bot.connect_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO timetable (member, seconds)
                    VALUES ($1, $2)
                    ON CONFLICT (member) DO UPDATE SET seconds = timetable.seconds + $2
                    """,
                    member.id,
                    total,
                )
            await self.remove_from_keeper(member.id)
            await ctx.send(
                "I have recorded {:.2} hours. {} is now clocked out.".format(
                    total / 3600.0, member.mention
                )
            )

    @clock.command(aliases=["status"], description=STATUS_DESC)
    async def state(self, ctx: commands.Context):
        """Show your current clock state."""
        session_start = None
        async with self.bot.connect_pool.acquire() as conn:
            rec = await conn.fetchrow(
                """SELECT time_in FROM timekeeper WHERE member = $1""", ctx.author.id
            )
            session_start = float(rec["time_in"]) if rec is not None else None
        total_time = await self.get_total_time(ctx.author.id)
        send = "You have {:.2} hours on record, {}.".format(
            total_time / 3600.0, ctx.author.mention
        )
        if session_start is not None:
            send += "\nYou are clocked in. In this session, you have recorded {:.2} hours so far.".format(
                (time.time() - session_start) / 3600
            )
        else:
            send += "\nYou are currently clocked out."
        await ctx.send(send)


def setup(bot: commands.Bot):
    bot.add_cog(timeclock(bot))
