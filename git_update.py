import discord
from discord.ext import commands
import subprocess
import os
import sys
import time


class git_updater():
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def update(self, ctx):
        '''
        Update the bot. Can only be done by the almighty one, the Maker.
        '''
        if (ctx.message.author.id == "164342765394591744"):
            start_time = time.time()
            subprocess.run(["git", "pull"])
            finish_time = time.time()
            await self.bot.say("I finished pulling code in {} seconds.\nRestarting now.\n`Goodbye`.".format(finish_time - start_time))
            os.execl(sys.executable, sys.executable, *sys.argv)

def setup(bot):
    bot.add_cog(git_updater(bot))
