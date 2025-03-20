import aiosqlite
        

async def initialise_db(db_path: str):
    """Creates the required database tables if they don't exist."""

    async with aiosqlite.connect(db_path) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS Profile (
                track_id TEXT PRIMARY KEY,
                joy REAL, 
                sadness REAL, 
                anger REAL, 
                fear REAL, 
                love REAL,
                hope REAL, 
                nostalgia REAL, 
                loneliness REAL, 
                confidence REAL,
                despair REAL, 
                excitement REAL, 
                mystery REAL, 
                defiance REAL,
                gratitude REAL, 
                spirituality REAL
            );

            CREATE TABLE IF NOT EXISTS Tags (
                track_id TEXT PRIMARY KEY,
                tags TEXT
            );
        """)

        await db.commit()

        select_query = """SELECT name FROM sqlite_master WHERE type='table'"""

        async with db.execute(select_query) as cursor:
            tables = await cursor.fetchall()
            print(f"{tables = }")


class StorageServiceException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class StorageService:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def store_profile(self, track_id: str, profile: dict):
        insert_statement = f"""
            INSERT INTO Profile (
                track_id, 
                joy, 
                sadness, 
                anger, 
                fear, 
                love, 
                hope, 
                nostalgia, 
                loneliness, 
                confidence, 
                despair, 
                excitement, 
                mystery, 
                defiance, 
                gratitude, 
                spirituality
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        data_to_insert = (track_id, *profile.values())

        await self.db.execute(insert_statement, data_to_insert)
        await self.db.commit()

    async def retrieve_profile(self, track_id: str) -> dict | None:
        select_query = f"""
            SELECT * FROM Profile 
            WHERE track_id = ?
        """

        async with self.db.execute(select_query, (track_id, )) as cursor:
            row = await cursor.fetchone()

            if row is None:
                return None

            _, *emotions = row
            emotion_names = [description[0] for description in cursor.description][1:]
            data = dict(zip(emotion_names, emotions))

            return data

    async def store_tags(self, track_id: str, tags: str):
        insert_statement = f"""
            INSERT INTO Tags (track_id, tags)
            VALUES (?, ?);
        """

        data_to_insert = (track_id, tags)

        await self.db.execute(insert_statement, data_to_insert)
        await self.db.commit()

    async def retrieve_tags(self, track_id: str) -> str | None:
        select_query = f"""
            SELECT * FROM Tags 
            WHERE track_id = ?
        """

        async with self.db.execute(select_query, (track_id, )) as cursor:
            row = await cursor.fetchone()

            if row is None:
                return None

            _, tags = row

            return tags
