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
        guild_key = str(guild_id) # for some reason JSON only allows string keys
        guilddict = None
        try:
            guilddict = self.roledict[guild_key]
        except KeyError:
            self.roledict[guild_key] = {"available": [], "special": []}
            guilddict = self.roledict[guild_key]
        finally:
            return guilddict

    def save_dict(self):
        with open('role.json', 'w') as r:
            json.dump(self.roledict, r)

    async def __local_check(self, ctx: commands.Context) -> bool:
        return isinstance(ctx.channel, discord.TextChannel)

    @commands.command(description="Adds a role to [] giveme. Any user will be able to give themselves the role with [] giveme role. Caller must have \"Manage Roles\".")
    async def add_giveme(self, ctx, role: discord.Role):
        '''Adds a role to [] giveme'''
        if (ctx.channel.permissions_for(ctx.author).manage_roles):
            guilddict = self.get_guild_dict(ctx.guild.id)
            # add to available list
            if (role.id not in guilddict["available"]):
                guilddict["available"].append(role.id)
                if role in guilddict["special"]:
                    guilddict[ctx.guild.id]["special"].remove(role.id)
                self.save_dict()
            if not (ctx.guild.name.endswith("s") or ctx.guild.name.endswith("S")):
                await ctx.send("Added {} to {}'s giveme roles.".format(role, ctx.guild.name))
            else:
                await ctx.send("Added {} to {}' giveme roles.".format(role, ctx.guild.name))
        else:
            await ctx.send("You're not allowed to do that!")

    @commands.command(description="Removes a role from [] giveme. The role will show as not configured to users. Caller must have \"Manage Roles\".")
    async def remove_giveme(self, ctx, role: discord.Role):
        '''Removes a role from [] giveme without marking it as blocked.'''
        if (ctx.channel.permissions_for(ctx.author).manage_roles):
            guilddict = self.get_guild_dict(ctx.guild.id)
            try:
                guilddict["available"].remove(role.id)
            except ValueError:
                await ctx.send("That role wasn't in giveme to begin with!")
            else:
                self.save_dict()
                await ctx.send("Removed {} from giveme roles.".format(role.name))
        else:
            await ctx.send("You're not allowed to do that!")

    @commands.command(description='Blocks a role from [] giveme. The role will show as "special", and users will not be able to give them to or remove them from themselves. Caller must have "Manage Roles".')
    async def add_special(self, ctx, role: discord.Role):
        '''Blocks a role from [] giveme and [] removeme.'''
        if (ctx.channel.permissions_for(ctx.author).manage_roles):
            guilddict = self.get_guild_dict(ctx.guild.id)
            if (role.id not in guilddict["special"]):
                guilddict["special"].append(role.id)
                if role in guilddict["available"]:
                    guilddict["available"].remove(role.id)
                self.save_dict()
            if not (ctx.guild.name.endswith("s") or ctx.guild.name.endswith("S")):
                await ctx.send("Blocked {} from {}'s giveme roles.".format(role.name, ctx.guild.name))
            else:
                await ctx.send("Blocked {} from {}' giveme roles.".format(role.name, ctx.guild.name))
        else:
            await ctx.send("You're not allowed to do that!")

    @commands.command(description="Unblocks a role from [] giveme. The role will show as not configured to users. Caller must have \"Manage Roles\".")
    async def remove_special(self, ctx, role: discord.Role):
        '''Unblocks a role from [] giveme and [] removeme.'''
        if (ctx.channel.permissions_for(ctx.author).manage_roles):
            guilddict = self.get_guild_dict(ctx.guild.id)
            try:
                guilddict["special"].remove(role.id)
            except ValueError:
                await ctx.send("That role wasn't blocked to begin with!")
            else:
                self.save_dict()
                await ctx.send("Unblocked {} from giveme roles.".format(role.name))
        else:
            await ctx.send("You're not allowed to do that!")

    @commands.command()
    async def competition(self, ctx, member: discord.Member = None):
        '''Gives the competition role. (3494 guild only.)'''
        if (ctx.guild.id == 286174293006745601):
            await ctx.invoke(self.giveme, request="Competition")

    @commands.command()
    async def giveme(self, ctx, *, request: discord.Role):
        '''Gives the requested role.'''
        available = self.get_guild_dict(ctx.guild.id)["available"]
        special_roles = self.get_guild_dict(ctx.guild.id)["special"]
        member = ctx.author
        if (request.id in available):
            await member.add_roles(request)
            await ctx.send("Gave {} the {} role".format(member.mention, request.name))
        elif (request in special_roles):
            await ctx.send("You're not allowed to give yourself the {} role.".format(request.name))
        elif (request is not None):
            await ctx.send("Could not find the role {}! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request.name))

    @commands.command(description="The opposite of [] giveme.")
    async def removeme(self, ctx, *, request: discord.Role):
        '''Removes the requested role.'''
        available = self.get_guild_dict(ctx.guild.id)["available"]
        special_roles = self.get_guild_dict(ctx.guild.id)["special"]
        member = ctx.author
        if (request.id in available):
            await member.remove_roles(request)
            await ctx.send("Took the {1} role from {0}".format(member.mention, request.name))
        elif (request in special_roles):
            await ctx.send("You're not allowed to remove yourself from the {} role.".format(request.name))
        elif (request is not None):
            await ctx.send("Could not find the role {} in any list for this guild! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request.name))

    @commands.command()
    async def listme(self, ctx: commands.Context):
        '''Lists all roles available with [] giveme.'''
        guilddict = self.get_guild_dict(ctx.guild.id)
        em = boiler.embed_template("List of Roles")
        em.description = "May not be all-encompassing. Only includes roles a guild moderator has set the status of."
        send = ""
        for role_id in guilddict["available"]:
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role is not None:
                send += "* {}\n".format(role.name)
        if (send is not ""):
            em.add_field(name="Available roles", value=send, inline=True)
        send = ""
        for role_id in guilddict["special"]:
            role = discord.utils.get(ctx.guild.roles, id=role_id)
            if role is not None:
                send += "* {}\n".format(role.name)
        if (send is not ""):
            em.add_field(name="Roles blocked from giveme",
                         value=send, inline=True)
        if (len(em.fields) > 0):
            await ctx.send(None, embed=em)
        else:
            await ctx.send("No roles configured!")


def setup(bot):
    bot.add_cog(roles(bot))
