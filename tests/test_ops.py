import sqlite3
import os
import sys
import pytest

from pymbtiles import MBtiles, Tile, TileCoordinate
from pymbtiles.ops import extend, union, difference

IS_PY2 = sys.version_info[0] == 2


def test_extend(tmpdir):
    source = str(tmpdir.join("source.mbtiles"))
    target = str(tmpdir.join("target.mbtiles"))
    with MBtiles(source, mode="w") as out:
        out.write_tiles([Tile(0, 0, 0, b""), Tile(1, 0, 0, b"")])

    with MBtiles(target, mode="w") as out:
        out.write_tiles([Tile(0, 0, 0, b"123"), Tile(2, 0, 0, b"")])

    extend(source, target)

    with MBtiles(target) as src:
        tiles = set(src.list_tiles())
        assert tiles == {(0, 0, 0), (1, 0, 0), (2, 0, 0)}

        # Make sure we didn't overwrite a tile
        assert src.read_tile(0, 0, 0) == b"123"


def test_union(tmpdir):
    left = str(tmpdir.join("left.mbtiles"))
    right = str(tmpdir.join("right.mbtiles"))
    outfilename = str(tmpdir.join("out.mbtiles"))

    with MBtiles(left, mode="w") as out:
        out.write_tiles([Tile(0, 0, 0, b""), Tile(1, 0, 0, b"")])

    with MBtiles(right, mode="w") as out:
        out.write_tiles([Tile(0, 0, 0, b"123"), Tile(2, 0, 0, b"")])

    union(left, right, outfilename)

    with MBtiles(outfilename) as src:
        tiles = set(src.list_tiles())
        assert tiles == {(0, 0, 0), (1, 0, 0), (2, 0, 0)}

        # Make sure we didn't overwrite a tile
        assert src.read_tile(0, 0, 0) == b""


def test_difference(tmpdir):
    left = str(tmpdir.join("left.mbtiles"))
    right = str(tmpdir.join("right.mbtiles"))
    outfilename = str(tmpdir.join("out.mbtiles"))

    with MBtiles(left, mode="w") as out:
        out.write_tiles([Tile(0, 0, 0, b""), Tile(1, 0, 0, b"")])

    with MBtiles(right, mode="w") as out:
        out.write_tiles([Tile(0, 0, 0, b""), Tile(2, 0, 0, b"")])

    difference(left, right, outfilename)

    with MBtiles(outfilename) as src:
        tiles = set(src.list_tiles())
        assert tiles == {(1, 0, 0)}

