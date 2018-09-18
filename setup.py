import asyncio
import asyncpg
import config


async def main():
    print('I will now attempt to connect to database {} on host {} as user {}'.format(
        config.sql_db, config.sql_host, config.sql_user))
    conn = None
    try:
        conn = await asyncpg.connect(config.postgresql)
    except asyncpg.ConnectionFailureError:
        print("Could not connect. Are you sure the database {} exists?\nExiting.".format(
            config.sql_db))
        exit(1)
    else:
        print('Connected!')
        print('Creating table dnd_chars...')
        try:
            print(await conn.execute('''CREATE TABLE dnd_chars (\
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
                    classes varchar[]
                )'''))
        except asyncpg.exceptions.DuplicateTableError:
            print("That table already exists! If you're upgrading you can safely ignore this, if not, please drop that table and run this script again.")
        print('Creating table role_table...')
        print(await conn.execute('''CREATE TABLE role_table(
            internal serial PRIMARY KEY,
            server_id bigint NOT NULL,
            available bigint[] NOT NULL,
            special bigint[] NOT NULL
        )'''))
        print('Setting unique constraints and defaults...')
        # dnd table
        await conn.execute('''ALTER TABLE dnd_chars ADD UNIQUE (discord_id)''')
        for col in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            await conn.execute('''ALTER TABLE dnd_chars ALTER COLUMN {} SET DEFAULT 0'''.format(col))
        await conn.execute("ALTER TABLE dnd_chars ALTER COLUMN levels SET DEFAULT '{1}'")
        # role table
        await conn.execute('''ALTER TABLE role_table ADD UNIQUE (server_id)''')
        await conn.execute("ALTER TABLE role_table ALTER COLUMN available SET DEFAULT '{0}'")
        await conn.execute("ALTER TABLE role_table ALTER COLUMN special SET DEFAULT '{0}'")
        print('Done!')

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
