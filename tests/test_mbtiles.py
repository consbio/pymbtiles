import sqlite3
import pytest

from pymbtiles import MBtiles, Tile


def test_read_missing_file(tmpdir):
    mbtiles_filename = str(tmpdir.join('test.pymbtiles'))
    with pytest.raises(IOError):
        MBtiles(mbtiles_filename)


def test_invalid_mode(tmpdir):
    mbtiles_filename = str(tmpdir.join('test.pymbtiles'))

    with pytest.raises(ValueError):
        MBtiles(mbtiles_filename, mode='r+w')


def test_write_tile(tmpdir, blank_png_tile):
    filename = str(tmpdir.join('test.pymbtiles'))
    with MBtiles(filename, mode='w') as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    with sqlite3.connect(filename) as db:
        cursor = db.cursor()
        cursor.execute(
            'SELECT tile_data FROM tiles '
            'where zoom_level=0 and tile_column=0 and tile_row=0 LIMIT 1'
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == blank_png_tile


def test_write_tiles(tmpdir, blank_png_tile):
    filename = str(tmpdir.join('test.pymbtiles'))
    tiles = (
        Tile(1, 0, 0, blank_png_tile),
        Tile(1, 0, 1, blank_png_tile)
    )

    with MBtiles(filename, mode='w') as out:
        out.write_tiles(tiles)

    with sqlite3.connect(filename) as db:
        cursor = db.cursor()
        cursor.execute('SELECT tile_data FROM tiles')
        rows = cursor.fetchall()
        assert len(rows) == 2
        assert rows[0][0] == tiles[0].data
        assert rows[1][0] == tiles[1].data


def test_read_tile(tmpdir, blank_png_tile):
    filename = str(tmpdir.join('test.pymbtiles'))

    # Create mbtiles file with a tile to read
    with MBtiles(filename, mode='w') as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    with MBtiles(filename, mode='r') as src:
        assert src.read_tile(0, 0 , 0) == blank_png_tile


def test_read_missing_tile(tmpdir, blank_png_tile):
    filename = str(tmpdir.join('test.pymbtiles'))

    # Create mbtiles file with a tile to read
    with MBtiles(filename, mode='w') as out:
        out.write_tile(0, 0, 0, blank_png_tile)

    with MBtiles(filename, mode='r') as src:
        assert src.read_tile(1, 0, 0) is None