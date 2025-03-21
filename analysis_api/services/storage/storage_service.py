import aiosqlite
        

async def initialise_db(db: aiosqlite.Connection):
    """Creates the required database tables if they don't exist."""

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

        try:
            await self.db.execute(insert_statement, data_to_insert)
            await self.db.commit()
        except aiosqlite.IntegrityError:
            raise StorageServiceException(f"Track ID '{track_id}' already exists.")
        except aiosqlite.OperationalError as e:
            raise StorageServiceException(f"Database operation failed - {e}")
        except aiosqlite.DatabaseError as e:
            raise StorageServiceException(f"Unexpected database error - {e}")

    async def retrieve_profile(self, track_id: str) -> dict | None:
        select_query = f"""
            SELECT * FROM Profile 
            WHERE track_id = ?
        """

        try:
            cursor = await self.db.execute(select_query, (track_id,))
            row = await cursor.fetchone()

            if row is None:
                return None

            _, *emotions = row
            emotion_names = [description[0] for description in cursor.description][1:]
            profile = dict(zip(emotion_names, emotions))

            return profile
        except aiosqlite.OperationalError as e:
            raise StorageServiceException(f"Database operation failed - {e}")
        except aiosqlite.DatabaseError as e:
            raise StorageServiceException(f"Unexpected database error - {e}")

    async def store_tags(self, track_id: str, tags: str):
        insert_statement = f"""
            INSERT INTO Tags (track_id, tags)
            VALUES (?, ?);
        """

        data_to_insert = (track_id, tags)

        try:
            await self.db.execute(insert_statement, data_to_insert)
            await self.db.commit()
        except aiosqlite.IntegrityError:
            raise StorageServiceException(f"Track ID '{track_id}' already exists.")
        except aiosqlite.OperationalError as e:
            raise StorageServiceException(f"Database operation failed - {e}")
        except aiosqlite.DatabaseError as e:
            raise StorageServiceException(f"Unexpected database error - {e}")

    async def retrieve_tags(self, track_id: str) -> str | None:
        select_query = f"""
            SELECT * FROM Tags 
            WHERE track_id = ?
        """

        try:
            cursor = await self.db.execute(select_query, (track_id,))
            row = await cursor.fetchone()
            tags = row[1] if row else None

            return tags
        except aiosqlite.OperationalError as e:
            raise StorageServiceException(f"Database operation failed - {e}")
        except aiosqlite.DatabaseError as e:
            raise StorageServiceException(f"Unexpected database error - {e}")
