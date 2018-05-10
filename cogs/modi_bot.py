import discord
from discord.ext import commands


class modi():
    def __init__(self, bot: commands.Bot, special_cogs: list):
        self.bot = bot
        self.special_cogs = special_cogs

    @commands.group(pass_context=True, description="Base command for module tinkering.\nMust be invoked with a subcommand. Can only be invoked by the bot's creator.")
    async def mod(self, ctx):
        '''Base command for all module tinkering.'''
        if (ctx.invoked_subcommand is None):
            await self.bot.say("This command must be invoked with a subcommand (`unload`, `load`, or `reload`)!")

    @mod.command(pass_context=True, description="Load a module. This assumes that the module exists in `cogs/`.")
    async def load(self, ctx, module: str):
        '''Load a module.'''
        if (ctx.message.author.id == "164342765394591744" and module not in self.special_cogs):
            module = "cogs." + module
            self.bot.load_extension(module)
            await self.bot.say("Loaded `{}`".format(module))

    @mod.command(pass_context=True, description="Unloads a module. This operation has no special conditions.")
    async def unload(self, ctx, module: str):
        '''Unload a module.'''
        if (ctx.message.author.id == "164342765394591744" and module not in self.special_cogs):
            self.bot.unload_extension(module)
            await self.bot.say("Unloaded `{}`".format(module))

    @mod.command(pass_context=True, description='Reload a module. Technically, just calls the unload and load commands.')
    async def reload(self, ctx, module: str):
        '''Reload a module.'''
        await ctx.invoke(self.unload, module)
        await ctx.invoke(self.load, module)


def setup(bot: commands.Bot):
    bot.add_cog(modi(bot, ["main", "modi_bot"]))
