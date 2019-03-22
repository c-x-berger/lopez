import discord
from discord.ext import commands
import logging


class modi(commands.Cog):
    def __init__(self, bot: commands.Bot, special_cogs: list):
        self.bot = bot
        self.logger = logging.getLogger("cogs.modi_bot")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.bot.log_handler)
        self.special_cogs = special_cogs

    @commands.group(
        description="Base command for module tinkering.\nMust be invoked with a subcommand. Can only be invoked by the bot's creator.",
        case_insensitive=True,
    )
    @commands.is_owner()
    async def mod(self, ctx: commands.Context):
        """Base command for all module tinkering."""
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "This command must be invoked with a subcommand (`unload`, `load`, or `reload`)!"
            )

    @mod.command()
    async def load(self, ctx: commands.Context, module: str):
        """Load a module."""
        self.logger.info("Loading " + module + "...")
        if module not in self.special_cogs:
            self.bot.load_extension(module)
            self.logger.info("Loaded " + module)
            await ctx.send("Loaded `{}`".format(module))

    @mod.command()
    async def unload(self, ctx: commands.Context, module: str):
        """Unload a module."""
        self.logger.info("Unloading " + module + "...")
        if module not in self.special_cogs:
            self.bot.unload_extension(module)
            self.logger.info("Unloaded " + module)
            await ctx.send("Unloaded `{}`".format(module))

    @mod.command(description="Reload a module.")
    async def reload(self, ctx: commands.Context, module: str):
        """Reload a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send("Could not reload `{}`: {}".format(module, str(e)))


def setup(bot: commands.Bot):
    bot.add_cog(modi(bot, ["main", "cogs.modi_bot"]))
