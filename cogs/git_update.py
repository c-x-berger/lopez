import discord
from discord.ext import commands
import logging
import subprocess
import os
import sys
import time


class git_updater():
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def update(self, ctx: commands.Context):
        '''
        Update the bot. Can only be done by the almighty one, the Maker.
        '''
        if (ctx.author.id == self.bot.owner_id):
            start_time = time.time()
            subprocess.run(["git", "pull"])
            finish_time = time.time()
            logging.warning(
                "Bot is preparing for restart. Pulling bad code may cause a fail to restart!")
            await ctx.send("I finished pulling code in {:.2} seconds.\nRestarting now.\n`Goodbye`.".format(finish_time - start_time))
            os.execl(sys.executable, sys.executable, *sys.argv)


def setup(bot: commands.Bot):
    bot.add_cog(git_updater(bot))
