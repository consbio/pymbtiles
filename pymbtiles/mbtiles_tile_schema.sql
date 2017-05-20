-- Derived from https://github.com/mapbox/node-mbtiles/blob/master/lib/schema.sql
--
-- Modifications copyright (c) 2016-2017, Conservation Biology Institute
-- Modifications:
-- * removed geocoder table and index statements
--
--
-- Copyright (c), Development Seed
-- All rights reserved.
--
-- Redistribution and use in source and binary forms, with or without modification,
-- are permitted provided that the following conditions are met:
--
-- - Redistributions of source code must retain the above copyright notice, this
--   list of conditions and the following disclaimer.
-- - Redistributions in binary form must reproduce the above copyright notice, this
--   list of conditions and the following disclaimer in the documentation and/or
--   other materials provided with the distribution.
-- - Neither the name "Development Seed" nor the names of its contributors may be
--   used to endorse or promote products derived from this software without
--   specific prior written permission.
--
-- THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
-- ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
-- WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
-- DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
-- ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
-- (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-- LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
-- ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
-- (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
-- SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

-- MBTiles schema for tiles

BEGIN;

CREATE TABLE IF NOT EXISTS map (
   zoom_level INTEGER,
   tile_column INTEGER,
   tile_row INTEGER,
   tile_id TEXT,
   grid_id TEXT
);

CREATE TABLE IF NOT EXISTS keymap (
    key_name TEXT,
    key_json TEXT
);

CREATE TABLE IF NOT EXISTS images (
    tile_data blob,
    tile_id text
);

CREATE TABLE IF NOT EXISTS metadata (
    name text,
    value text
);

CREATE UNIQUE INDEX IF NOT EXISTS map_index ON map (zoom_level, tile_column, tile_row);
CREATE UNIQUE INDEX IF NOT EXISTS keymap_lookup ON keymap (key_name);
CREATE UNIQUE INDEX IF NOT EXISTS images_id ON images (tile_id);
CREATE UNIQUE INDEX IF NOT EXISTS name ON metadata (name);

CREATE VIEW IF NOT EXISTS tiles AS
    SELECT
        map.zoom_level AS zoom_level,
        map.tile_column AS tile_column,
        map.tile_row AS tile_row,
        images.tile_data AS tile_data
    FROM map
    JOIN images ON images.tile_id = map.tile_id;

COMMIT;