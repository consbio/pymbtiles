
# Mapbox MBtiles Utilities

A Python 2.7 and 3 library for working with [Mabox mbtiles v1.1](https://github.com/mapbox/mbtiles-spec/blob/master/1.1/spec.md)

[![Build Status](https://travis-ci.org/consbio/pymbtiles.svg?branch=master)](https://travis-ci.org/consbio/pymbtiles) [![Coverage Status](https://coveralls.io/repos/github/consbio/pymbtiles/badge.svg?branch=master)](https://coveralls.io/github/consbio/pymbtiles?branch=master)


## Goals
* Provide a very lightweight API for reading / writing mbtiles files



## Installation
For now, while this is under active development, install from master
branch on GitHub using pip:
```
pip install git+https://github.com/consbio/pymbtiles.git --upgrade
```

Once functionality stabilizes, it will be added to
[PyPi](https://pypi.python.org/pypi)


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




*Note:*
* tiles are output to mbtiles format in xyz tile scheme.



## Credits:

Inspired by:
* [mbutil](https://github.com/mapbox/mbutil)
* [node-mbtiles](https://github.com/mapbox/node-mbtiles)

SQL for creating mbtiles database derived from
[node-mbtiles](https://github.com/mapbox/node-mbtiles)


## License:
See LICENSE.md
