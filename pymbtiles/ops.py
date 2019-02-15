import os
import shutil

from pymbtiles import MBtiles, TileCoordinate, Tile


def extend(source_filename, target_filename, batch_size=1000):
    """
    Add tiles from source_filename to target_tileset that are not already in target.

    Equivalent to the union of tiles from source and target, but
    written to the target to cut down on additional IO of copying
    both to a new file.

    Note: caller is responsible for updating metadata as needed.

    Parameters
    ----------
    source_filename : str
        name of source tiles mbtiles file for additional tiles
    target_tileset : str
        name of target tiles mbtiles file for adding tiles to
    batch_size : int, optional (default: 1000)
        size of each batch to read from the source and write to the target
    """

    with MBtiles(target_filename, "r+") as target, MBtiles(source_filename) as source:
        for batch in source.list_tiles_batched(batch_size):
            tiles_to_copy = [tile for tile in batch if not target.has_tile(*tile)]

            if tiles_to_copy:
                target.write_tiles(
                    Tile(*tile, data=source.read_tile(*tile)) for tile in tiles_to_copy
                )


def union(leftfilename, rightfilename, outfilename, batch_size=1000):
    """Combine unique tiles from left and right, where tiles are added from right that are not already in left.

    Note: caller is responsible for updating metadata as needed.  Metadata is copied from left.

    Parameters
    ----------
    leftfilename : str
        first tileset filename
    rightfilename : str
        second tileset filename
    outfilename : str
        output tileset filename
    batch_size : int, optional (default: 1000)
        size of each batch to read from the source and write to the target
    """

    # Copy the largest file to the target to avoid unnecessary tile I/O
    # of individual tiles
    if os.stat(leftfilename).st_size >= os.stat(rightfilename).st_size:
        targetfilename = leftfilename
        sourcefilename = rightfilename
    else:  # pragma: no cover
        targetfilename = rightfilename
        sourcefilename = leftfilename

    print("copying tiles from {0} to {1}".format(targetfilename, outfilename))
    shutil.copy(targetfilename, outfilename)

    print("merging tiles from {0} to {1}".format(sourcefilename, outfilename))
    extend(sourcefilename, outfilename, batch_size=batch_size)


def difference(leftfilename, rightfilename, outfilename, batch_size=1000):
    """Create new tileset from tiles in left that are not in right.
    
    Note: caller is responsible for updating metadata as needed.  Metadata is copied from target.

    Parameters
    ----------
    leftfilename : str
        first tileset filename
    rightfilename : str
        second tileset filename
    outfilename : str
        output tileset filename
    batch_size : int, optional (default: BATCH_SIZE)
        size of each batch to read from the source and write to the target
    """

    with MBtiles(leftfilename) as left, MBtiles(rightfilename) as right, MBtiles(
        outfilename, "w"
    ) as out:
        out.meta = left.meta

        for batch in left.list_tiles_batched(batch_size):
            tiles_to_copy = [tile for tile in batch if not right.has_tile(*tile)]

            if tiles_to_copy:
                out.write_tiles(
                    Tile(*tile, data=left.read_tile(*tile)) for tile in tiles_to_copy
                )
