import pytest
from sqlalchemy import text

from agents.utils import (
    get_db_table_names,
    get_detailed_table_info,
    get_engine_for_chinook_db,
    get_schema_overview,
)


@pytest.mark.utils
def test_get_engine_for_chinook_db():
    engine = get_engine_for_chinook_db()
    assert engine is not None
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
    assert "Album" in tables
    assert "Artist" in tables


@pytest.mark.utils
def test_get_db_table_names():
    table_names = get_db_table_names()
    assert isinstance(table_names, list)
    assert "Album" in table_names
    assert "Track" in table_names


@pytest.mark.utils
def test_get_detailed_table_info():
    detailed_info = get_detailed_table_info()
    assert isinstance(detailed_info, dict)
    assert "Album" in detailed_info

    album_info = detailed_info["Album"]
    assert "columns" in album_info
    assert isinstance(album_info["columns"], list)
    assert any(col["name"] == "Title" for col in album_info["columns"])
    assert "sample_data" in album_info

    # Updated: sample_data is returned as a string
    sample_data = album_info["sample_data"]
    assert isinstance(sample_data, str)
    assert sample_data.startswith("[")  # basic sanity check
    assert "For Those About To Rock" in sample_data  # verify content presence


@pytest.mark.utils
def test_get_schema_overview():
    overview = get_schema_overview()
    assert isinstance(overview, dict)
    assert "Track" in overview
    track_schema = overview["Track"]
    assert isinstance(track_schema, list)
    assert any(col["name"] == "Name" for col in track_schema)
