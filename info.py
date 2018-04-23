import boiler
import discord
from discord.ext import commands

class info:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Post info", pass_context=True)
    async def infopost(self, ctx):
        if (ctx.message.channel.id == "372457065895165952"):
            em1 = boiler.embed_template()
            em1.title = "About the server"
            em1.set_footer(text=discord.Embed.Empty)
            em1.add_field(name="Moderation", value="Your resident Admins are <@!164342765394591744>, <@!256489829473320977>, and <@!226426407952187393>. If you have an issue/suggestion about anything, feel free to bring it up with us, either here or in a direct message (DM.)", inline=False)
            em1.add_field(name="Roles", value="You will be given roles based on what you do in the team, with most being listed on the channels to the left. Notable exceptions are mentors, leads, and parents, given to people who are those things. There are also component roles, used for build season. These will be distributed by <@!436251140376494080>, and each role will have a channel for discussion on their part. There is another role, Memer, which grants access to the <#286175382682730497> channel, but that is the only hidden channel. The competition role is self assigned via Lopez, and will be used for the people who are at a competition.", inline=False)
            em1.add_field(name="Channels", value="All channels are visible to the left (again, with the exception of memes and competition). The channels under the server info category are locked to mentors and leads, since it is used for general team information, and not for conversation. <#419469024876036097> will open up when we travel, but otherwise is useless, and hidden. The subteam channels are open, (except leads, mentors), and if you are active/intrested in those topics, we encourage you to give yourself the role with Lopez. (We also recommend muting <#411246560568147969>.) <#286174293006745601> is used for conversation relating more directly to the team/robot/robotics, and <#372721765815812096> is for just hanging out, talking about whatever. <#379647663697821696> is for things we need/want, be it tools, parts, etc. When posting there, include a link to the item where possible.", inline=False)
            await self.bot.send_message(ctx.message.channel, None, embed=em1)
            em2 = boiler.embed_template()
            em2.title = "The Rules"
            em2.set_footer(text="STOP BREAKING THE LAW")
            em2.add_field(name="1. This is a team server, and we expect ALL members to act in a GP manner.", value="1a. Don't bash other people. If you have a problem with someone, either bring it up with them or a mentor\n1b. Don't bash other teams. We are all just highschool students, we all make mistakes.\n1c. If there's a problem with an idea, explain what it is and preferabily present another idea. \"It's dumb\" helps no one.")
            em2.add_field(name="2. Keep conversation relevant to the channel that you are in.", value="This keeps important things current in the channel, and the channel cluttter free.", inline=False)
            em2.add_field(name="3. Don't harass people.", value="This includes repeated pings, unprofessional conduct, etc. Use your best judgement.", inline=False)
            em2.add_field(name="4. Nicknames must be set, with your real name.", value="This is done with `/nick yournamehere` and will be enforced.", inline=False)
            em2.add_field(name="5. Profile pictures must be appropriate.", value="You don't have to set one if you dont want to.", inline=False)
            em2.add_field(name="6. Personal disagreements are not allowed here.", value="Either take it to DMs or have it in person.", inline=False)
            em2.add_field(name="Consequences", value="If these rules are broken, punishments will be made at the discretion of the admin team. Most likely, the General 3494 role will be removed, and you won't be able to see/type in channels for a length of time (to be decided as needed.)", inline=False)
            await self.bot.send_message(ctx.message.channel, None, embed=em2)
            em3 = boiler.embed_template()
            em3.url = "https://github.com/BHSSFRC/lopez"
            em3.title = "Lopez - your new best friend"
            em3.set_thumbnail(url="https://i.imgur.com/j1bnW3q.png")
            em3.set_footer(text="^_^", icon_url=discord.Embed.Empty)
            em3.add_field(name="What?", value="{0} is a bot created by {1}. It helps with various annoying administrative tasks, such as giving roles. Please be kind to him and he'll be kind to you.".format(self.bot.user.mention, "<@!164342765394591744>"), inline=False)
            em3.add_field(name="How do I use it?", value="You can have a summary of Lopez's commands delivered directly to you by doing `[] help`.")
            em3.add_field(name="Just tell me the commands!", value="Common commands include:\n* `[] competition` to give oneself the Competition role\n* `[] giveme rolename` to be given the role `rolename`\n* `[] removeme rolename` to remove yourself from `rolename`\n* `[] listme` to see roles available for use with `[] giveme` and `[] removeme`")
            await self.bot.say(None, embed=em3)
            await self.bot.say("**Server links**\nThis server: https://discord.gg/3wJUjfs\nFRC Discord: https://discord.gg/frc\nIndianaFIRST Discord: https://discord.gg/5CbEQKS\n\nKvale's room phone number is (812) 330-7714 ext. 51121")


def setup(bot):
    bot.add_cog(info(bot))
