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

    @commands.command(pass_context=True)
    async def competition(self, ctx, member: discord.Member = None):
        '''
        Gives the competition role
        '''
        if (ctx.message.server.id == "286174293006745601"):
            await ctx.invoke(self.giveme, request="Competition")

    @commands.command(description="Gives you a subteam role.", pass_context=True)
    async def giveme(self, ctx, *, request: str):
        '''
        Gives the requested subteam role
        '''
        if (ctx.message.channel.type == discord.ChannelType.text):
            try:
                available = self.roledict[ctx.message.server.id]["available"]
                special_roles = self.roledict[ctx.message.server.id]["special"]
            except KeyError:
                await self.bot.say("No roles found for this server!")
                return
            member = ctx.message.author
            role = None
            if (request in available):
                role = discord.utils.get(ctx.message.server.roles, name=request)
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
        '''
        Removes the requested subteam role
        '''
        if (ctx.message.channel.type == discord.ChannelType.text):
            try:
                available = self.roledict[ctx.message.server.id]["available"]
                special_roles = self.roledict[ctx.message.server.id]["special"]
            except KeyError:
                await self.bot.say("No roles found for this server!")
                return  
            member = ctx.message.author
            role = None
            if (request in available):
                role = discord.utils.get(ctx.message.server.roles, name=request)
                await self.bot.remove_roles(member, role)
                await self.bot.say("Took the {1} role from {0}".format(member.mention, request)) 
            elif (request in special_roles):
                await self.bot.say("You're not allowed to remove yourself from the {} role.".format(request))
            elif (request is not None):
                await self.bot.say("Could not find the role {}! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request))
        else:
            await self.bot.say("Cannot run role commands in a direct message!")

    @commands.command(pass_context=True)
    async def listme(self, ctx):
        '''
        Lists all roles available with [] giveme
        '''
        em = boiler.embed_template()
        em.title = "Available roles"
        send = ""
        for role in self.roledict[ctx.message.server.id]["available"]:
            send += "* {}\n".format(role)
        em.add_field(name="Available roles", value=send)
        await self.bot.send_message(ctx.message.channel, None, embed=em)


def setup(bot):
    bot.add_cog(roles(bot))
