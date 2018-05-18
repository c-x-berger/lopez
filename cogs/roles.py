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

    def get_server_dict(self, i: str) -> dict:
        serverdict = None
        try:
            serverdict = self.roledict[i]
        except KeyError:
            self.roledict[i] = {"available": [], "special": []}
            serverdict = self.roledict[i]
        finally:
            return serverdict

    @commands.command(pass_context=True, description="Adds a role to [] giveme. Any user will be able to give themselves the role with [] giveme role. Caller must have \"Manage Roles\".")
    async def add_giveme(self, ctx, role: str):
        '''Adds a role to [] giveme'''
        if (ctx.message.channel.type == discord.ChannelType.text):
            if (ctx.message.channel.permissions_for(ctx.message.author).manage_roles):
                serverdict = self.get_server_dict(ctx.message.server.id)
                # add to available list
                if (role not in serverdict["available"]):
                    serverdict["available"].append(role)
                    if role in serverdict["special"]:
                        serverdict[ctx.message.server.id]["special"].remove(
                            role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                if not (ctx.message.server.name.endswith("s") or ctx.message.server.name.endswith("S")):
                    await self.bot.say("Added {} to {}'s giveme roles.".format(role, ctx.message.server.name))
                else:
                    await self.bot.say("Added {} to {}' giveme roles.".format(role, ctx.message.server.name))
            else:
                await self.bot.say("You're not allowed to do that!")

    @commands.command(pass_context=True, description="Removes a role from [] giveme. The role will show as not configured to users. Caller must have \"Manage Roles\".")
    async def remove_giveme(self, ctx, role: str):
        '''Removes a role from [] giveme without marking it as blocked.'''
        if (ctx.message.channel.type == discord.ChannelType.text):
            if (ctx.message.channel.permissions_for(ctx.message.author).manage_roles):
                serverdict = self.get_server_dict(ctx.message.server.id)
                try:
                    serverdict["available"].remove(role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                    await self.bot.say("Removed {} from giveme roles.".format(role))
                except ValueError:
                    await self.bot.say("That role wasn't in giveme to begin with!")
            else:
                await self.bot.say("You're not allowed to do that!")

    @commands.command(pass_context=True, description='Blocks a role from [] giveme. The role will show as "special", and users will not be able to give them to or remove them from themselves. Caller must have "Manage Roles".')
    async def add_special(self, ctx, role: str):
        '''Blocks a role from [] giveme and [] removeme.'''
        if (ctx.message.channel.type == discord.ChannelType.text):
            if (ctx.message.channel.permissions_for(ctx.message.author).manage_roles):
                serverdict = self.get_server_dict(ctx.message.server.id)
                if (role not in serverdict["special"]):
                    serverdict["special"].append(role)
                    if role in serverdict["available"]:
                        serverdict["available"].remove(role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                if not (ctx.message.server.name.endswith("s") or ctx.message.server.name.endswith("S")):
                    await self.bot.say("Blocked {} from {}'s giveme roles.".format(role, ctx.message.server.name))
                else:
                    await self.bot.say("Blocked {} from {}' giveme roles.".format(role, ctx.message.server.name))
            else:
                await self.bot.say("You're not allowed to do that!")

    @commands.command(pass_context=True, description="Unblocks a role from [] giveme. The role will show as not configured to users. Caller must have \"Manage Roles\".")
    async def remove_special(self, ctx, role: str):
        '''Unblocks a role from [] giveme and [] removeme.'''
        if (ctx.message.channel.type == discord.ChannelType.text):
            if (ctx.message.channel.permissions_for(ctx.message.author).manage_roles):
                serverdict = self.get_server_dict(ctx.message.server.id)
                try:
                    serverdict["special"].remove(role)
                    with open("role.json", 'w') as r:
                        json.dump(self.roledict, r, indent=4)
                    await self.bot.say("Unblocked {} from giveme roles.".format(role))
                except ValueError:
                    await self.bot.say("That role wasn't blocked to begin with!")
            else:
                await self.bot.say("You're not allowed to do that!")

    @commands.command(pass_context=True)
    async def competition(self, ctx, member: discord.Member = None):
        '''Gives the competition role. (3494 server only.)'''
        if (ctx.message.server.id == "286174293006745601"):
            await ctx.invoke(self.giveme, request="Competition")

    @commands.command(pass_context=True)
    async def giveme(self, ctx, *, request: str):
        '''Gives the requested role.'''
        if (ctx.message.channel.type == discord.ChannelType.text):
            available = self.get_server_dict(ctx.message.server.id)["available"]
            special_roles = self.get_server_dict(ctx.message.server.id)["special"]
            member = ctx.message.author
            role = None
            if (request in available):
                role = discord.utils.get(
                    ctx.message.server.roles, name=request)
                await self.bot.add_roles(member, role)
                await self.bot.say("Gave {} the {} role".format(member.mention, request))
            elif (request in special_roles):
                await self.bot.say("You're not allowed to give yourself the {} role.".format(request))
            elif (request is not None):
                await self.bot.say("Could not find the role {}! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request))
        else:
            await self.bot.say("Cannot run role commands in a direct message!")

    @commands.command(description="The opposite of [] giveme.", pass_context=True)
    async def removeme(self, ctx, *, request: str):
        '''Removes the requested role.'''
        if (ctx.message.channel.type == discord.ChannelType.text):
            available = self.get_server_dict(ctx.message.server.id)["available"]
            special_roles = self.get_server_dict(ctx.message.server.id)["special"]
            member = ctx.message.author
            role = None
            if (request in available):
                role = discord.utils.get(
                    ctx.message.server.roles, name=request)
                await self.bot.remove_roles(member, role)
                await self.bot.say("Took the {1} role from {0}".format(member.mention, request))
            elif (request in special_roles):
                await self.bot.say("You're not allowed to remove yourself from the {} role.".format(request))
            elif (request is not None):
                await self.bot.say("Could not find the role {} in any list for this server! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request))
        else:
            await self.bot.say("Cannot run role commands in a direct message!")

    @commands.command(pass_context=True)
    async def listme(self, ctx):
        '''Lists all roles available with [] giveme.'''
        if (ctx.message.channel.type == discord.ChannelType.text):
            serverdict = self.get_server_dict(ctx.message.server.id)
            em = boiler.embed_template()
            em.title = "List of Roles"
            em.description = "May not be all-encompassing. Only includes roles a server moderator has set the status of."
            send = ""
            for role in serverdict["available"]:
                send += "* {}\n".format(role)
            if (send is not ""):
                em.add_field(name="Available roles", value=send, inline=True)
            send = ""
            for role in serverdict["special"]:
                send += "* {}\n".format(role)
            if (send is not ""):
                em.add_field(name="Roles blocked from giveme",
                             value=send, inline=True)
            if (len(em.fields) > 0):
                await self.bot.send_message(ctx.message.channel, None, embed=em)
            else:
                await self.bot.say("No roles configured!")


def setup(bot):
    bot.add_cog(roles(bot))
