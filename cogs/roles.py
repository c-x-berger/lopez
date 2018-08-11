import boiler
import json
import random
import discord
from discord.ext import commands


class roles():
    def __init__(self, bot):
        self.bot = bot
        self.roledict = None
        with open("role.json") as r:
            self.roledict = json.load(r)

    def get_guild_dict(self, guild_id: int) -> dict:
        guild_key = str(guild_id)
        guilddict = None
        try:
            guilddict = self.roledict[guild_key]
        except KeyError:
            self.roledict[guild_key] = {"available": [], "special": []}
            guilddict = self.roledict[guild_key]
        finally:
            return guilddict

    @commands.command(description="Adds a role to [] giveme. Any user will be able to give themselves the role with [] giveme role. Caller must have \"Manage Roles\".")
    async def add_giveme(self, ctx, role: str):
        '''Adds a role to [] giveme'''
        if (isinstance(ctx.channel, discord.TextChannel)):
            if (ctx.channel.permissions_for(ctx.author).manage_roles):
                guilddict = self.get_guild_dict(ctx.guild.id)
                # add to available list
                if (role not in guilddict["available"]):
                    guilddict["available"].append(role)
                    if role in guilddict["special"]:
                        guilddict[ctx.guild.id]["special"].remove(
                            role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                if not (ctx.guild.name.endswith("s") or ctx.guild.name.endswith("S")):
                    await ctx.send("Added {} to {}'s giveme roles.".format(role, ctx.guild.name))
                else:
                    await ctx.send("Added {} to {}' giveme roles.".format(role, ctx.guild.name))
            else:
                await ctx.send("You're not allowed to do that!")

    @commands.command(description="Removes a role from [] giveme. The role will show as not configured to users. Caller must have \"Manage Roles\".")
    async def remove_giveme(self, ctx, role: str):
        '''Removes a role from [] giveme without marking it as blocked.'''
        if (isinstance(ctx.channel, discord.TextChannel)):
            if (ctx.channel.permissions_for(ctx.author).manage_roles):
                guilddict = self.get_guild_dict(ctx.guild.id)
                try:
                    guilddict["available"].remove(role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                    await ctx.send("Removed {} from giveme roles.".format(role))
                except ValueError:
                    await ctx.send("That role wasn't in giveme to begin with!")
            else:
                await ctx.send("You're not allowed to do that!")

    @commands.command(description='Blocks a role from [] giveme. The role will show as "special", and users will not be able to give them to or remove them from themselves. Caller must have "Manage Roles".')
    async def add_special(self, ctx, role: str):
        '''Blocks a role from [] giveme and [] removeme.'''
        if (isinstance(ctx.channel, discord.TextChannel)):
            if (ctx.channel.permissions_for(ctx.author).manage_roles):
                guilddict = self.get_guild_dict(ctx.guild.id)
                if (role not in guilddict["special"]):
                    guilddict["special"].append(role)
                    if role in guilddict["available"]:
                        guilddict["available"].remove(role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                if not (ctx.guild.name.endswith("s") or ctx.guild.name.endswith("S")):
                    await ctx.send("Blocked {} from {}'s giveme roles.".format(role, ctx.guild.name))
                else:
                    await ctx.send("Blocked {} from {}' giveme roles.".format(role, ctx.guild.name))
            else:
                await ctx.send("You're not allowed to do that!")

    @commands.command(description="Unblocks a role from [] giveme. The role will show as not configured to users. Caller must have \"Manage Roles\".")
    async def remove_special(self, ctx, role: str):
        '''Unblocks a role from [] giveme and [] removeme.'''
        if (isinstance(ctx.channel, discord.TextChannel)):
            if (ctx.channel.permissions_for(ctx.author).manage_roles):
                guilddict = self.get_guild_dict(ctx.guild.id)
                try:
                    guilddict["special"].remove(role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                    await ctx.send("Unblocked {} from giveme roles.".format(role))
                except ValueError:
                    await ctx.send("That role wasn't blocked to begin with!")
            else:
                await ctx.send("You're not allowed to do that!")

    @commands.command()
    async def competition(self, ctx, member: discord.Member = None):
        '''Gives the competition role. (3494 guild only.)'''
        if (ctx.guild.id == 286174293006745601):
            await ctx.invoke(self.giveme, request="Competition")

    @commands.command()
    async def giveme(self, ctx, *, request: str):
        '''Gives the requested role.'''
        if (isinstance(ctx.channel, discord.TextChannel)):
            available = self.get_guild_dict(ctx.guild.id)["available"]
            special_roles = self.get_guild_dict(ctx.guild.id)["special"]
            member = ctx.author
            role = None
            if (request in available):
                role = discord.utils.get(
                    ctx.guild.roles, name=request)
                await self.bot.add_roles(member, role)
                await ctx.send("Gave {} the {} role".format(member.mention, request))
            elif (request in special_roles):
                await ctx.send("You're not allowed to give yourself the {} role.".format(request))
            elif (request is not None):
                await ctx.send("Could not find the role {}! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request))
        else:
            await ctx.send("Cannot run role commands in a direct message!")

    @commands.command(description="The opposite of [] giveme.")
    async def removeme(self, ctx, *, request: str):
        '''Removes the requested role.'''
        if (isinstance(ctx.channel, discord.TextChannel)):
            available = self.get_guild_dict(ctx.guild.id)["available"]
            special_roles = self.get_guild_dict(ctx.guild.id)["special"]
            member = ctx.author
            role = None
            if (request in available):
                role = discord.utils.get(
                    ctx.guild.roles, name=request)
                await self.bot.remove_roles(member, role)
                await ctx.send("Took the {1} role from {0}".format(member.mention, request))
            elif (request in special_roles):
                await ctx.send("You're not allowed to remove yourself from the {} role.".format(request))
            elif (request is not None):
                await ctx.send("Could not find the role {} in any list for this guild! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request))
        else:
            await ctx.send("Cannot run role commands in a direct message!")

    @commands.command()
    async def listme(self, ctx):
        '''Lists all roles available with [] giveme.'''
        if (isinstance(ctx.channel, discord.TextChannel)):
            guilddict = self.get_guild_dict(ctx.guild.id)
            em = boiler.embed_template()
            em.title = "List of Roles"
            em.description = "May not be all-encompassing. Only includes roles a guild moderator has set the status of."
            send = ""
            for role in guilddict["available"]:
                send += "* {}\n".format(role)
            if (send is not ""):
                em.add_field(name="Available roles", value=send, inline=True)
            send = ""
            for role in guilddict["special"]:
                send += "* {}\n".format(role)
            if (send is not ""):
                em.add_field(name="Roles blocked from giveme",
                             value=send, inline=True)
            if (len(em.fields) > 0):
                await self.bot.send_message(ctx.channel, None, embed=em)
            else:
                await ctx.send("No roles configured!")


def setup(bot):
    bot.add_cog(roles(bot))
