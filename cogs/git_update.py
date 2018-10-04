import discord
from discord.ext import commands
import logging
import subprocess
import os
import sys
import time


class git_updater:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("cogs.git_update")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.bot.log_handler)

    @commands.command(
        description="Update the bot. Can only be done by the bot's owner.",
        aliases=["upgrade"],
    )
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        """Update the bot."""
        start_time = time.time()
        subprocess.run(["git", "pull"])
        self.logger.warning(
            "Bot is preparing for restart. Pulling bad code may cause a fail to restart!"
        )
        await ctx.send(
            "I finished pulling code in {:.2} seconds.\nRestarting now.\n`Goodbye`.".format(
                time.time() - start_time
            )
        )
        # To concerned parties:
        # The below line should not be uncommented if Lopez has been installed correctly.
        # You should only uncomment it if you're a fool who has failed to configure process management for Lopez and
        # need a hack to fix it.
        # os.execl(sys.executable, sys.executable, *sys.argv)
        self.logger.info("Shutting down...")
        await self.bot.logout()


def setup(bot: commands.Bot):
    bot.add_cog(git_updater(bot))
