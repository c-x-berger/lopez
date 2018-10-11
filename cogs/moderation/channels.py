import asyncpg
import boiler
import discord
from discord.ext import commands
import json
from typing import Dict


class channels:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role_converter = commands.RoleConverter()

    async def __local_check(self, ctx: commands.Context) -> bool:
        return isinstance(ctx.channel, discord.TextChannel)

    async def get_guild_data(self, guild_id: int) -> asyncpg.Record:
        async with self.bot.connect_pool.acquire() as conn:
            g_row = await conn.fetchrow(
                """SELECT * FROM channels_table WHERE guild_id = $1""", guild_id
            )
            if g_row is None:
                await conn.execute(
                    """INSERT INTO channels_table(guild_id, default_permission) VALUES($1, $2)""",
                    guild_id,
                    "{}",
                )
                g_row = await conn.fetchrow(
                    """SELECT * FROM channels_table WHERE guild_id = $1""", guild_id
                )
            return g_row

    @staticmethod
    def thaw_permissions(
        frozen: Dict[str, Dict[str, bool]]
    ) -> Dict[int, discord.PermissionOverwrite]:
        r = {}
        for key, value in frozen:
            r[int(key)] = discord.PermissionOverwrite(**frozen[key])
        return r

    @commands.command()
    async def set_chancreate_defaults(self, ctx: commands.Context, *, permissions: str):
        perms_namekeys = json.loads(boiler.cleanup_code(permissions))
        perms_idkeys = {}
        for key, value in perms_namekeys.items():
            newkey = 0
            try:
                role = await self.role_converter.convert(ctx, key)
                newkey = str(role.id)
            except commands.BadArgument:
                await ctx.send("Could not find the role {} - skipping!".format(key))
            else:
                perms_idkeys[newkey] = value
        g_row = await self.get_guild_data(ctx.guild.id)
        current = (
            json.loads(g_row["default_permission"])
            if json.loads(g_row["default_permission"]) is not None
            else {}
        )
        current.update(perms_idkeys)
        async with self.bot.connect_pool.acquire() as conn:
            await conn.set_type_codec(
                "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
            )
            await conn.execute(
                """UPDATE channels_table SET default_permission = $1::jsonb WHERE guild_id = $2""",
                current,
                ctx.guild.id,
            )
        await ctx.send("```json\n" + str(current) + "\n```")


def setup(bot: commands.Bot):
    bot.add_cog(channels(bot))
