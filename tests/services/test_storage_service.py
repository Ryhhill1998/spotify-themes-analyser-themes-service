from unittest.mock import AsyncMock, Mock

import aiosqlite
import pytest
import pytest_asyncio

from analysis_api.services.storage.storage_service import initialise_db, StorageService, StorageServiceException

DB_PATH = ":memory:"


@pytest_asyncio.fixture
async def db():
    """Creates an in-memory SQLite database for testing."""

    db = await aiosqlite.connect(DB_PATH)
    await initialise_db(db)

    yield db

    await db.close()


@pytest.fixture
def storage_service(db) -> StorageService:
    return StorageService(db)


# -------------------- INITIALISE DB -------------------- #
# 1. Test that initialise_db creates a new table with expected columns.
@pytest.mark.asyncio
async def test_initialise_db_creates_table():
    """Test that initialise_db creates a new table with expected columns."""

    async with (aiosqlite.connect(DB_PATH) as db):
        await initialise_db(db)

        # Query database metadata to check if 'Profile' table exists
        async with db.execute("PRAGMA table_info(Profile);") as cursor:
            profile_columns = await cursor.fetchall()

        profile_column_names = {col[1] for col in profile_columns}

        # Query database metadata to check if 'Tags' table exists
        async with db.execute("PRAGMA table_info(Tags);") as cursor:
            tags_columns = await cursor.fetchall()

        tags_column_names = {col[1] for col in tags_columns}

        assert (
            profile_column_names == {
                "track_id",
                "joy",
                "sadness",
                "anger",
                "fear",
                "love",
                "hope",
                "nostalgia",
                "loneliness",
                "confidence",
                "despair",
                "excitement",
                "mystery",
                "defiance",
                "gratitude",
                "spirituality"
            }
            and tags_column_names == {"track_id", "tags"}
        )


# -------------------- STORE PROFILE -------------------- #
@pytest_asyncio.fixture
async def existing_profile(db) -> tuple[str, dict[str, float]]:
    track_id = "1"
    emotional_profile = {
        "joy": 0.1,
        "sadness": 0.1,
        "anger": 0.2,
        "fear": 0.05,
        "love": 0.1,
        "hope": 0,
        "nostalgia": 0.03,
        "loneliness": 0.02,
        "confidence": 0.1,
        "despair": 0.05,
        "excitement": 0.1,
        "mystery": 0,
        "defiance": 0.05,
        "gratitude": 0.1,
        "spirituality": 0
    }

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
    await db.execute(insert_statement, (track_id, *emotional_profile.values()))
    await db.commit()

    return track_id, emotional_profile


# -------------------- RETRIEVE PROFILE -------------------- #


# -------------------- STORE TAGS -------------------- #
# 1. Test that store_tags raises StorageServiceException if track_id already exists.
# 2. Test that store_tags raises StorageServiceException if operational error occurs.
# 3. Test that store_tags raises StorageServiceException if database error occurs.
# 4. Test that store_tags stores tags in database.
@pytest_asyncio.fixture
async def existing_tags(db) -> tuple[str, str]:
    track_id = "1"
    tags = """<span class="anger">I’ll hurt you</span>"""

    insert_statement = f"""
        INSERT INTO Tags (track_id, tags)
        VALUES (?, ?);
    """

    await db.execute(insert_statement, (track_id, tags))
    await db.commit()

    return track_id, tags


@pytest.mark.asyncio
async def test_store_tags_track_id_already_exists(storage_service, existing_tags):
    """Ensure StorageServiceException is raised on duplicate track ID."""

    existing_track_id, existing_tags = existing_tags

    # insert should fail due to primary key violation
    with pytest.raises(StorageServiceException, match="Track ID '1' already exists."):
        await storage_service.store_tags(track_id=existing_track_id, tags="Random tags")


@pytest.mark.asyncio
async def test_store_tags_operational_error(storage_service, db):
    """Test retrieving tags when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.OperationalError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Database operation failed"):
        await storage_service.store_tags(track_id="1", tags="""<span class="anger">I’ll hurt you</span>""")


@pytest.mark.asyncio
async def test_store_tags_database_error(storage_service, db):
    """Test retrieving tags when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.DatabaseError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Unexpected database error"):
        await storage_service.store_tags(track_id="1", tags="Random tags")


@pytest.mark.asyncio
async def test_store_tags_adds_tags_to_db(storage_service, db):
    """Test that store tags adds tags to db"""

    track_id = "1"
    tags = """<span class="anger">I’ll hurt you</span>"""

    await storage_service.store_tags(track_id=track_id, tags=tags)

    cursor = await db.execute(f"SELECT * FROM Tags WHERE track_id = {track_id}")
    row = await cursor.fetchone()
    assert row == (track_id, tags)

# -------------------- RETRIEVE TAGS -------------------- #
# 1. Test that retrieve_tags raises StorageServiceException if operational error occurs.
# 2. Test that retrieve_tags raises StorageServiceException if database error occurs.
# 3. Test that retrieve_tags returns None if track_id not found.
# 4. Test that retrieve_tags returns expected tags.
# @pytest.mark.asyncio
# async def test_retrieve_tags_operational_error(storage_service, existing_track, db):
#     """Test retrieving tags when a DB operational error occurs."""
#
#     mock_execute = AsyncMock()
#     mock_execute.side_effect = aiosqlite.OperationalError
#     db.execute = mock_execute
#
#     with pytest.raises(StorageServiceException, match="Database operation failed"):
#         await storage_service.retrieve_tags(track_id="1")
#
#
# @pytest.mark.asyncio
# async def test_retrieve_tags_database_error(storage_service, existing_track, db):
#     """Test retrieving tags when a DB operational error occurs."""
#
#     mock_execute = AsyncMock()
#     mock_execute.side_effect = aiosqlite.DatabaseError
#     db.execute = mock_execute
#
#     with pytest.raises(StorageServiceException, match="Unexpected database error"):
#         await storage_service.retrieve_tags(track_id="1")
#
#
# @pytest.mark.asyncio
# async def test_retrieve_tags_does_not_exist(storage_service):
#     """Test retrieving tags for a track that doesn't exist."""
#
#     retrieved_tags = await storage_service.retrieve_tags("does_not_exist")
#
#     assert retrieved_tags is None, "Should return None for non-existent track"
#
#
# @pytest.mark.asyncio
# async def test_retrieve_tags_does_exist(storage_service, existing_track):
#     """Test retrieving tags for a track that does exist."""
#
#     existing_track_id, existing_tags = existing_track
#
#     retrieved_tags = await storage_service.retrieve_tags(existing_track_id)
#
#     assert retrieved_tags == existing_tags, "Should return stored tags for stored track"
