import asyncio
import boiler
import contextlib
import discord
from discord.ext import commands
import logging
import sys
import textwrap
import traceback
import io
import inspect
import os


class developer():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command(description='Evaluates arbitrary Python 3 code blocks. Indent with two spaces.', aliases=['evaluate', 'run'], hidden=True)
    @commands.is_owner()
    async def devalue(self, ctx: commands.Context, *, source: str):
        '''Evaluates arbitrary Python 3 code blocks.'''
        env = {  # set some shortcuts up
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }
        env.update(globals())
        source = self.cleanup_code(source)
        to_run = 'async def func():\n{}'.format(
            textwrap.indent(source, "  "))  # wrap source in async def
        ret = None
        output = io.StringIO()
        try:
            exec(to_run, env)  # executes to_run, defining func()
        except Exception as e:
            # sends traceback
            return await ctx.send('```py\n{0}: {1}\n```'.format(e.__class__.__name__, e))
        func = env['func']
        try:
            with contextlib.redirect_stdout(output):
                ret = await func()
        except Exception as e:
            # failed to run due to exception in func()
            value = output.getvalue()
            await ctx.send('```py\n{0}{1}\n```'.format(value, traceback.format_exc()))
        else:
            # all went well, send result
            self._last_result = ret
            em = boiler.embed_template("Result")
            em.description = "Python 3 code evaluation"
            if (output.getvalue() != ''):
                em.add_field(name="Output", value='```\n{}\n```'.format(
                    output.getvalue()), inline=False)
            em.add_field(name="Return value",
                         value='```\n{}\n```'.format(ret), inline=False)
            await ctx.send(None, embed=em)

    @commands.command()
    async def source(self, ctx: commands.Context, command: str = None):
        """Get the bot source or the source of a given command."""
        s_url = "https://github.com/BHSSFRC/lopez/tree/master"
        if command is None:
            return await ctx.send(s_url)

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        src = obj.callback.__code__
        lines, firstline = inspect.getsourcelines(src)
        location = ""
        if not obj.callback.__module__.startswith('discord'):
            location = os.path.relpath(src.co_filename).replace('\\', '/')
        else:
            s_url = "https://github.com/Rapptz/discord.py/tree/rewrite"
            location = obj.callback.__module__.replace('.', '/') + '.py'
        await ctx.send("{}/{}/#L{}-L{}".format(s_url, location, firstline, firstline + len(lines) - 1))


def setup(bot):
    bot.add_cog(developer(bot))
