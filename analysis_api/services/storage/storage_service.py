import aiosqlite
from loguru import logger
        

async def initialise_db(db: aiosqlite.Connection):
    """
    Creates the required database tables if they do not exist.

    This function initializes the database by creating two tables:
    - `Profile`: Stores emotional attributes for a track.
    - `Tags`: Stores tags associated with a track.

    Parameters
    ----------
    db : aiosqlite.Connection
        The SQLite database connection.

    Raises
    ------
    aiosqlite.Error
        If an error occurs while creating the table.
    """

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
            track_id TEXT,
            emotion TEXT,
            tags TEXT,
            PRIMARY KEY (track_id, emotion)
        );
    """)

    await db.commit()


class StorageServiceException(Exception):
    """
    Custom exception for errors in the StorageService.

    This exception is raised when database operations fail due to integrity, operational or unexpected database errors.
    """

    def __init__(self, message: str):
        super().__init__(message)


class StorageService:
    """
    Provides methods to store and retrieve track-related data from an SQLite database.

    This service manages two types of data:
    - `Profile`: Stores various emotional attributes associated with a track.
    - `Tags`: Stores descriptive tags for a track.

    Attributes
    ----------
    db : aiosqlite.Connection
        The SQLite database connection used for executing queries.

    Methods
    -------
    store_profile(track_id: str, profile: dict)
        Stores a track's emotional profile in the database.
    retrieve_profile(track_id: str) -> dict | None
        Retrieves a track's emotional profile from the database.
    store_tags(track_id: str, tags: str)
        Stores tags associated with a track in the database.
    retrieve_tags(track_id: str) -> str | None
        Retrieves tags associated with a track from the database.
    """

    def __init__(self, db: aiosqlite.Connection):
        """
        Attributes
        ----------
        db : aiosqlite.Connection
            The SQLite database connection.
        """

        self.db = db

    async def store_profile(self, track_id: str, profile: dict[str, float]):
        """
        Stores a track's emotional profile in the database.

        Parameters
        ----------
        track_id : str
            The unique identifier for the track.
        profile : dict
            A dictionary containing emotional attributes as keys and their values as floats.

        Raises
        ------
        StorageServiceException
            If the track ID already exists or if a database error occurs.
        """

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
        """
        Retrieves a track's emotional profile from the database.

        Parameters
        ----------
        track_id : str
            The unique identifier for the track.

        Returns
        -------
        dict or None
            A dictionary containing the track's emotional attributes if found, otherwise None.

        Raises
        ------
        StorageServiceException
            If a database error occurs.
        """

        select_query = f"""
            SELECT * FROM Profile 
            WHERE track_id = ?;
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

    async def store_tags(self, track_id: str, emotion: str, tags: str):
        """
        Stores tags associated with a track in the database.

        Parameters
        ----------
        track_id : str
            The unique identifier for the track.
        emotion : str
            The emotion the tags represent.
        tags : str
            The emotional tags for the track.

            The emotional tags are original lyrics of the track with certain phrases wrapped in <span> tags, where the
            class names correspond to the detected emotion.

        Raises
        ------
        StorageServiceException
            If the track ID already exists or if a database error occurs.
        """

        insert_statement = f"""
            INSERT INTO Tags (track_id, emotion, tags)
            VALUES (?, ?, ?);
        """

        data_to_insert = (track_id, emotion, tags)

        try:
            await self.db.execute(insert_statement, data_to_insert)
            await self.db.commit()
        except aiosqlite.IntegrityError:
            raise StorageServiceException(f"Entry already exists with track ID '{track_id}' and emotion '{emotion}'.")
        except aiosqlite.OperationalError as e:
            raise StorageServiceException(f"Database operation failed - {e}")
        except aiosqlite.DatabaseError as e:
            raise StorageServiceException(f"Unexpected database error - {e}")

    async def retrieve_tags(self, track_id: str, emotion: str) -> str | None:
        """
        Retrieves tags associated with a track from the database.

        Parameters
        ----------
        track_id : str
            The unique identifier for the track.
        emotion : str
            The emotion to retrieve tags for.

        Returns
        -------
        str or None
            The emotional tags for the track if found, otherwise None.

            The emotional tags are original lyrics of the track with certain phrases wrapped in <span> tags, where the
            class names correspond to the detected emotion.

        Raises
        ------
        StorageServiceException
            If a database error occurs.
        """

        select_query = f"""
            SELECT * FROM Tags 
            WHERE track_id = ?
            AND emotion = ?;
        """

        try:
            cursor = await self.db.execute(select_query, (track_id, emotion))
            row = await cursor.fetchone()
            tags = row[1] if row else None

            return tags
        except aiosqlite.OperationalError as e:
            raise StorageServiceException(f"Database operation failed - {e}")
        except aiosqlite.DatabaseError as e:
            raise StorageServiceException(f"Unexpected database error - {e}")
