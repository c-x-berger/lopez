import asyncpg
import boiler
import config
import discord
from discord.ext import commands
import math
import random

scores = ["STR", "DEX", "CON", "INT", "WIS", "CHR"]


def ndn(amount: str) -> list:
    '''Converts a string in ndn format into a two item list of the form [number to roll, size of dice].'''
    d = amount.split('d')
    num_roll = roller.to_int(d[0])
    die_size = roller.to_int(d[1])
    return [num_roll, die_size]


class roller():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pool = None
        self.bot.loop.create_task(self.open_connection())

    async def open_connection(self):
        self.pool = await asyncpg.create_pool(config.postgresql)

    @staticmethod
    def to_int(number: str) -> int:
        '''Really bad str -> int function not to be used outside this file.'''
        try:
            return int(number)
        except ValueError:
            return 1

    @staticmethod
    def mod_from_score(score: int) -> int:
        '''Returns a skill modifier given a DnD ability score.'''
        return math.floor((score - 10) / 2)

    @staticmethod
    def roll_ndn(dice: list) -> list:
        '''Rolls x many n sided dice, where x is dice[0] and n is dice[1].'''
        rolls = []
        for _ in range(dice[0]):
            rolls.append(random.randint(1, dice[1]))
        return rolls

    @commands.command()
    async def roll(self, ctx: commands.Context, dice: ndn):
        '''\"Straight\" rolls a die (no ability scores applied.)'''
        rolls = roller.roll_ndn(dice)
        message = "**Your rolls:**\n"
        for i in range(len(rolls)):
            roll = rolls[i]
            message += "{} + ".format(roll) if i is not len(rolls) - \
                1 else "{} = ".format(roll)
        message += "**{0!s}**".format(sum(rolls))
        await ctx.send(message)

    @commands.command()
    async def skill_check(self, ctx: commands.Context, bonus: int, dc: int = None):
        '''Rolls an ability check.'''
        message = "**You rolled:**\n"
        roll = roller.roll_ndn([1, 20])
        total = sum(roll) + bonus
        message += "{0} {3} {1} = **{2}**\n".format(
            sum(roll), abs(bonus), total, "+" if bonus >= 0 else "-")
        if dc is not None:
            message += "{} {} {}: {}".format(total, "passes DC" if total >=
                                             dc else "fails DC", dc, "Success!" if total >= dc else "You fail!")
        await ctx.send(message)

    @commands.group(description='Base character creation/modification command.\nCurrently, NO DATA is stored and these commands are for testing only.')
    async def character(self, ctx: commands.Context):
        '''Base character creation/modification command.'''
        if (ctx.invoked_subcommand is None):
            await ctx.send("You need to invoke this command with a subcommand. To see available subcommands, try `[] help character`.")

    async def retrieve_character(self, conn: asyncpg.Connection, player: discord.Member) -> asyncpg.Record:
        return await conn.fetchrow('''SELECT * FROM dnd_chars WHERE discord_id = $1''', str(player.id))

    @character.command()
    async def get(self, ctx: commands.Context, player: discord.Member = None):
        if player is None:
            player = ctx.author
        async with self.pool.acquire() as conn:
            char = await self.retrieve_character(conn, player)
            if char is not None:
                em = boiler.embed_template(char["name"])
                em.description = ''
                for i in range(len(char['classes'])):
                    em.description += "Level {} {}\n".format(
                        char['levels'][i], char['classes'][i])
                char_scores = ''
                for stat, fullname in {"STR": "strength", "DEX": "dexterity", "CON": "constitution", "INT": "intelligence", "WIS": "wisdom", "CHR": "charisma"}.items():
                    score = char[fullname]
                    modstring = "+ {}".format(roller.mod_from_score(
                        score)) if score > 9 else "- {}".format(abs(roller.mod_from_score(score)))
                    char_scores += "**{0}:** {1!s} ({2})\n".format(stat,
                                                                   score, modstring)
                em.add_field(name='Stats', value=char_scores)
                await ctx.send(None, embed=em)
            else:
                await ctx.send("Could not locate a character for {}!".format(player.display_name))

    @character.command(description="Creates a character with all properties defined in a single command.\
    \nClasses should be comma separated and wrapped in quotes.\
    \nLevels must be separated in the same way and in the same order as classes.\
    \nStats MUST be in the following order: strength, dexterity, constitution, intelligence, wisdom, charisma.\
    \nAs this is a very long command, other options will be available.")
    async def create_onecall(self, ctx: commands.Context, name: str, race: str, character_classes: boiler.comma_sep, class_levels: boiler.comma_sep, *stats):
        '''Creates a character (long form.)'''
        # HACK: For some reason character_classes occasionally becomes a string. If it's a string we make it a list instead.
        if (type(character_classes) is str):
            character_classes = [character_classes]
        em = boiler.embed_template(name)
        if (len(class_levels) != len(character_classes)):
            await ctx.send("Error in class / level list! {} classes and {} levels given".format(len(character_classes), len(class_levels)))
            return
        else:
            em.description = ''
            for i in range(len(character_classes)):
                em.description += "Level {} {}\n".format(
                    class_levels[i], character_classes[i])
        s = {}
        for i in range(len(scores)):
            s[scores[i]] = roller.to_int(stats[i])
        statblock = ""
        for stat, score in s.items():
            modstring = "+ {}".format(roller.mod_from_score(
                score)) if score > 9 else "- {}".format(abs(roller.mod_from_score(score)))
            statblock += "**{0}:** {1!s} ({2})\n".format(stat,
                                                         score, modstring)
        em.add_field(name="Stats", value=statblock)
        # prepare levels list
        int_levels = []
        for level in class_levels:
            int_levels.append(roller.to_int(level))
        async with ctx.typing():
            async with self.pool.acquire() as conn:
                try:
                    # TODO: optimize with prepared statements somehow?
                    await conn.execute('''INSERT INTO dnd_chars(name, strength, dexterity, constitution, intelligence, wisdom, charisma, race, discord_id, levels, classes) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)''',
                                       name, s["STR"], s["DEX"], s["CON"], s["INT"], s["WIS"], s["CHR"], race, str(ctx.author.id), int_levels, character_classes)
                except asyncpg.UniqueViolationError:
                    await ctx.send("You already have a character saved, and this command won't overwrite it!\n(All that construction work for nothing...)")
                    return
        await ctx.send(None, embed=em)

    @character.command(description="Creates a character with all stats set to zero.\
    \nUnder the hood, this just calls create_onecall with defaults supplied.")
    async def create_nameonly(self, ctx: commands.Context, name: str):
        '''Creates a character with all stats set to 0.'''
        await ctx.invoke(self.create_onecall, name, 'Living Creature', 'Critter', '1', 0, 0, 0, 0, 0, 0)

    @character.command(description="Modify an existing character. Coming soon to a Lopez near you.")
    async def edit(self, ctx: commands.Context, prop: str, value: str):
        '''Modify an existing character.'''
        await ctx.send("Coming soon to a Lopez near you!")
        if prop.upper() in scores or prop.lower() in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            # modify stat
            pass
        elif prop.lower() in ["race", "name"]:
            async with self.pool.acquire() as conn:
                char = await self.retrieve_character(conn, ctx.author)
                if char is not None:
                    await conn.execute('''UPDATE dnd_chars SET {} = $1 WHERE discord_id = $2'''.format(prop.lower()), value, str(ctx.author.id))
                    await ctx.send("Updated property `{}` to value `{}` for character `{}`".format(prop, value, char))


def setup(bot: commands.Bot):
    bot.add_cog(roller(bot))
