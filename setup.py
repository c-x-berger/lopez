import asyncio
import asyncpg
import config
import json


async def safe_table_create(connection, table_exec: str):
    try:
        print(await connection.execute(table_exec))
    except asyncpg.DuplicateTableError:
        print(
            "That table already exists! If you're upgrading you can safely ignore this, if not, please drop that table and run this script again."
        )


async def main():
    print(
        "I will now attempt to connect to database {} on host {} as user {}".format(
            config.sql_db, config.sql_host, config.sql_user
        )
    )
    conn = None
    try:
        conn = await asyncpg.connect(config.postgresql)
    except asyncpg.ConnectionFailureError:
        print(
            "Could not connect. Are you sure the database {} exists?\nExiting.".format(
                config.sql_db
            )
        )
        exit(1)
    else:
        print("Connected!")
        print("Creating table dnd_chars...")
        await safe_table_create(
            conn,
            """
        CREATE TABLE dnd_chars (\
            character_id serial PRIMARY KEY,\
            name varchar NOT NULL,\
            strength smallint NOT NULL,\
            dexterity smallint NOT NULL,\
            constitution smallint NOT NULL,\
            intelligence smallint NOT NULL,\
            wisdom smallint NOT NULL,\
            charisma smallint NOT NULL,\
            race varchar NOT NULL,\
            discord_id varchar NOT NULL,\
            levels integer[],\
            classes varchar[])
        """,
        )
        print("Creating table role_table...")
        await safe_table_create(
            conn,
            """
            CREATE TABLE role_table(
                internal serial PRIMARY KEY,
                server_id bigint NOT NULL,
                available bigint[] NOT NULL,
                special bigint[] NOT NULL
            )
            """,
        )
        print("Attempting to import old role.json")
        try:
            with open("role.json", "r") as role:
                data = json.load(role)
                for key, value in data.items():
                    await conn.execute(
                        "INSERT INTO role_table(server_id, available, special) VALUES($1, $2, $3)",
                        int(key),
                        value["available"],
                        value["special"],
                    )
        except FileNotFoundError:
            print("No role.json found!")
        else:
            print("Imported role.json.")
        print("Creating table guild_table...")
        await safe_table_create(
            conn,
            """
            CREATE TABLE guild_table(
                internal serial PRIMARY KEY,
                guild_id bigint NOT NULL,
                default_permission jsonb,
                esrb varchar(5)
            )
            """,
        )
        print("Creating table timetable...")
        await safe_table_create(
            conn,
            """
            CREATE TABLE timetable(
                member bigint PRIMARY KEY,
                seconds numeric NOT NULL DEFAULT 0
            )
            """,
        )
        print("Creating table timekeeper...")
        await safe_table_create(
            conn,
            """
            CREATE TABLE timekeeper(
                member bigint PRIMARY KEY,
                time_in decimal
            )
            """,
        )
        print("Setting unique constraints and defaults...")
        # dnd table
        await conn.execute("""ALTER TABLE dnd_chars ADD UNIQUE (discord_id)""")
        for col in [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]:
            await conn.execute(
                """ALTER TABLE dnd_chars ALTER COLUMN {} SET DEFAULT 0""".format(col)
            )
        await conn.execute(
            "ALTER TABLE dnd_chars ALTER COLUMN levels SET DEFAULT '{1}'"
        )
        # role table
        await conn.execute("""ALTER TABLE role_table ADD UNIQUE (server_id)""")
        await conn.execute(
            "ALTER TABLE role_table ALTER COLUMN available SET DEFAULT '{0}'"
        )
        await conn.execute(
            "ALTER TABLE role_table ALTER COLUMN special SET DEFAULT '{0}'"
        )
        print("Done!")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
