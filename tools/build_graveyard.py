#!/usr/bin/env python3
"""Build the graveyard .mcstructure (17x12x17) with the structure toolkit."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "structure_tools"))

import build_lib as L
from build_lib import Canvas, B, slab

OUT = os.path.join(HERE, "graveyard_assets", "BP", "structures", "graveyard.mcstructure")


def ruined(x, z):
    return (x * 7 + z * 11) % 5 != 0


def headstone(c, x, z, mossy=False):
    c.set(x, 1, z, B("minecraft:cobblestone"))
    body = B("minecraft:mossy_stone_bricks") if mossy else B("minecraft:chiseled_stone_bricks")
    c.set(x, 2, z, body)
    c.set(x, 3, z, slab("minecraft:stone_brick_slab"))


def build():
    c = Canvas(17, 12, 17, ymin=-3)
    soil = B("minecraft:soul_soil")
    c.ground_pad(soil, 0, 0, 16, 16, y=0, depth=3, skirt=B("minecraft:stone"))

    # paths
    for i in range(17):
        c.set(8, 0, i, B("minecraft:gravel"))
        c.set(i, 0, 8, B("minecraft:gravel"))

    # soul-sand accents
    for (x, z) in ((2, 2), (14, 2), (2, 14), (14, 14)):
        c.set(x, 0, z, B("minecraft:soul_sand"))

    # ruined perimeter wall + iron bars
    for i in range(17):
        for (x, z) in ((i, 0), (i, 16), (0, i), (16, i)):
            gate = (x in (7, 8, 9) and z in (0, 16)) or (z in (7, 8, 9) and x in (0, 16))
            if gate:
                continue
            wall = B("minecraft:mossy_cobblestone") if (x + z) % 3 == 0 else B("minecraft:cobblestone")
            c.set(x, 1, z, wall)
            if ruined(x, z) and not ((x in (0, 16)) and (z in (0, 16))):
                c.set(x, 2, z, B("minecraft:iron_bars"))

    # gate posts with soul lanterns
    for (x, z) in ((7, 0), (9, 0), (7, 16), (9, 16), (0, 7), (0, 9), (16, 7), (16, 9)):
        c.set(x, 1, z, B("minecraft:cobblestone"))
        c.set(x, 2, z, B("minecraft:cobblestone"))
        c.set(x, 3, z, B("minecraft:soul_lantern"))
    for (x, z) in ((0, 0), (16, 0), (0, 16), (16, 16)):
        c.set(x, 1, z, B("minecraft:mossy_cobblestone"))
        c.set(x, 2, z, B("minecraft:cobblestone"))
        c.set(x, 3, z, B("minecraft:soul_lantern"))

    # graves
    graves = [(3, 3), (5, 3), (11, 3), (13, 3), (3, 5), (5, 5), (11, 5), (13, 5), (3, 12), (13, 12)]
    for i, (x, z) in enumerate(graves):
        headstone(c, x, z, mossy=(i % 3 == 0))

    # mausoleum (x 5..11, z 11..15), open archway facing the path
    dbrick = B("minecraft:deepslate_bricks")
    dtile = B("minecraft:deepslate_tiles")
    dchis = B("minecraft:chiseled_deepslate")
    c.fill(5, 0, 11, 11, 0, 15, dtile)
    for y in (1, 2, 3):
        for x in range(5, 12):
            c.set(x, y, 11, dbrick)
            c.set(x, y, 15, dbrick)
        for z in range(11, 16):
            c.set(5, y, z, dbrick)
            c.set(11, y, z, dbrick)
    for (x, z) in ((5, 11), (11, 11), (5, 15), (11, 15)):
        for y in (1, 2, 3):
            c.set(x, y, z, dchis)
    c.set(7, 2, 11, dchis)
    c.set(9, 2, 11, dchis)
    c.set(8, 1, 11, None)
    c.set(8, 2, 11, None)
    # roof with overhang
    c.fill(4, 4, 10, 12, 4, 16, dtile)
    for x in range(4, 13):
        c.set(x, 5, 10, dchis)
        c.set(x, 5, 16, dchis)
    c.fill(6, 5, 12, 10, 5, 14, dtile)

    # interior: chest + soul lantern pedestals
    c.chest(8, 1, 14, "loot_tables/chests/graveyard.json", facing="south", name="Forgotten Chest")
    for (x, z) in ((6, 14), (10, 14)):
        c.set(x, 1, z, dtile)
        c.set(x, 2, z, B("minecraft:soul_lantern"))

    # bare dead tree
    for y in range(1, 5):
        c.set(3, y, 13, B("minecraft:oak_log", pillar_axis="y"))
    c.set(2, 3, 13, B("minecraft:oak_log", pillar_axis="x"))
    c.set(4, 3, 13, B("minecraft:oak_log", pillar_axis="x"))
    c.set(3, 4, 12, B("minecraft:oak_log", pillar_axis="z"))

    return c


def main():
    c = build()
    data = c.to_bytes()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(data)
    print(OUT, len(data), "bytes")


if __name__ == "__main__":
    main()
