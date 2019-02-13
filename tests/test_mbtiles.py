import sqlite3
import os
import sys
import pytest

from pymbtiles import MBtiles, Tile

IS_PY2 = sys.version_info[0] == 2


def test_read_missing_file(tmpdir):
    mbtiles_filename = str(tmpdir.join("test.pymbtiles"))
    with pytest.raises(IOError):
        MBtiles(mbtiles_filename)


def test_invalid_mode(tmpdir):
    mbtiles_filename = str(tmpdir.join("test.pymbtiles"))

    with pytest.raises(ValueError):
        MBtiles(mbtiles_filename, mode="r+w")


def test_existing_file(tmpdir, blank_png_tile):
    filename = str(tmpdir.join("test.pymbtiles"))

    # create a file first
    with MBtiles(filename, mode="w") as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    assert os.path.exists(filename)

    # this should overwrite the previous
    with MBtiles(filename, mode="w") as out:
        out.write_tile(1, 0, 0, blank_png_tile)

    with MBtiles(filename, mode="r") as src:
        assert src.read_tile(0, 0, 0) is None
        assert src.read_tile(1, 0, 0) == blank_png_tile


def test_write_tile(tmpdir, blank_png_tile):
    filename = str(tmpdir.join("test.pymbtiles"))
    with MBtiles(filename, mode="w") as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    with sqlite3.connect(filename) as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT tile_data FROM tiles "
            "where zoom_level=0 and tile_column=0 and tile_row=0 LIMIT 1"
        )
        row = cursor.fetchone()
        assert row is not None
        assert blank_png_tile == str(row[0]) if IS_PY2 else row[0]


def test_write_tiles(tmpdir, blank_png_tile):
    filename = str(tmpdir.join("test.pymbtiles"))
    tiles = (Tile(1, 0, 0, blank_png_tile), Tile(1, 0, 1, blank_png_tile))

    with MBtiles(filename, mode="w") as out:
        out.write_tiles(tiles)

    with sqlite3.connect(filename) as db:
        cursor = db.cursor()
        cursor.execute("SELECT tile_data FROM tiles")
        rows = cursor.fetchall()
        assert len(rows) == 2
        for i, row in enumerate(rows):
            assert tiles[i].data == str(row[0]) if IS_PY2 else row[0]


def test_overwrite_tile(tmpdir, blank_png_tile):
    # Should not fail if we send in a duplicate tile
    filename = str(tmpdir.join("test.pymbtiles"))
    with MBtiles(filename, mode="w") as out:
        out.write_tile(0, 0, 0, blank_png_tile)

        # overwrite tile previously written
        out.write_tile(0, 0, 0, b"123")

    with MBtiles(filename, mode="r") as src:
        assert src.read_tile(0, 0, 0) == b"123"


def test_has_tile(tmpdir, blank_png_tile):
    filename = str(tmpdir.join("test.pymbtiles"))

    # Create mbtiles file with a tile to read
    with MBtiles(filename, mode="w") as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    with MBtiles(filename, mode="r") as src:
        assert src.has_tile(0, 0, 0) == True
        assert src.has_tile(10, 10, 10) == False


def test_read_tile(tmpdir, blank_png_tile):
    filename = str(tmpdir.join("test.pymbtiles"))

    # Create mbtiles file with a tile to read
    with MBtiles(filename, mode="w") as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    with MBtiles(filename, mode="r") as src:
        assert src.read_tile(0, 0, 0) == blank_png_tile


def test_read_missing_tile(tmpdir, blank_png_tile):
    filename = str(tmpdir.join("test.pymbtiles"))

    # Create mbtiles file with a tile to read
    with MBtiles(filename, mode="w") as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    with MBtiles(filename, mode="r") as src:
        assert src.read_tile(1, 0, 0) is None


def test_write_metadata(tmpdir):
    filename = str(tmpdir.join("test.pymbtiles"))

    metadata = {"name": "test tiles", "version": "1.0.0"}

    with MBtiles(filename, mode="w") as out:
        out.meta = metadata

    with sqlite3.connect(filename) as db:
        cursor = db.cursor()
        cursor.execute("SELECT name, value from metadata")
        out = {row[0]: row[1] for row in cursor.fetchall()}
        assert out == metadata

    # add a new key, value
    with MBtiles(filename, mode="r+") as out:
        out.meta["foo"] = "bar"

    with sqlite3.connect(filename) as db:
        cursor = db.cursor()
        cursor.execute('SELECT value from metadata WHERE name="foo" LIMIT 1')
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "bar"


def test_read_metadata(tmpdir):
    filename = str(tmpdir.join("test.pymbtiles"))

    metadata = {"name": "test tiles", "version": "1.0.0"}

    with MBtiles(filename, mode="w") as out:
        out.meta = metadata

    with MBtiles(filename, mode="r") as src:
        src.meta == metadata
