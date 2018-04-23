import boiler
import json
import random
import discord
from discord.ext import commands

special_roles = ["General 3494", "Admin", "Mentors", "Alumni", "Leads", "Bot, but admin", "Bots", "Parents", "Lopez"]
footers = []
with open("footers.json") as feet:
    footers = json.load(feet)

class roles():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def competition(self, ctx, member: discord.Member = None):
        '''
        Gives the competition role
        '''
        await ctx.invoke(self.giveme, request="Competition")

    @commands.command(description="Gives you a subteam role. Available roles:\n* Programming\n* CAD/Design\n* Marketing\n* Fabrication\n* Scouts\n* Electrical\n* Drive Team\n* Outreach\n* Awards\n* Strategy\n* Field Build\n* Website\n* Memer\n* NSWC Crane bot team", pass_context=True)
    async def giveme(self, ctx, *, request: str):
        '''
        Gives the requested subteam role
        '''
        member = ctx.message.author
        role = None
        if (request not in special_roles):
            role = discord.utils.get(ctx.message.server.roles, name=request)
        else:
            await self.bot.say("You're not allowed to give yourself the {} role.".format(request))
            return
        if (role is not None):
            await self.bot.add_roles(member, role)
            await self.bot.say("Gave {} the {} role".format(member.mention, request))
        elif (request is not None):
            await self.bot.say("Could not find the role {}! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request))

    @commands.command(description="The opposite of [] giveme.", pass_context=True)
    async def removeme(self, ctx, *, request: str):
        '''
        Removes the requested subteam role
        '''
        member = ctx.message.author
        role = None
        if (request not in special_roles):
            role = discord.utils.get(ctx.message.server.roles, name=request)
        else:
            await self.bot.say("You're not allowed to remove yourself from the {} role.".format(request))
            return
        if (role is not None):
            await self.bot.add_roles(member, role)
            await self.bot.say("Took the {1} role from {0}".format(member.mention, request))
        elif (request is not None):
            await self.bot.say("Could not find the role {}! Please check for typos. If you need a list of available roles, do `[] listme`.".format(request))

    @commands.command(pass_context=True)
    async def listme(self, ctx):
        '''
        Lists all roles available with [] giveme
        '''
        em = boiler.embed_template()
        em.title = "Available roles"
        send = ""
        for role in ["Programming", "CAD/Design", "Marketing", "Fabrication", "Scouts", "Electrical", "Drive Team", "Outreach", "Awards", "Strategy", "NSWC Crane bot team"]:
            send += "* {}\n".format(role)
        em.add_field(name="Subteam roles", value=send)
        em.add_field(name="Other roles", value="* Memer\n* Field Build\n* Website")
        await self.bot.send_message(ctx.message.channel, None, embed=em)

def setup(bot):
    bot.add_cog(roles(bot))
