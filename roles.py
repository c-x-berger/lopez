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

    @commands.command(description="Gives the competition role", pass_context=True)
    async def competition(self, ctx, member: discord.Member = None):
        member = ctx.message.author
        await self.bot.add_roles(member, discord.utils.get(ctx.message.server.roles, name="Competition"))
        await self.bot.say("Gave {} the competition role".format(member.mention))

    @commands.command(description="Gives the requested subteam role", pass_context=True)
    async def giveme(self, ctx, *, request: str):
        """
        Gives you a subteam role. Available roles:
        * Programming
        * CAD/Design
        * Marketing
        * Fabrication
        * Scouts
        * Electrical
        * Drive Team
        * Outreach
        * Awards
        * Strategy
        * Field Build
        * Website
        * Memer
        * NSWC Crane bot team
        """
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

    @commands.command(description="The opposite of [] giveme", pass_context=True)
    async def removeme(self, ctx, *, request: str):
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

    @commands.command(description="Lists all roles available with [] giveme", pass_context=True)
    async def listme(self, ctx):
        em = discord.Embed()
        em.title = "Available roles"
        em.color = discord.Colour.gold()
        em.set_footer(text=random.choice(footers))
        send = ""
        for role in ["Programming", "CAD/Design", "Marketing", "Fabrication", "Scouts", "Electrical", "Drive Team", "Outreach", "Awards", "Strategy", "NSWC Crane bot team"]:
            send += "* {}\n".format(role)
        em.add_field(name="Subteam roles", value=send)
        em.add_field(name="Other roles", value="* Memer\n* Field Build\n* Website")
        await self.bot.send_message(ctx.message.channel, None, embed=em)

def setup(bot):
    bot.add_cog(roles(bot))