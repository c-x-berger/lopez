import asyncio
import boiler
import contextlib
import discord
from discord.ext import commands
import sys
import StringIO

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yeild stdout
    sys.stdout = old


class developer:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command('Evaluates arbitrary Python 3 code blocks.')
    async def devalue(ctx: commands.Context, source: str):
        if (bot.is_owner(ctx.author)):
            # clean up source
            if source.startswith("\n"):
                source = source[1:] # trim off leading \n
            for leader in ['\n```', '\n```python']:
                if source.startswith(leader):
                    source = source[len(leader):-3]
                    break
            ret = None
            with stdoutIO() as output:
                try:
                    ret = eval(source)
                except Exception as e:
                    print("error: {}".format(e))
            em = boiler.embed_template()
            em.title = "Result"
            em.description = "Python 3 code evaluation"
            em.add_field(name="Output", value='```\n{}\n```'.format(output.getvalue()), inline=False)
            em.add_field(name="Return value", value='```\n{}\n```'.format(ret), inline=False)
            await ctx.send(None, embed=em)
        else:
            pass

def setup(bot):
    bot.add_cog(developer(bot))

