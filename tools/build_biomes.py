#!/usr/bin/env python3
"""Build Neo's More Biomes: 30 custom overworld biomes for Bedrock.

Biome placement follows the current 1.26 samples: `overworld_generation_rules`
with `generate_for_climates`, `surface_builder` materials and vanilla biome tags
so the base game's and the mob addon's tag-driven spawn/feature rules apply.
"""
import json
import os
import shutil
import uuid
import zipfile
from pathlib import Path

ROOT = Path("/workspace/Neo's more mobs")
OUT = ROOT / "NeosMoreBiomes"
BP = OUT / "NeosMoreBiomes_BP"
RP = OUT / "NeosMoreBiomes_RP"

# UUIDs of the unified mob addon this pack requires.
MOB_BP_UUID = "08ea1f24-e2b2-5799-b4ae-aea7a21d4456"
MOB_RP_UUID = "111d4c0b-65a9-5663-b0fd-6af67f38a8db"


def ns(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"neosmorebiomes:{name}"))


def overworld(top, mid="minecraft:dirt", foundation="minecraft:stone",
              sea_floor="minecraft:gravel", sea="minecraft:water", depth=7):
    return {
        "type": "minecraft:overworld",
        "sea_floor_depth": depth,
        "sea_floor_material": sea_floor,
        "foundation_material": foundation,
        "mid_material": mid,
        "top_material": top,
        "sea_material": sea,
    }


def mesa(top="minecraft:red_sand", mid="minecraft:hardened_clay",
         foundation="minecraft:stone", clay="minecraft:white_terracotta",
         hard_clay="minecraft:hardened_clay"):
    return {
        "type": "minecraft:mesa",
        "bryce_pillars": False,
        "has_forest": False,
        "clay_material": clay,
        "hard_clay_material": hard_clay,
        "sea_floor_depth": 7,
        "sea_floor_material": "minecraft:gravel",
        "foundation_material": foundation,
        "mid_material": mid,
        "top_material": top,
        "sea_material": "minecraft:water",
    }


def swamp():
    b = overworld("minecraft:grass_block")
    b["type"] = "minecraft:swamp"
    b["max_puddle_depth_below_sea_level"] = 1
    return b


def frozen_ocean():
    b = overworld("minecraft:grass_block")
    b["type"] = "minecraft:frozen_ocean"
    return b


# id, label, tags, climate, height, surface, fog, water, music, climates
BIOMES = [
    ("autumn_forest", "Autumn Forest",
     ["animal", "monster", "overworld", "forest", "bee_habitat", "neo_flowery"],
     (0.6, 0.8, [0.0, 0.125], 0.0), "default", overworld("minecraft:grass_block", "minecraft:podzol"),
     "forest", "#2E7FA8", "forest", [("medium", 1), ("warm", 1)]),
    ("birch_grove", "Birch Grove",
     ["animal", "monster", "overworld", "birch", "forest", "bee_habitat", "neo_flowery"],
     (0.5, 0.6, [0.0, 0.125], 0.0), "default", overworld("minecraft:grass_block"),
     "birch_forest", "#4E9FE0", "birch_forest", [("medium", 1)]),
    ("flower_meadow", "Flower Meadow",
     ["animal", "monster", "overworld", "meadow", "plains", "bee_habitat", "neo_flowery"],
     (0.7, 0.9, [0.0, 0.125], 0.0), "lowlands", overworld("minecraft:grass_block"),
     "flower_forest", "#53A8E8", "meadow", [("medium", 1), ("warm", 1)]),
    ("ancient_woods", "Ancient Woods",
     ["animal", "monster", "overworld", "roofed", "forest"],
     (0.5, 0.9, [0.0, 0.125], 0.0), "default", overworld("minecraft:grass_block", "minecraft:podzol"),
     "roofed_forest", "#2C6E5A", "roofed_forest", [("medium", 1)]),
    ("pine_forest", "Pine Forest",
     ["animal", "monster", "overworld", "taiga", "forest"],
     (0.25, 0.8, [0.0, 0.25], 0.0), "taiga", overworld("minecraft:grass_block", "minecraft:podzol"),
     "taiga", "#2A7298", "mega_taiga", [("cold", 1), ("medium", 1)]),
    ("redwood_grove", "Redwood Grove",
     ["animal", "monster", "overworld", "mega", "taiga", "forest", "neo_rocky"],
     (0.35, 0.9, [0.0, 0.25], 0.0), "highlands", overworld("minecraft:grass_block", "minecraft:podzol"),
     "mega_taiga", "#2F7A6E", "mega_taiga", [("cold", 1), ("medium", 1)]),
    ("misty_marsh", "Misty Marsh",
     ["animal", "monster", "overworld", "swamp", "neo_wet"],
     (0.6, 0.9, [0.0, 0.125], 0.0), "swamp", swamp(),
     "swampland", "#4B5B3A", "swampland", [("medium", 1)]),
    ("lush_jungle", "Lush Jungle",
     ["animal", "monster", "overworld", "jungle", "rare"],
     (0.95, 0.9, [0.0, 0.125], 0.0), "default", overworld("minecraft:grass_block"),
     "jungle", "#1FA37A", "jungle", [("warm", 1)]),
    ("bamboo_thicket", "Bamboo Thicket",
     ["animal", "monster", "overworld", "bamboo", "jungle"],
     (0.95, 0.95, [0.0, 0.125], 0.0), "default", overworld("minecraft:grass_block"),
     "bamboo_jungle", "#33B08A", "bamboo_jungle", [("warm", 1)]),
    ("savanna_highlands", "Savanna Highlands",
     ["animal", "monster", "overworld", "savanna"],
     (1.2, 0.0, [0.0, 0.125], 0.0), "highlands", overworld("minecraft:grass_block"),
     "savanna_plateau", "#3B9FA8", None, [("warm", 1)]),
    ("acacia_steppe", "Acacia Steppe",
     ["animal", "monster", "overworld", "savanna"],
     (1.1, 0.2, [0.0, 0.125], 0.0), "lowlands", overworld("minecraft:grass_block"),
     "savanna", "#3B9FA8", None, [("warm", 1)]),
    ("red_badlands", "Red Badlands",
     ["animal", "monster", "overworld", "mesa"],
     (2.0, 0.0, [0.0, 0.125], 0.0), "default", mesa(),
     "mesa", "#2F7F8C", "mesa", [("warm", 1)]),
    ("golden_dunes", "Golden Dunes",
     ["monster", "overworld", "desert"],
     (2.0, 0.0, [0.0, 0.125], 0.0), "lowlands",
     overworld("minecraft:sand", "minecraft:sandstone"),
     "desert", "#35A6C9", "desert", [("warm", 1)]),
    ("frostpine_taiga", "Frostpine Taiga",
     ["animal", "monster", "overworld", "taiga", "cold", "frozen"],
     (-0.5, 0.8, [0.125, 0.5], 0.0), "taiga", overworld("minecraft:grass_block", "minecraft:podzol"),
     "cold_taiga", "#2A6E9E", "grove", [("cold", 1), ("frozen", 1)]),
    ("alpine_meadow", "Alpine Meadow",
     ["animal", "monster", "overworld", "meadow", "mountains", "neo_flowery"],
     (0.1, 0.8, [0.0, 0.125], 0.0), "highlands", overworld("minecraft:grass_block"),
     "cold_taiga", "#4F9ED0", "meadow", [("cold", 1), ("medium", 1)]),
    ("stony_summit", "Stony Summit",
     ["monster", "overworld", "mountains", "frozen", "extreme_hills", "neo_rocky"],
     (-0.3, 0.5, [0.125, 0.25], 0.0), "mountains",
     overworld("minecraft:stone", "minecraft:stone", "minecraft:stone", "minecraft:stone"),
     "extreme_hills", "#2C6480", "stony_peaks", [("frozen", 1), ("cold", 1)]),
    ("crystal_peaks", "Crystal Peaks",
     ["monster", "overworld", "mountains", "frozen", "neo_rocky"],
     (-0.6, 0.6, [0.125, 0.5], 0.0), "mountains",
     overworld("minecraft:calcite", "minecraft:stone", "minecraft:deepslate", "minecraft:calcite"),
     "ice_mountains", "#3B8FB0", "frozen_peaks", [("frozen", 1)]),
    ("mushroom_hollow", "Mushroom Hollow",
     ["overworld", "mooshroom_island", "rare"],
     (0.9, 1.0, [0.0, 0.125], 0.0), "mushroom", overworld("minecraft:mycelium"),
     "mushroom_island", "#4A7FA8", None, [("medium", 1)]),
    ("coral_shore", "Coral Shore",
     ["monster", "overworld", "beach", "warm"],
     (1.0, 0.4, [0.0, 0.125], 0.0), "beach",
     overworld("minecraft:sand", "minecraft:sandstone", depth=3),
     "beach", "#12C4C9", None, [("warm", 1), ("lukewarm", 1)]),
    ("kelp_forest", "Kelp Forest",
     ["monster", "overworld", "ocean"],
     (0.5, 0.5, [0.0, 0.125], 0.0), "ocean",
     overworld("minecraft:gravel", "minecraft:dirt", sea_floor="minecraft:sand"),
     "lukewarm_ocean", "#1E8FA8", None, [("lukewarm", 1), ("warm", 1)]),
    ("frozen_sea", "Frozen Sea",
     ["monster", "overworld", "frozen", "ocean", "deep"],
     (-0.8, 0.5, [0.125, 0.5], 0.0), "ocean", frozen_ocean(),
     "frozen_ocean", "#2A5C8A", None, [("frozen", 1)]),
    ("volcanic_wastes", "Volcanic Wastes",
     ["monster", "overworld", "mesa"],
     (2.0, 0.0, [0.0, 0.0], 1.0), "mountains",
     overworld("minecraft:blackstone", "minecraft:basalt", "minecraft:stone", "minecraft:basalt"),
     "hell", "#5A3A2A", "hell", [("warm", 1)]),
    ("whispering_woods", "Whispering Woods",
     ["monster", "overworld", "forest", "roofed"],
     (0.3, 0.7, [0.0, 0.125], 0.0), "default", overworld("minecraft:grass_block", "minecraft:podzol"),
     "roofed_forest_mutated", "#2B4A4A", "roofed_forest_mutated", [("medium", 1)]),
    ("sunflower_plains", "Sunflower Plains",
     ["animal", "monster", "overworld", "plains", "mutated", "bee_habitat", "neo_flowery"],
     (0.8, 0.6, [0.0, 0.125], 0.0), "lowlands", overworld("minecraft:grass_block"),
     "sunflower_plains", "#3E9ED0", None, [("medium", 1), ("warm", 1)]),
    ("lavender_fields", "Lavender Fields",
     ["animal", "monster", "overworld", "flower_forest", "plains", "neo_flowery"],
     (0.7, 0.7, [0.0, 0.125], 0.0), "lowlands", overworld("minecraft:grass_block"),
     "flower_forest", "#6A9FD0", "flower_forest", [("medium", 1), ("warm", 1)]),
    ("salt_flats", "Salt Flats",
     ["monster", "overworld", "desert", "mesa"],
     (2.0, 0.0, [0.0, 0.125], 0.0), "lowlands",
     overworld("minecraft:white_terracotta", "minecraft:stone"),
     "desert", "#66C2D6", "desert", [("warm", 1)]),
    ("emerald_grove", "Emerald Grove",
     ["animal", "monster", "overworld", "extreme_hills", "forest", "mountains", "neo_rocky"],
     (0.4, 0.7, [0.0, 0.125], 0.0), "extreme", overworld("minecraft:grass_block"),
     "extreme_hills_plus_trees", "#2F8F78", "grove", [("medium", 1), ("cold", 1)]),
    ("bleak_moor", "Bleak Moor",
     ["monster", "overworld", "swamp", "plains", "neo_wet"],
     (0.2, 0.9, [0.0, 0.125], 0.0), "swamp",
     overworld("minecraft:coarse_dirt", "minecraft:dirt"),
     "swampland_mutated", "#3A4A44", "swampland", [("cold", 1), ("medium", 1)]),
    ("aurora_taiga", "Aurora Taiga",
     ["animal", "monster", "overworld", "taiga", "cold", "frozen"],
     (-0.8, 0.7, [0.25, 0.6], 0.0), "taiga", overworld("minecraft:grass_block", "minecraft:podzol"),
     "cold_taiga", "#245E8A", "grove", [("frozen", 1), ("cold", 1)]),
    ("sakura_grove", "Sakura Grove",
     ["animal", "monster", "overworld", "cherry_grove", "forest", "neo_flowery"],
     (0.6, 0.7, [0.0, 0.125], 0.0), "default", overworld("minecraft:grass_block"),
     "cherry_grove", "#5AAED0", "cherry_grove", [("medium", 1)]),
]

FEATURES = {
    "boulder_single": {
        "format_version": "1.21.40",
        "minecraft:single_block_feature": {
            "description": {"identifier": "neosmorebiomes:boulder_single"},
            "places_block": "minecraft:cobblestone",
            "enforce_survivability_rules": True,
            "enforce_placement_rules": True,
            "may_replace": ["minecraft:air"],
        },
    },
    "boulder_scatter": {
        "format_version": "1.21.40",
        "minecraft:scatter_feature": {
            "description": {"identifier": "neosmorebiomes:boulder_scatter"},
            "places_feature": "neosmorebiomes:boulder_single",
            "distribution": {
                "iterations": 3,
                "scatter_chance": 35,
                "x": {"distribution": "uniform", "extent": [0, 15]},
                "z": {"distribution": "uniform", "extent": [0, 15]},
                "y": "query.heightmap(variable.worldx, variable.worldz)",
            },
        },
    },
    "poppy_single": {
        "format_version": "1.21.40",
        "minecraft:single_block_feature": {
            "description": {"identifier": "neosmorebiomes:poppy_single"},
            "places_block": "minecraft:poppy",
            "enforce_survivability_rules": True,
            "enforce_placement_rules": True,
            "may_replace": ["minecraft:air"],
        },
    },
    "poppy_scatter": {
        "format_version": "1.21.40",
        "minecraft:scatter_feature": {
            "description": {"identifier": "neosmorebiomes:poppy_scatter"},
            "places_feature": "neosmorebiomes:poppy_single",
            "distribution": {
                "iterations": 4,
                "scatter_chance": 45,
                "x": {"distribution": "uniform", "extent": [0, 15]},
                "z": {"distribution": "uniform", "extent": [0, 15]},
                "y": "query.heightmap(variable.worldx, variable.worldz)",
            },
        },
    },
    "daisy_single": {
        "format_version": "1.21.40",
        "minecraft:single_block_feature": {
            "description": {"identifier": "neosmorebiomes:daisy_single"},
            "places_block": "minecraft:oxeye_daisy",
            "enforce_survivability_rules": True,
            "enforce_placement_rules": True,
            "may_replace": ["minecraft:air"],
        },
    },
    "daisy_scatter": {
        "format_version": "1.21.40",
        "minecraft:scatter_feature": {
            "description": {"identifier": "neosmorebiomes:daisy_scatter"},
            "places_feature": "neosmorebiomes:daisy_single",
            "distribution": {
                "iterations": 3,
                "scatter_chance": 35,
                "x": {"distribution": "uniform", "extent": [0, 15]},
                "z": {"distribution": "uniform", "extent": [0, 15]},
                "y": "query.heightmap(variable.worldx, variable.worldz)",
            },
        },
    },
}

RULES = [
    ("boulder_rule", "neosmorebiomes:boulder_scatter", "neo_rocky", 1),
    ("poppy_rule", "neosmorebiomes:poppy_scatter", "neo_flowery", 1),
    ("daisy_rule", "neosmorebiomes:daisy_scatter", "neo_flowery", 1),
]


def biome_json(b):
    ident, label, tags, (temp, downfall, snow, ash), height, surface, fog, water, music, cats = b
    components = {
        "minecraft:climate": {
            "temperature": temp,
            "downfall": downfall,
            "snow_accumulation": snow,
        },
        "minecraft:overworld_height": {"noise_type": height},
        "minecraft:surface_builder": {"builder": surface},
        "minecraft:overworld_generation_rules": {
            "generate_for_climates": [[c, w] for c, w in cats],
        },
        "minecraft:tags": {"tags": sorted(set(tags + ["overworld", "no_legacy_worldgen"]))},
    }
    if ash > 0:
        components["minecraft:climate"]["ash"] = ash
    return {"format_version": "1.26.0", "minecraft:biome": {"description": {"identifier": f"neosmorebiomes:{ident}"}, "components": components}}


def client_biome_json(b):
    ident, label, tags, climate, height, surface, fog, water, music, cats = b
    components = {
        "minecraft:fog_appearance": {"fog_identifier": f"minecraft:fog_{fog}"},
        "minecraft:water_appearance": {"surface_color": water},
        "minecraft:atmosphere_identifier": {"atmosphere_identifier": "minecraft:default_atmospherics"},
        "minecraft:color_grading_identifier": {"color_grading_identifier": "minecraft:default_color_grading"},
        "minecraft:lighting_identifier": {"lighting_identifier": "minecraft:default_lighting"},
        "minecraft:water_identifier": {"water_identifier": "minecraft:default_water"},
        "minecraft:ambient_sounds": {
            "underwater_addition": {"asset": "ambient.underwater.additions", "chance": 0.01},
            "underwater_loop": "ambient.underwater.loop",
        },
    }
    if music:
        components["minecraft:biome_music"] = {"music_definition": music}
    return {"format_version": "1.21.120", "minecraft:client_biome": {"description": {"identifier": f"neosmorebiomes:{ident}"}, "components": components}}


def feature_rule_json(rule_id, feature, tag, iterations):
    return {
        "format_version": "1.21.40",
        "minecraft:feature_rules": {
            "description": {"identifier": f"neosmorebiomes:{rule_id}", "places_feature": feature},
            "conditions": {
                "placement_pass": "surface_pass",
                "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==", "value": tag},
            },
            "distribution": {
                "iterations": iterations,
                "x": {"distribution": "uniform", "extent": [0, 15]},
                "y": "query.heightmap(variable.worldx, variable.worldz)",
                "z": {"distribution": "uniform", "extent": [0, 15]},
            },
        },
    }


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for d in ("biomes", "features", "feature_rules"):
        (BP / d).mkdir(parents=True, exist_ok=True)
    (RP / "biomes").mkdir(parents=True, exist_ok=True)
    (RP / "texts").mkdir(parents=True, exist_ok=True)

    for b in BIOMES:
        ident = b[0]
        (BP / "biomes" / f"{ident}.biome.json").write_text(json.dumps(biome_json(b), indent=1))
        (RP / "biomes" / f"{ident}.client_biome.json").write_text(json.dumps(client_biome_json(b), indent=1))

    for name, data in FEATURES.items():
        (BP / "features" / f"{name}.json").write_text(json.dumps(data, indent=1))
    for rule_id, feature, tag, it in RULES:
        (BP / "feature_rules" / f"{rule_id}.json").write_text(json.dumps(feature_rule_json(rule_id, feature, tag, it), indent=1))

    bp_header, bp_data = ns("bp_header"), ns("bp_data")
    rp_header, rp_res = ns("rp_header"), ns("rp_res")
    (BP / "manifest.json").write_text(json.dumps({
        "format_version": 2,
        "header": {
            "name": "Neo's More Biomes BP",
            "description": f"{len(BIOMES)} custom overworld biomes with varied terrain, flora and natural placement. Requires Neo's More Mobs + Alex's Mobs. Enable the 'Custom Biomes' experiment if the biomes do not appear.",
            "uuid": bp_header,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 10],
        },
        "modules": [{"type": "data", "uuid": bp_data, "version": [1, 0, 0]}],
        "dependencies": [
            {"uuid": MOB_BP_UUID, "version": [1, 0, 0]},
            {"uuid": MOB_RP_UUID, "version": [1, 0, 0]},
            {"uuid": rp_header, "version": [1, 0, 0]},
        ],
        "metadata": {"authors": ["Neo"], "credits": ["Requires Neo's More Mobs + Alex's Mobs"]},
    }, indent=2))
    (RP / "manifest.json").write_text(json.dumps({
        "format_version": 2,
        "header": {
            "name": "Neo's More Biomes RP",
            "description": f"Fog, water and music for {len(BIOMES)} custom biomes.",
            "uuid": rp_header,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 10],
        },
        "modules": [{"type": "resources", "uuid": rp_res, "version": [1, 0, 0]}],
        "dependencies": [{"uuid": MOB_RP_UUID, "version": [1, 0, 0]}],
        "metadata": {"authors": ["Neo"], "credits": ["Requires Neo's More Mobs + Alex's Mobs"]},
    }, indent=2))

    (RP / "texts" / "en_US.lang").write_text(
        "pack.name=Neo's More Biomes\n"
        f"pack.description={len(BIOMES)} custom overworld biomes with new terrain, flora and fog.\n")
    (RP / "texts" / "languages.json").write_text(json.dumps(["en_US"], indent=1))

    from PIL import Image, ImageDraw, ImageFont
    image = Image.new("RGBA", (256, 256), "#18251f")
    draw = ImageDraw.Draw(image)
    big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    draw.rounded_rectangle((12, 12, 244, 244), radius=26, outline="#7FC08A", width=4)
    draw.text((128, 68), "NEO'S MORE", font=big, fill="#A8E0A0", anchor="ma")
    draw.text((128, 98), "BIOMES", font=big, fill="#A8E0A0", anchor="ma")
    draw.text((128, 138), "TERRAIN & FLORA", font=small, fill="#DCE8D8", anchor="ma")
    draw.text((128, 188), f"{len(BIOMES)} BIOMES", font=big, fill="#FFFFFF", anchor="ma")
    icon = OUT / "pack_icon.png"
    image.save(icon)
    shutil.copyfile(icon, BP / "pack_icon.png")
    shutil.copyfile(icon, RP / "pack_icon.png")

    output = ROOT / "NeosMoreBiomes.mcaddon"
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for pack in (BP, RP):
            for path in pack.rglob("*"):
                if path.is_file():
                    zf.write(path, str(path.relative_to(OUT)))
    print(output, len(BIOMES), "biomes")


if __name__ == "__main__":
    main()
