# Mapbox MBtiles Utilities

A Python 2.7 and 3 library for working with [Mabox mbtiles v1.1](https://github.com/mapbox/mbtiles-spec/blob/master/1.1/spec.md)

[![Build Status](https://travis-ci.org/consbio/pymbtiles.svg?branch=master)](https://travis-ci.org/consbio/pymbtiles) [![Coverage Status](https://coveralls.io/repos/github/consbio/pymbtiles/badge.svg?branch=master)](https://coveralls.io/github/consbio/pymbtiles?branch=master)

## Features

Provides a lighweight Python API for reading and writing mbtiles files.

[Mabox mbtiles v1.1](https://github.com/mapbox/mbtiles-spec/blob/master/1.1/spec.md) allow you to store geographic data as rendered image tiles or as vector tiles, along with associated metadata.

## Installation

```
pip install pymbtiles
```

To install from master branch on GitHub using pip:

```
pip install git+https://github.com/consbio/pymbtiles.git#egg=pymbtiles --upgrade
```

## Usage

### Python API

open for reading and read a tile:

```
from pymbtiles import MBTiles
with MBtiles('my.mbtiles') as src:
    tile_data = src.read_tile(z=0, x=0, y=0)
```

returns tile data in bytes.

open for writing (existing file will be overwritten):

```
with MBtiles('my.mbtiles', mode='w') as out:
    out.write_tile(z=0, x=0, y=0, tile_data)
```

or write a bunch of tiles at once:

```
from pymbtiles import MBTiles, Tile

tiles = (
    Tile(z=1, x=0, y=0, tile_data=first_tile),
    ...
)

with MBtiles('my.mbtiles', mode='w') as out:
    out.write_tiles(tiles)
```

Use `r+` mode to read and write.

Metadata is stored in the `meta` attribute of the mbtiles instance:

```
with MBtiles('my.mbtiles') as src:
    metadata = src.meta
```

This metadata is stored in the `metadata` table in the mbtiles file, and contains
a number of records required or optional under the
[mbtiles specification](https://github.com/mapbox/mbtiles-spec/blob/master/1.1/spec.md) .

To update metadata:

```
with MBtiles('my.mbtiles', 'r+') as out:
    out.meta['some_key'] = 'some_value'
```

You can set several values at once by passing in a new `dict` object:

```
with MBtiles('my.mbtiles', 'w') as out:
    out.meta = my_metadata_dict
```

## Listing available tiles

To list available tiles in the tileset:

```
with MBtiles('my.mbtiles') as src:
    for tile_coords in src.list_tiles():  # [TileCoordinate(z, x, y)...]
        ...
```

_WARNING:_ for large tilesets, this can exceed available memory.

To list available tilesets for large tilesets, use:

```
with MBtiles('my.mbtiles') as src:
    for batch in src.list_tiles_batched():
        for tile_coords in batch: # [TileCoordinate(z, x, y)...]
            ...
```

## Set operations

The `ops` module provides `extend`, `union`, and `difference` functions to perform set operations on tilesets.

Extend a tileset with new tiles from a second:

```
extend(source_filename, target_filename)
```

Create a new tileset with unique tiles combined from both left and right tilesets:

```
union(left_filename, right_filename, out_filename)
```

Create a new tileset from the tileset in the left tileset not present in the right tileset:

```
difference(left_filename, right_filename, out_filename)
```

## Tile Scheme

Tiles are output to mbtiles format in xyz tile scheme.

## Possibly useful:

-   [`mbtileserver`](https://github.com/consbio/mbtileserver): a lightweight Go tile server
-   [`tpkutils`](https://github.com/consbio/tpkutils): a library for converting ArcGIS tile cache to mbtiles

## Changes :

### 0.5.0

-   added `zoom_range`, `row_range`, `col_range` to provide basic information about tiles available in the tileset

### 0.4.0

-   added `list_tiles` to list tiles and `list_tiles_batch` to list tiles in batches
-   added `ops` module with `extend`, `union`, `difference` functions

### 0.3.0

-   all write-like operations for metadata and tiles are now overwrite by default

## Credits:

Inspired by:

-   [mbutil](https://github.com/mapbox/mbutil)
-   [node-mbtiles](https://github.com/mapbox/node-mbtiles)

SQL for creating mbtiles database derived from
[node-mbtiles](https://github.com/mapbox/node-mbtiles)

## License:

See LICENSE.md
