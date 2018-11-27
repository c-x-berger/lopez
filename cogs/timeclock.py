import asyncio
import asyncpg
import boiler
import discord
from discord.ext import commands
import time
from typing import Dict, Optional


CLOCK_DESC = "Clock in or out. Note that if you're clocked in, running this without a subcommand will result in you being clocked out. In that event, simply clock back in and you won't miss any notable amount of time."
BADGE_DESC = "Get the QR code you use to clock in/out. To prevent someone else from clocking you out, the message will autodelete after five (5) seconds."
STATUS_DESC = "Show your current clock state. Includes total hours, if you're clocked in or out, and how many hours you've recorded in this session."


class timeclock:
    """
    Timeclock commands. Hours and in/out state are recorded per guild.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def remove_from_keeper(self, user: int, guild: int):
        async with self.bot.connect_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM timekeeper WHERE member = $1 AND guild = $2", user, guild
            )

    async def add_to_keeper(self, user: int, guild_id: int, t_: int = None):
        async with self.bot.connect_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO timekeeper(member, time_in, guild) VALUES ($1, $2, $3)",
                user,
                t_ if t_ is not None else time.time(),
                guild_id,
            )

    async def get_total_time(self, user: int, guild: int) -> float:
        async with self.bot.connect_pool.acquire() as conn:
            rec = await conn.fetchrow(
                """SELECT seconds FROM timetable WHERE member = $1 AND guild = $2""",
                user,
                guild,
            )
            return float(rec["seconds"]) if rec is not None else 0

    async def add_time_to_table(self, user: int, guild: int, seconds: float):
        async with self.bot.connect_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO timetable (member, seconds, guild) VALUES ($1, $2, $3) ON CONFLICT (member, guild) DO UPDATE SET seconds = timetable.seconds + $2",
                user,
                seconds,
                guild,
            )

    @commands.command(aliases=["hours"])
    async def get_hours(self, ctx: commands.Context):
        """Display the number of hours you've reccorded."""
        seconds = await self.get_total_time(ctx.author.id, ctx.guild.id)
        await ctx.send(
            "You have {} hours on record, {}.".format(
                round(seconds / 3600.0, 2), ctx.author.mention
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

    @commands.group(description=CLOCK_DESC)
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
                    "SELECT member FROM timekeeper WHERE member = $1 AND guild = $2",
                    u,
                    g,
                )
                is_in = len(mem_rows) > 0
            if is_in:
                # clock out
                time_in = 0
                async with self.bot.connect_pool.acquire() as conn:
                    time_in = await conn.fetchval(
                        "SELECT time_in FROM timekeeper WHERE member = $1 AND guild = $2",
                        u,
                        g,
                    )
                total = time.time() - float(time_in)
                await self.add_time_to_table(u, g, total)
                await self.remove_from_keeper(u, g)
                await ctx.send(
                    "I have recorded {} hours. You are now clocked out.".format(
                        round(total / 3600.0, 2)
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
            time_in = None
            async with self.bot.connect_pool.acquire() as conn:
                time_in = await conn.fetchval(
                    "SELECT time_in FROM timekeeper WHERE member = $1 AND guild = $2",
                    member.id,
                    ctx.guild.id,
                )
            if time_in is None:
                await ctx.send(
                    "Member {} isn't clocked in for this guild!".format(member.mention)
                )
            else:
                total = time.time() - float(time_in)
                await self.add_time_to_table(member.id, ctx.guild.id, total)
                await self.remove_from_keeper(member.id, ctx.guild.id)
                await ctx.send(
                    "I have recorded {} hours. {} is now clocked out.".format(
                        round(total / 3600.0, 2), member.mention
                    )
                )

    @clock.command(aliases=["status"], description=STATUS_DESC)
    async def state(self, ctx: commands.Context):
        """Show your current clock state."""
        session_start = None
        async with self.bot.connect_pool.acquire() as conn:
            rec = await conn.fetchrow(
                """SELECT time_in FROM timekeeper WHERE member = $1 AND guild = $2""",
                ctx.author.id,
                ctx.guild.id,
            )
            session_start = float(rec["time_in"]) if rec is not None else None
        total_time = await self.get_total_time(ctx.author.id, ctx.guild.id)
        send = "You have {} hours on record, {}.".format(
            round(total_time / 3600.0, 2), ctx.author.mention
        )
        if session_start is not None:
            send += "\nYou are clocked in. In this session, you have recorded {} hours so far.".format(
                round((time.time() - session_start) / 3600.0, 2)
            )
        else:
            send += "\nYou are currently clocked out."
        await ctx.send(send)

    @clock.command()
    async def add_hours(
        self,
        ctx: commands.Context,
        hours: float,
        member: Optional[discord.Member] = None,
    ):
        """Add hours to members (or yourself, if no member is specified.)"""
        if member is not None:
            # changing someone else
            if ctx.author.guild_permissions.kick_members:
                await self.add_time_to_table(member.id, ctx.guild.id, hours * 3600.0)
                await ctx.send(
                    "Added {} hours to the log for {}. Whether they have clocked in or not has **not** been changed.".format(
                        hours, member.mention
                    )
                )
            else:
                await ctx.send("You don't have the power (Kick Members) to do that!")
        else:
            # changing self
            if hours > 0:
                m = await ctx.send(
                    "I CANNOT READ MINDS. I ASSUME YOU ARE BEING HONEST. Since you're adding to your own hours, you must react to this message with \N{ALARM CLOCK} in the next five (5) seconds as acknowledgement that you're not cheating."
                )
                await m.add_reaction("\N{ALARM CLOCK}")
                try:

                    def c(reaction, user):
                        return (
                            user == ctx.author
                            and str(reaction.emoji) == "\N{ALARM CLOCK}"
                        )

                    reaction, user = await self.bot.wait_for(
                        "reaction_add", timeout=5.0, check=c
                    )
                except asyncio.TimeoutError:
                    return await ctx.send("Too slow!")
                else:
                    # proceed with adding hours
                    await ctx.send(
                        "I'm now adding {} hours to your log. Better not be lying to me!".format(
                            str(hours)
                        )
                    )
                    await self.add_time_to_table(
                        ctx.author.id, ctx.guild.id, hours * 3600.0
                    )


def setup(bot: commands.Bot):
    bot.add_cog(timeclock(bot))
