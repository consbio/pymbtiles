import hashlib
import logging
import os
import sys
import sqlite3
from collections import namedtuple

logger = logging.getLogger("pymbtiles")

IS_PY2 = sys.version_info[0] == 2


Tile = namedtuple("Tile", ["z", "x", "y", "data"])
TileCoordinate = namedtuple("TileCoordinate", ["z", "x", "y"])


class MBtiles(object):
    """
    Interface for reading and writing mbtiles files.

    meta attribute maps to the metadata table in the mbtiles file.
    """

    class Metadata(dict):
        def __init__(self, db, cursor, autoload=True):
            self._db = db
            self._cursor = cursor
            if autoload:
                self._cursor.execute("SELECT name, value from metadata")
                dict.update(self, {row[0]: row[1] for row in self._cursor.fetchall()})

        def __setitem__(self, k, v):
            dict.__setitem__(self, k, v)
            print("setting", k, v)
            self._cursor.execute(
                "INSERT OR REPLACE INTO metadata (name, value) values (?, ?)", (k, v)
            )
            self._db.commit()

        def update(self, *args, **kwargs):
            dict.update(self, *args, **kwargs)
            self._cursor.executemany(
                "INSERT OR REPLACE INTO metadata (name, value) values (?, ?)",
                self.items(),
            )
            self._db.commit()

    def __init__(self, filename, mode="r"):
        """
        Creates an open mbtiles file.  Must be closed after all data are added.

        Parameters
        ----------
        filename: string
            name of output mbtiles file
        mode: string, one of ('r', 'w', 'r+')
            if 'w', existing mbtiles file will be deleted first
        """

        self.mode = mode
        if mode not in ("r", "w", "r+"):
            raise ValueError("Mode must be r, w, or r+")

        if os.path.exists(filename):
            if mode == "w":
                os.remove(filename)
        elif "r" in mode:
            raise IOError("mbtiles not found: {0}".format(filename))

        if IS_PY2:  # pragma: no cover
            self._db = sqlite3.connect(filename, isolation_level=None)

        else:
            connect_mode = "ro" if mode == "r" else "rwc"
            self._db = sqlite3.connect(
                "file:{0}?mode={1}".format(filename, connect_mode),
                uri=True,
                isolation_level=None,
            )

        self._cursor = self._db.cursor()

        self._cursor.execute("PRAGMA synchronous=OFF")
        self._cursor.execute("PRAGMA journal_mode=OFF")  # TODO: DELETE or WAL?
        self._cursor.execute("PRAGMA locking_mode=EXCLUSIVE")

        # initialize tables if needed
        if mode != "r":
            schema = open(
                os.path.join(os.path.dirname(__file__), "mbtiles_tile_schema.sql")
            ).read()
            self._cursor.executescript(schema)
            self._db.commit()

        self._meta = self.Metadata(self._db, self._cursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def meta(self):
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = self.Metadata(self._db, self._cursor, autoload=False)
        self._meta.update(value)

    def has_tile(self, z, x, y):
        self._cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM tiles "
            "where zoom_level=? and tile_column=? and tile_row=? LIMIT 1)",
            (z, x, y),
        )

        row = self._cursor.fetchone()
        return row[0] == 1

    def list_tiles(self):
        """Read a list of TileCoordinate (z, x, y) tuples from the tileset.

        For large tilesets, use a list_tiles_batched to avoid reading all tiles into memory.
        
        Returns
        -------
        list of TileCoordinate objects
        """

        self._cursor.execute("select zoom_level, tile_column, tile_row from tiles")
        return [TileCoordinate(*tile) for tile in self._cursor.fetchall()]

    def zoom_range(self):
        """Return the minimum and maximum zoom ranges available in the tileset.
        """

        return tuple(
            self._cursor.execute(
                "select min(zoom_level), max(zoom_level) from tiles"
            ).fetchone()
        )

    def row_range(self, z=0):
        """Return the minimum and maximum row available for a given zoom level.
        
        NOTE: this will return (None, None) for a zoom level not present in the tileset.
        
        Parameters
        ----------
        z : int, optional (default: 0)
            zoom level to query for available rows
        """

        return tuple(
            self._cursor.execute(
                "select min(tile_row), max(tile_row) from tiles where zoom_level = {}".format(
                    z
                )
            ).fetchone()
        )

    def col_range(self, z=0):
        """Return the minimum and maximum column available for a given zoom level.

        NOTE: this will return (None, None) for a zoom level not present in the tileset.
        
        Parameters
        ----------
        z : int, optional (default: 0)
            zoom level to query for available columns
        """

        return tuple(
            self._cursor.execute(
                "select min(tile_column), max(tile_column) from tiles where zoom_level = {}".format(
                    z
                )
            ).fetchone()
        )

    def list_tiles_batched(self, batch_size=1000):
        """Read a list of TileCoordinate (z, x, y) tuples from the tileset, in batches.

        Use this for larger tilesets to avoid reading all tiles into memory.
        
        Parameters
        ----------
        batch_size : int, optional (default: None)
            If present, tiles are read in batches using a generator.
            Otherwise, tiles are returned as a generator.
        
        Returns
        -------
        generator over each batch, each batch is a list of TileCoordinate objects
        """

        offset = 0
        while True:
            self._cursor.execute(
                "select zoom_level, tile_column, tile_row from tiles limit {limit} offset {offset}".format(
                    offset=offset, limit=batch_size
                )
            )
            offset += batch_size
            tiles = [TileCoordinate(z, x, y) for z, x, y in self._cursor.fetchall()]
            if len(tiles):
                yield tiles
            else:
                return

    def read_tile(self, z, x, y):
        """
        Get a tile for z, x, y values

        Parameters
        ----------
        z: int
            zoom level
        x: int
            tile column
        y: int
            tile row

        Returns
        -------
        tile data in bytes.  None if no tile exists.
        """

        self._cursor.execute(
            "SELECT tile_data FROM tiles "
            "where zoom_level=? and tile_column=? and tile_row=? LIMIT 1",
            (z, x, y),
        )

        row = self._cursor.fetchone()
        if row is None:
            return None

        if IS_PY2:  # pragma: no cover
            return str(row[0])

        return row[0]

    def write_tile(self, z, x, y, data):
        """
        Add a tile to the mbtiles file.  Note: this is not as performant as
        add_tiles function for inserting several tiles at once.

        Parameters
        ----------
        z: int
            zoom level
        x: int
            tile column
        y: int
            tile row
        data: bytes
            tile data bytes
        """

        id = hashlib.sha1(data).hexdigest()

        self._cursor.execute(
            "INSERT OR REPLACE INTO images (tile_id, tile_data) values (?, ?)",
            (id, sqlite3.Binary(data)),  # is this necessary
        )

        self._cursor.execute(
            "INSERT OR REPLACE INTO map "
            "(zoom_level, tile_column, tile_row, tile_id) "
            "values(?, ?, ?, ?)",
            (z, x, y, id),
        )

        self._db.commit()

    def write_tiles(self, tiles):
        """
        Add several tiles to mbtiles file, using a single transaction.
        Parameters
        ----------
        tiles: iterable of Tile(z, x, y, data) tuples
        """

        self._cursor.execute("BEGIN")

        try:
            for tile in tiles:
                id = hashlib.sha1(tile.data).hexdigest()
                self._cursor.execute(
                    "INSERT OR REPLACE INTO images (tile_id, tile_data) values (?, ?)",
                    (id, sqlite3.Binary(tile.data)),
                )

                self._cursor.execute(
                    "INSERT OR REPLACE INTO map "
                    "(zoom_level, tile_column, tile_row, tile_id) "
                    "values(?, ?, ?, ?)",
                    (tile.z, tile.x, tile.y, id),
                )

            self._cursor.execute("COMMIT")

        except self._db.Error:  # pragma: no cover
            logger.exception("Error inserting tiles, rolling back database")
            self._cursor.execute("ROLLBACK")
            raise

    def close(self):
        """
        Close the mbtiles file.
        """

        self._cursor.close()
        self._db.close()
