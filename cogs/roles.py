import asyncpg
import discord
from discord.ext import commands

import boiler


class roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_guild_dict(self, guild_id: int) -> asyncpg.Record:
        async with self.bot.connect_pool.acquire() as conn:
            g_row = await conn.fetchrow(
                """SELECT * FROM role_table WHERE server_id = $1""", guild_id
            )
            if g_row is None:
                await conn.execute(
                    """INSERT INTO role_table(server_id, available, special) VALUES($1, $2, $3)""",
                    guild_id,
                    [],
                    [],
                )
                g_row = await conn.fetchrow(
                    """SELECT * FROM role_table WHERE server_id = $1""", guild_id
                )
            return g_row

    async def cog_check(self, ctx: commands.Context) -> bool:
        return boiler.guild_only_localcheck(ctx)

    @commands.command(
        description='Adds a role to giveme. Any user will be able to give themselves the role with giveme <role>. Caller must have "Manage Roles".'
    )
    @commands.has_permissions(manage_roles=True)
    async def add_giveme(self, ctx: commands.Context, *, role: discord.Role):
        """Adds a role to giveme"""
        async with self.bot.connect_pool.acquire() as conn:
            await conn.execute(
                """UPDATE role_table SET available = available || $1 WHERE server_id = $2""",
                [role.id],
                ctx.guild.id,
            )
            await conn.execute(
                """UPDATE role_table SET special = array_remove(special, $1) WHERE server_id = $2""",
                role.id,
                ctx.guild.id,
            )
        if not (ctx.guild.name.endswith("s") or ctx.guild.name.endswith("S")):
            await ctx.send(
                "Added {} to {}'s giveme roles.".format(role, ctx.guild.name)
            )
        else:
            await ctx.send("Added {} to {}' giveme roles.".format(role, ctx.guild.name))

    @commands.command(
        description='Removes a role from giveme. The role will show as not configured to users. Caller must have "Manage Roles".'
    )
    @commands.has_permissions(manage_roles=True)
    async def remove_giveme(self, ctx: commands.Context, *, role: discord.Role):
        """Removes a role from giveme without marking it as blocked."""
        guilddict = await self.get_guild_dict(ctx.guild.id)
        if role.id not in guilddict["available"]:
            await ctx.send("That role wasn't in giveme to begin with!")
            return
        else:
            # do stuff
            async with self.bot.connect_pool.acquire() as conn:
                await conn.execute(
                    """UPDATE role_table SET available = array_remove(available, $1) WHERE server_id = $2""",
                    role.id,
                    ctx.guild.id,
                )
            await ctx.send("Removed {} from giveme roles.".format(role.name))

    @commands.command(
        description='Blocks a role from giveme. The role will show as "special", and users will not be able to give them to or remove them from themselves. Caller must have "Manage Roles".'
    )
    @commands.has_permissions(manage_roles=True)
    async def add_special(self, ctx: commands.Context, *, role: discord.Role):
        """Blocks a role from giveme."""
        async with self.bot.connect_pool.acquire() as conn:
            await conn.execute(
                """UPDATE role_table SET available = array_remove(available, $1) WHERE server_id = $2""",
                role.id,
                ctx.guild.id,
            )
            await conn.execute(
                """UPDATE role_table SET special = special || $1 WHERE server_id = $2""",
                [role.id],
                ctx.guild.id,
            )
        if not (ctx.guild.name.endswith("s") or ctx.guild.name.endswith("S")):
            await ctx.send(
                "Blocked {} from {}'s giveme roles.".format(role.name, ctx.guild.name)
            )
        else:
            await ctx.send(
                "Blocked {} from {}' giveme roles.".format(role.name, ctx.guild.name)
            )

    @commands.command(
        description='Unblocks a role from giveme. The role will show as not configured to users. Caller must have "Manage Roles".'
    )
    @commands.has_permissions(manage_roles=True)
    async def remove_special(self, ctx: commands.Context, *, role: discord.Role):
        """Unblocks a role from giveme."""
        guilddict = await self.get_guild_dict(ctx.guild.id)
        if role.id not in guilddict["special"]:
            await ctx.send("That role wasn't blocked to begin with!")
        else:
            async with self.bot.connect_pool.acquire() as conn:
                await conn.execute(
                    """UPDATE role_table SET special = array_remove(special, $1) WHERE server_id = $2""",
                    role.id,
                    ctx.guild.id,
                )
            await ctx.send("Unblocked {} from giveme roles.".format(role.name))

    @commands.command()
    async def competition(self, ctx: commands.Context):
        """Gives the competition role. (3494 guild only.)"""
        if ctx.guild.id == 286174293006745601:
            await ctx.invoke(
                self.giveme,
                request=discord.utils.get(ctx.guild.roles, name="Competition"),
            )

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    async def giveme(self, ctx: commands.Context, *, request: discord.Role):
        """Gives the requested role."""
        g_dict = await self.get_guild_dict(ctx.guild.id)
        available = g_dict["available"]
        special_roles = g_dict["special"]
        member = ctx.author
        if request.id in available:
            await member.add_roles(request)
            await ctx.send("Gave {} the {} role".format(member.mention, request.name))
        elif request.id in special_roles:
            await ctx.send(
                "You're not allowed to give yourself the {} role.".format(request.name)
            )
        elif request is not None:
            await ctx.send(
                "Could not find the role {} in any list for this guild! Please check for typos. If you need a list of available roles, do `[] listme`.".format(
                    request.name
                )
            )

    @commands.command()
    @boiler.bot_and_invoke_hasperms(manage_roles=True)
    async def assign(
        self, ctx: commands.Context, target: discord.Member, *roles: discord.Role
    ):
        roles = list(roles)
        for role in roles[:]:
            if role.position >= ctx.author.top_role.position:
                await ctx.send(
                    "You don't have the power to manage the `{}` role!".format(
                        role.name
                    )
                )
                roles.remove(role)
        if not roles:
            return
        await target.add_roles(*roles, reason="Requested by " + ctx.author.name)
        s_roles = ""
        for i in range(len(roles)):
            if i != len(roles) - 1 and i != len(roles) - 2:
                s_roles += "`{}`, ".format(roles[i].name)
            elif i == len(roles) - 2:
                s_roles += "`{}`, and ".format(roles[i].name)
            else:
                s_roles += "`{}`".format(roles[i].name)
        await ctx.send("Gave {} the {} role(s)".format(target.mention, s_roles))

    @commands.command()
    @boiler.bot_and_invoke_hasperms(manage_roles=True)
    async def remove(
        self, ctx: commands.Context, target: discord.Member, *roles: discord.Role
    ):
        roles = list(roles)
        for role in roles[:]:
            if role.position >= ctx.author.top_role.position:
                await ctx.send(
                    "You don't have the power to manage the `{}` role!".format(
                        role.name
                    )
                )
                roles.remove(role)
        if not roles:
            return
        await target.remove_roles(*roles, reason="Requested by " + ctx.author.name)
        s_roles = ""
        for i in range(len(roles)):
            if i != len(roles) - 1 and i != len(roles) - 2:
                s_roles += "`{}`, ".format(roles[i].name)
            elif i == len(roles) - 2:
                s_roles += "`{}`, and ".format(roles[i].name)
            else:
                s_roles += "`{}`".format(roles[i].name)
        await ctx.send("Took the {1} role(s) from {0}".format(target.mention, s_roles))

    @commands.command(description="The opposite of giveme.")
    @commands.bot_has_permissions(manage_roles=True)
    async def removeme(self, ctx: commands.Context, *, request: discord.Role):
        """Removes the requested role."""
        g_dict = await self.get_guild_dict(ctx.guild.id)
        available = g_dict["available"]
        special_roles = g_dict["special"]
        member = ctx.author
        if request.id in available:
            await member.remove_roles(request)
            await ctx.send(
                "Took the {1} role from {0}".format(member.mention, request.name)
            )
        elif request.id in special_roles:
            await ctx.send(
                "You're not allowed to remove yourself from the {} role.".format(
                    request.name
                )
            )
        elif request is not None:
            await ctx.send(
                "Could not find the role {} in any list for this guild! Please check for typos. If you need a list of available roles, do `[] listme`.".format(
                    request.name
                )
            )

    @commands.command(aliases=["rolelist"])
    async def listme(self, ctx: commands.Context):
        """Lists all roles available with giveme."""
        guilddict = await self.get_guild_dict(ctx.guild.id)
        em = boiler.embed_template("List of Roles", ctx.me.color)
        em.description = "May not be all-encompassing. Only includes roles a guild moderator has set the status of."
        send = ""
        for role_id in guilddict["available"]:
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role is not None:
                send += "* {}\n".format(role.name)
        if send != "":
            em.add_field(name="Available roles", value=send, inline=True)
        send = ""
        for role_id in guilddict["special"]:
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role is not None:
                send += "* {}\n".format(role.name)
        if send != "":
            em.add_field(name="Roles blocked from giveme", value=send, inline=True)
        if len(em.fields) > 0:
            await ctx.send(embed=em)
        else:
            await ctx.send("No roles configured!")

    @commands.command(aliases=["lusers", "rollcall"])
    async def listusers(self, ctx: commands.Context, *, role: discord.Role):
        """Get a list of users with the role `role`."""
        em = boiler.embed_template("Users with role {}".format(role.name), ctx.me.color)
        em.description = ""
        for m in role.members:
            em.description += m.mention + "\n"
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(roles(bot))
