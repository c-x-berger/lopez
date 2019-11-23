import math
import random

import asyncpg
import discord
from discord.ext import commands

import boiler

scores = ["STR", "DEX", "CON", "INT", "WIS", "CHR"]


def ndn(amount: str) -> list:
    """Converts a string in ndn format into a two item list of the form [number to roll, size of dice]."""
    d = amount.split("d")
    num_roll = roller.to_int(d[0])
    die_size = roller.to_int(d[1])
    return [num_roll, die_size]


class roller(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def to_int(number: str) -> int:
        """Really bad str -> int function not to be used outside this file."""
        try:
            return int(number)
        except ValueError:
            return 1

    @staticmethod
    def mod_from_score(score: int) -> int:
        """Returns a skill modifier given a DnD ability score."""
        return math.floor((score - 10) / 2)

    @staticmethod
    def roll_ndn(dice: list) -> list:
        """Rolls x many n sided dice, where x is dice[0] and n is dice[1]."""
        rolls = []
        for _ in range(dice[0]):
            rolls.append(random.randint(1, dice[1]))
        return rolls

    @commands.command()
    async def roll(self, ctx: commands.Context, dice: ndn):
        """\"Straight\" rolls a die (no ability scores applied.)"""
        rolls = roller.roll_ndn(dice)
        message = "**Your rolls:**\n"
        for i in range(len(rolls)):
            roll = rolls[i]
            message += (
                "{} + ".format(roll)
                if i is not len(rolls) - 1
                else "{} = ".format(roll)
            )
        message += "**{0!s}**".format(sum(rolls))
        await ctx.send(message)

    @commands.command(
        description="Rolls an ability check.\nDoes not currently use stored characters."
    )
    async def skill_check(self, ctx: commands.Context, bonus: int, dc: int = None):
        """Rolls an ability check."""
        message = "**You rolled:**\n"
        roll = roller.roll_ndn([1, 20])
        total = sum(roll) + bonus
        message += "{0} {3} {1} = **{2}**\n".format(
            sum(roll), abs(bonus), total, "+" if bonus >= 0 else "-"
        )
        if dc is not None:
            message += "{} {} {}: {}".format(
                total,
                "passes DC" if total >= dc else "fails DC",
                dc,
                "Success!" if total >= dc else "You fail!",
            )
        await ctx.send(message)

    @commands.group(case_insensitive=True)
    async def character(self, ctx: commands.Context):
        """Base character creation/modification command."""
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "You need to invoke this command with a subcommand. To see available subcommands, try `[] help character`."
            )

    @staticmethod
    async def retrieve_character(
        conn: asyncpg.Connection, player: discord.Member
    ) -> asyncpg.Record:
        return await conn.fetchrow(
            """SELECT * FROM dnd_chars WHERE discord_id = $1""", str(player.id)
        )

    @staticmethod
    async def no_character(ctx: commands.Context, player: discord.Member = None):
        if player is None:
            player = ctx.author
        await ctx.send(
            "Could not locate a character for {}!".format(player.display_name)
        )

    @character.command()
    async def get(self, ctx: commands.Context, player: discord.Member = None):
        """Displays a user\'s character."""
        char = None
        async with self.bot.connect_pool.acquire() as conn:
            char = await roller.retrieve_character(
                conn, player if player is not None else ctx.author
            )
        if char is not None:
            em = boiler.embed_template(char["name"], ctx.me.color)
            em.description = ""
            for i in range(len(char["classes"])):
                em.description += "Level {} {}\n".format(
                    char["levels"][i], char["classes"][i]
                )
            char_scores = ""
            for stat, fullname in {
                "STR": "strength",
                "DEX": "dexterity",
                "CON": "constitution",
                "INT": "intelligence",
                "WIS": "wisdom",
                "CHR": "charisma",
            }.items():
                score = char[fullname]
                modstring = (
                    "+ {}".format(roller.mod_from_score(score))
                    if score > 9
                    else "- {}".format(abs(roller.mod_from_score(score)))
                )
                char_scores += "**{0}:** {1!s} ({2})\n".format(stat, score, modstring)
            em.add_field(name="Stats", value=char_scores)
            await ctx.send(embed=em)
        else:
            await roller.no_character(ctx, player)

    @character.command(
        description="Creates a character with all properties defined in a single command.\nClasses should be comma separated and wrapped in quotes.\nLevels must be separated in the same way and in the same order as classes.\nStats MUST be in the following order: strength, dexterity, constitution, intelligence, wisdom, charisma.\nAs this is a very long command, other options will be available."
    )
    async def create_onecall(
        self,
        ctx: commands.Context,
        name: str,
        race: str,
        character_classes: boiler.comma_sep,
        class_levels: boiler.comma_sep,
        *stats
    ):
        """Creates a character (long form.)"""
        # HACK: For some reason character_classes occasionally becomes a string. If it's a string we make it a list instead.
        if type(character_classes) is str:
            character_classes = [character_classes]
        em = boiler.embed_template(name, ctx.me.color)
        if len(class_levels) != len(character_classes):
            await ctx.send(
                "Error in class / level list! {} classes and {} levels given".format(
                    len(character_classes), len(class_levels)
                )
            )
            return
        else:
            em.description = ""
            for i in range(len(character_classes)):
                em.description += "Level {} {}\n".format(
                    class_levels[i], character_classes[i]
                )
        s = {}
        for i in range(len(scores)):
            s[scores[i]] = roller.to_int(stats[i])
        statblock = ""
        for stat, score in s.items():
            modstring = (
                "+ {}".format(roller.mod_from_score(score))
                if score > 9
                else "- {}".format(abs(roller.mod_from_score(score)))
            )
            statblock += "**{0}:** {1!s} ({2})\n".format(stat, score, modstring)
        em.add_field(name="Stats", value=statblock)
        # prepare levels list
        int_levels = []
        for level in class_levels:
            int_levels.append(roller.to_int(level))
        async with ctx.typing():
            async with self.bot.connect_pool.acquire() as conn:
                try:
                    # TODO: optimize with prepared statements somehow?
                    await conn.execute(
                        "INSERT INTO dnd_chars(name, strength, dexterity, constitution, intelligence, wisdom, charisma, race, discord_id, levels, classes) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
                        name,
                        s["STR"],
                        s["DEX"],
                        s["CON"],
                        s["INT"],
                        s["WIS"],
                        s["CHR"],
                        race,
                        str(ctx.author.id),
                        int_levels,
                        character_classes,
                    )
                except asyncpg.UniqueViolationError:
                    await ctx.send(
                        "You already have a character saved, and this command won't overwrite it!\n(All that construction work for nothing...)"
                    )
                    return
        await ctx.send(embed=em)

    @character.command(
        description="Creates a character with all stats set to zero.\nYou can use the edit command to fix the default values supplied.\nUnder the hood, this just calls create_onecall with defaults supplied.",
        aliases=["create"],
    )
    async def create_nameonly(self, ctx: commands.Context, name: str):
        """Creates a character with all stats set to 0."""
        await ctx.invoke(
            self.create_onecall,
            name,
            "Living Creature",
            "Critter",
            "1",
            0,
            0,
            0,
            0,
            0,
            0,
        )

    @character.command(
        description="Modify an existing character. Please note that for the time being, the full name (e.g. 'intelligence') must be used to modify stat scores."
    )
    async def edit(self, ctx: commands.Context, prop: str, value: str):
        """Modify an existing character."""
        to_send = ""
        async with self.bot.connect_pool.acquire() as conn:
            char = await roller.retrieve_character(conn, ctx.author)
            if char is not None:
                if prop.lower() in [
                    "strength",
                    "dexterity",
                    "constitution",
                    "intelligence",
                    "wisdom",
                    "charisma",
                ]:
                    # modify stat
                    await conn.execute(
                        "UPDATE dnd_chars SET {} = $1 WHERE discord_id = $2".format(
                            prop.lower()
                        ),
                        roller.to_int(value),
                        str(ctx.author.id),
                    )
                    to_send = "Set stat {} to {} for character {}".format(
                        prop.lower(), value, char["name"]
                    )
                elif prop.lower() in ["race", "name"]:
                    await conn.execute(
                        "UPDATE dnd_chars SET {} = $1 WHERE discord_id = $2".format(
                            prop.lower()
                        ),
                        value,
                        str(ctx.author.id),
                    )
                    to_send = "Set {} to {} for character {}".format(
                        prop, value, char["name"]
                    )
                await ctx.send(to_send)
            else:
                await roller.no_character(ctx)

    @character.command()
    async def edit_levels(
        self, ctx: commands.Context, character_class: str, level: int
    ):
        """Sets a character as having a number of levels in a given class."""
        async with self.bot.connect_pool.acquire() as conn:
            char = await roller.retrieve_character(conn, ctx.author)
            if char is not None:
                classlevel_index = None
                try:
                    # Python has correct (0-based) indexing, Postgres does not
                    # this line is also a "sign of database misdesign" according to the Postgres people,
                    # but multiclassing in the first place is dumb
                    classlevel_index = char["classes"].index(character_class) + 1
                except ValueError:
                    classlevel_index = len(char["classes"]) + 1
                    # since we didn't already have this class, we need to add it to the list
                    await conn.execute(
                        "UPDATE dnd_chars SET classes[{}] = $1 WHERE discord_id = $2".format(
                            classlevel_index
                        ),
                        character_class,
                        str(ctx.author.id),
                    )
                finally:
                    await conn.execute(
                        "UPDATE dnd_chars SET levels[{}] = $1 WHERE discord_id = $2".format(
                            classlevel_index
                        ),
                        level,
                        str(ctx.author.id),
                    )
                    await ctx.send(
                        "Set character {} to a level {} {} (in addition to their other classes and levels.)".format(
                            char["name"], level, character_class
                        )
                    )
            else:
                await roller.no_character(ctx)

    @character.command()
    async def remove_class(self, ctx: commands.Context, character_class: str):
        """Removes a class from a character."""
        async with self.bot.connect_pool.acquire() as conn:
            char = await roller.retrieve_character(conn, ctx.author)
            if char is not None and character_class in char["classes"]:
                classes = char["classes"]
                levels = char["levels"]
                classlevel_index = classes.index(character_class)
                del classes[classlevel_index]
                del levels[classlevel_index]
                await conn.execute(
                    "UPDATE dnd_chars SET classes = $1 WHERE discord_id = $2",
                    classes,
                    str(ctx.author.id),
                )
                await conn.execute(
                    "UPDATE dnd_chars SET levels = $1 WHERE discord_id = $2",
                    levels,
                    str(ctx.author.id),
                )
            elif char is not None:
                await ctx.send("Your character does not have that class!")
            else:
                await roller.no_character(ctx)


def setup(bot: commands.Bot):
    bot.add_cog(roller(bot))
