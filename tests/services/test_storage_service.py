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
# 1. Test that initialise_db creates new tables with expected columns.
@pytest.mark.asyncio
async def test_initialise_db_creates_table():
    """Test that initialise_db creates new tables with expected columns."""

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
            and tags_column_names == {"track_id", "emotion", "tags"}
        )


# -------------------- STORE PROFILE -------------------- #
# 1. Test that store_profile raises StorageServiceException if track_id already exists.
# 2. Test that store_profile raises StorageServiceException if operational error occurs.
# 3. Test that store_profile raises StorageServiceException if database error occurs.
# 4. Test that store_profile stores profile in database.
@pytest.fixture
def mock_emotional_profile() -> dict[str, float]:
    return {
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


@pytest_asyncio.fixture
async def existing_profile(db, mock_emotional_profile) -> tuple[str, dict[str, float]]:
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

    track_id = "1"

    await db.execute(insert_statement, (track_id, *mock_emotional_profile.values()))
    await db.commit()

    return track_id, mock_emotional_profile


@pytest.mark.asyncio
async def test_store_profile_track_id_already_exists(storage_service, existing_profile, mock_emotional_profile):
    """Ensure StorageServiceException is raised on duplicate track ID."""

    existing_track_id, existing_profile = existing_profile

    # insert should fail due to primary key violation
    with pytest.raises(StorageServiceException, match="Track ID '1' already exists."):
        await storage_service.store_profile(track_id=existing_track_id, profile=mock_emotional_profile)


@pytest.mark.asyncio
async def test_store_profile_operational_error(storage_service, db, mock_emotional_profile):
    """Test retrieving profile when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.OperationalError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Database operation failed"):
        await storage_service.store_profile(track_id="1", profile=mock_emotional_profile)


@pytest.mark.asyncio
async def test_store_profile_database_error(storage_service, db, mock_emotional_profile):
    """Test retrieving profile when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.DatabaseError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Unexpected database error"):
        await storage_service.store_profile(track_id="1", profile=mock_emotional_profile)


@pytest.mark.asyncio
async def test_store_profile_adds_profile_to_db(storage_service, db, mock_emotional_profile):
    """Test that store profile adds profile to db"""

    track_id = "1"

    await storage_service.store_profile(track_id=track_id, profile=mock_emotional_profile)

    cursor = await db.execute(f"SELECT * FROM profile WHERE track_id = {track_id}")
    row = await cursor.fetchone()
    assert row == (track_id, *mock_emotional_profile.values())


# -------------------- RETRIEVE PROFILE -------------------- #
# 1. Test that retrieve_profile raises StorageServiceException if operational error occurs.
# 2. Test that retrieve_profile raises StorageServiceException if database error occurs.
# 3. Test that retrieve_profile returns None if track_id not found.
# 4. Test that retrieve_profile returns expected profile.
@pytest.mark.asyncio
async def test_retrieve_profile_operational_error(storage_service, db):
    """Test retrieving profile when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.OperationalError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Database operation failed"):
        await storage_service.retrieve_profile(track_id="1")


@pytest.mark.asyncio
async def test_retrieve_profile_database_error(storage_service, db):
    """Test retrieving profile when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.DatabaseError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Unexpected database error"):
        await storage_service.retrieve_profile(track_id="1")


@pytest.mark.asyncio
async def test_retrieve_profile_does_not_exist(storage_service):
    """Test retrieving profile for a track that doesn't exist."""

    retrieved_profile = await storage_service.retrieve_profile("does_not_exist")

    assert retrieved_profile is None, "Should return None for non-existent track"


@pytest.mark.asyncio
async def test_retrieve_profile_does_exist(storage_service, existing_profile):
    """Test retrieving profile for a track that does exist."""

    existing_track_id, existing_profile = existing_profile

    retrieved_profile = await storage_service.retrieve_profile(existing_track_id)

    assert retrieved_profile == existing_profile, "Should return stored profile for stored track"
    

# -------------------- STORE TAGS -------------------- #
# 1. Test that store_tags raises StorageServiceException if track_id already exists.
# 2. Test that store_tags raises StorageServiceException if operational error occurs.
# 3. Test that store_tags raises StorageServiceException if database error occurs.
# 4. Test that store_tags stores tags in database.
@pytest_asyncio.fixture
async def existing_tags(db) -> tuple[str, str, str]:
    track_id = "1"
    emotion = "anger"
    tags = """<span class="anger">I’ll hurt you</span>"""

    insert_statement = f"""
        INSERT INTO Tags (track_id, emotion, tags)
        VALUES (?, ?, ?);
    """

    await db.execute(insert_statement, (track_id, emotion, tags))
    await db.commit()

    return track_id, emotion, tags


@pytest.mark.asyncio
async def test_store_tags_track_id_and_emotion_already_exist(storage_service, existing_tags):
    """Ensure StorageServiceException is raised on duplicate track ID."""

    existing_track_id, existing_emotion, _ = existing_tags

    # insert should fail due to primary key violation
    with pytest.raises(
            StorageServiceException,
            match=f"Entry already exists with track ID '{existing_track_id}' and emotion '{existing_emotion}'."
    ):
        await storage_service.store_tags(track_id=existing_track_id, emotion=existing_emotion, tags="Random tags")


@pytest.mark.asyncio
async def test_store_tags_operational_error(storage_service, db):
    """Test retrieving tags when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.OperationalError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Database operation failed"):
        await storage_service.store_tags(
            track_id="1",
            emotion="joy",
            tags="""<span class="anger">I’ll hurt you</span>"""
        )


@pytest.mark.asyncio
async def test_store_tags_database_error(storage_service, db):
    """Test retrieving tags when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.DatabaseError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Unexpected database error"):
        await storage_service.store_tags(track_id="1", emotion="joy", tags="Random tags")


@pytest.mark.asyncio
async def test_store_tags_adds_tags_to_db(storage_service, db):
    """Test that store tags adds tags to db"""

    track_id = "1"
    emotion = "anger"
    tags = """<span class="anger">I’ll hurt you</span>"""

    await storage_service.store_tags(track_id=track_id, emotion=emotion, tags=tags)

    cursor = await db.execute(f"SELECT * FROM Tags WHERE track_id = {track_id};")
    row = await cursor.fetchone()
    assert row == (track_id, emotion, tags)


# -------------------- RETRIEVE TAGS -------------------- #
# 1. Test that retrieve_tags raises StorageServiceException if operational error occurs.
# 2. Test that retrieve_tags raises StorageServiceException if database error occurs.
# 3. Test that retrieve_tags returns None if track_id not found.
# 4. Test that retrieve_tags returns expected tags.
@pytest.mark.asyncio
async def test_retrieve_tags_operational_error(storage_service, db):
    """Test retrieving tags when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.OperationalError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Database operation failed"):
        await storage_service.retrieve_tags(track_id="1", emotion="joy")


@pytest.mark.asyncio
async def test_retrieve_tags_database_error(storage_service, db):
    """Test retrieving tags when a DB operational error occurs."""

    mock_execute = AsyncMock()
    mock_execute.side_effect = aiosqlite.DatabaseError
    db.execute = mock_execute

    with pytest.raises(StorageServiceException, match="Unexpected database error"):
        await storage_service.retrieve_tags(track_id="1", emotion="joy")


@pytest.mark.asyncio
async def test_retrieve_tags_does_not_exist(storage_service):
    """Test retrieving tags for a track that doesn't exist."""

    retrieved_tags = await storage_service.retrieve_tags(track_id="does_not_exist", emotion="joy")

    assert retrieved_tags is None, "Should return None for non-existent track"


@pytest.mark.asyncio
async def test_retrieve_tags_does_exist(storage_service, existing_tags):
    """Test retrieving tags for a track that does exist."""

    existing_track_id, existing_emotion, tags = existing_tags

    retrieved_tags = await storage_service.retrieve_tags(track_id=existing_track_id, emotion=existing_emotion)

    assert retrieved_tags == tags, "Should return stored tags for stored track"
