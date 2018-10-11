import asyncpg
import boiler
import discord
from discord.ext import commands
import json
from typing import Dict


set_description = """Sets the default permissions for creating channels with Lopez. `permissions` should be a JSON code block similar to the below.
{
  "Role": {
    "manage_messages": true
  },
  "Another Role": {
    "add_reactions": false
  }
}
Note that prettifying your JSON is not required. Lopez will tell you if it cannot find a role in the block passed.
"""


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
    ) -> Dict[str, discord.PermissionOverwrite]:
        r = {}
        for key, value in frozen.items():
            r[key] = discord.PermissionOverwrite(**frozen[key])
        return r

    @commands.command(description=set_description)
    async def set_chancreate_defaults(self, ctx: commands.Context, *, permissions: str):
        """
        Sets the default permissions for channels created with Lopez.
        """
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

    @commands.command()
    async def get_chancreate_defaults(self, ctx: commands.Context):
        """
        Posts the current default permissions for channels created with Lopez.
        """
        g_row = await self.get_guild_data(ctx.guild.id)
        current = (
            json.loads(g_row["default_permission"])
            if json.loads(g_row["default_permission"]) is not None
            else {}
        )
        if current != {}:
            readable = {}
            em = boiler.embed_template(
                "Default permissions for new channels", ctx.guild.me.color
            )
            for key, value in current.items():
                role = await self.role_converter.convert(ctx, key)
                permissions = "```\n"
                for permission, state in value.items():
                    permissions += "{}: {}\n".format(permission, state)
                permissions += "```"
                em.add_field(name=role.name, value=permissions, inline=True)
            await ctx.send(None, embed=em)
        else:
            await ctx.send(
                "Default permissions for new channels haven't been configured!"
            )

    @commands.command()
    async def create_channel(
        self, ctx: commands.Context, name: str, nsfw_: bool = False
    ):
        """
        Create a new text channel, using the stored default permissions.
        """
        g_row = await self.get_guild_data(ctx.guild.id)
        default_perms = (
            json.loads(g_row["default_permission"])
            if json.loads(g_row["default_permission"]) is not None
            else {}
        )
        f_overwrites = {}
        for role_id, overwrite in channels.thaw_permissions(default_perms).items():
            role = await self.role_converter.convert(ctx, role_id)
            f_overwrites[role] = overwrite
        chan = await ctx.guild.create_text_channel(
            name, overwrites=f_overwrites, reason="Requested by " + ctx.author.name
        )
        await chan.edit(nsfw=nsfw_)
        await ctx.send("Done! Please enjoy your new " + chan.mention)


def setup(bot: commands.Bot):
    bot.add_cog(channels(bot))
