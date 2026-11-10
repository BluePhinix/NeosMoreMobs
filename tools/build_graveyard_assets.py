#!/usr/bin/env python3
"""Create the Forgotten Soul + Graveyard assets used by the unified pack."""
import json
import shutil
from pathlib import Path

ROOT = Path("/workspace/Neo's more mobs")
CHRONO = Path("/workspace/Chronoscape Echoes of the Shattered Epoch")
STAGE = ROOT / "work" / "graveyard_assets"
BP = STAGE / "BP"
RP = STAGE / "RP"


def w(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1) if not isinstance(data, str) else data)


def main():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    for d in ("entities", "spawn_rules", "loot_tables/entities", "loot_tables/chests",
              "features", "feature_rules", "structures"):
        (BP / d).mkdir(parents=True, exist_ok=True)
    for d in ("entity", "models/entity", "animations", "animation_controllers",
              "render_controllers", "textures/entity/neosmoremobs"):
        (RP / d).mkdir(parents=True, exist_ok=True)

    # ---- geometry (rename identifier)
    geo = json.loads((CHRONO / "RP/models/entity/Fahmi2.geo.json").read_text())
    for g in geo["minecraft:geometry"]:
        if g["description"]["identifier"] == "geometry.soul":
            g["description"]["identifier"] = "geometry.neosmoremobs.forgotten_soul"
    w(RP / "models/entity/forgotten_soul.geo.json", geo)

    # ---- texture
    shutil.copyfile(CHRONO / "RP/textures/entity/forgotten_soul.png",
                    RP / "textures/entity/neosmoremobs/forgotten_soul.png")

    # ---- animations (rename ids)
    anim_src = (CHRONO / "RP/animations/forgotten_soul.animation.json").read_text()
    anim_src = anim_src.replace("animation.soul.flying", "animation.neosmoremobs.forgotten_soul.flying")
    anim_src = anim_src.replace("animation.soul.attack", "animation.neosmoremobs.forgotten_soul.attack")
    (RP / "animations/forgotten_soul.animation.json").write_text(anim_src)

    # ---- controller (rename id)
    ctrl_src = (CHRONO / "RP/animation_controllers/forgotten_soul.animation_controllers.json").read_text()
    ctrl_src = ctrl_src.replace("controller.animation.soul.general",
                                "controller.animation.neosmoremobs.forgotten_soul")
    (RP / "animation_controllers/forgotten_soul.animation_controllers.json").write_text(ctrl_src)

    # ---- render controller
    w(RP / "render_controllers/forgotten_soul.render_controllers.json", {
        "format_version": "1.10.0",
        "render_controllers": {
            "controller.render.neosmoremobs.forgotten_soul": {
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": ["Texture.default"],
            }
        },
    })

    # ---- client entity
    w(RP / "entity/forgotten_soul.entity.json", {
        "format_version": "1.10.0",
        "minecraft:client_entity": {
            "description": {
                "identifier": "neosmoremobs:forgotten_soul",
                "materials": {"default": "entity_alphablend"},
                "textures": {"default": "textures/entity/neosmoremobs/forgotten_soul"},
                "geometry": {"default": "geometry.neosmoremobs.forgotten_soul"},
                "animations": {
                    "flying": "animation.neosmoremobs.forgotten_soul.flying",
                    "attack": "animation.neosmoremobs.forgotten_soul.attack",
                    "general": "controller.animation.neosmoremobs.forgotten_soul",
                },
                "scripts": {"animate": ["general"]},
                "render_controllers": ["controller.render.neosmoremobs.forgotten_soul"],
                "spawn_egg": {"base_color": "#14141F", "overlay_color": "#6C7BFF"},
            }
        },
    })

    # ---- behavior entity
    w(BP / "entities/forgotten_soul.json", {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {
                "identifier": "neosmoremobs:forgotten_soul",
                "is_spawnable": True,
                "is_summonable": True,
                "is_experimental": False,
            },
            "components": {
                "minecraft:type_family": {"family": ["undead", "monster", "soul"]},
                "minecraft:collision_box": {"width": 0.6, "height": 1.8},
                "minecraft:health": {"value": 15, "max": 15},
                "minecraft:physics": {},
                "minecraft:pushable_by_entity": {},
                "minecraft:pushable_by_block": {},
                "minecraft:movement": {"value": 0.25},
                "minecraft:movement.fly": {},
                "minecraft:can_fly": {},
                "minecraft:navigation.fly": {"can_path_over_water": True, "can_path_over_lava": False},
                "minecraft:damage_sensor": {"triggers": [{"cause": "fall", "deals_damage": "no"}]},
                "minecraft:attack": {"damage": 3},
                "minecraft:behavior.hurt_by_target": {"priority": 1},
                "minecraft:behavior.nearest_attackable_target": {
                    "priority": 2,
                    "must_see": True,
                    "reselect_targets": True,
                    "entity_types": [{
                        "filters": {"test": "is_family", "subject": "other", "value": "player"},
                        "max_dist": 24,
                    }],
                },
                "minecraft:behavior.melee_attack": {"priority": 3, "speed_multiplier": 1.2, "track_target": True},
                "minecraft:behavior.random_fly": {
                    "priority": 5, "xz_dist": 12, "y_dist": 5,
                    "speed_multiplier": 1.0, "avoid_damage_blocks": True,
                },
                "minecraft:behavior.look_at_player": {"priority": 7, "look_distance": 6, "probability": 0.02},
                "minecraft:behavior.random_look_around": {"priority": 8},
                "minecraft:nameable": {},
                "minecraft:is_hidden_when_invisible": {},
                "minecraft:conditional_bandwidth_optimization": {},
                "minecraft:loot": {"table": "loot_tables/entities/forgotten_soul.json"},
                "minecraft:experience_reward": {"on_death": "query.last_hit_by_player ? Math.Random(2,5) : 0"},
            },
        },
    })

    # ---- spawn rule: graveyard soil only, overworld only
    w(BP / "spawn_rules/forgotten_soul.json", {
        "format_version": "1.8.0",
        "minecraft:spawn_rules": {
            "description": {
                "identifier": "neosmoremobs:forgotten_soul",
                "population_control": "monster",
            },
            "conditions": [{
                "minecraft:spawns_on_surface": {},
                "minecraft:spawns_on_block_filter": ["minecraft:soul_soil"],
                "minecraft:brightness_filter": {"min": 0, "max": 15, "adjust_for_weather": False},
                "minecraft:difficulty_filter": {"min": "easy", "max": "hard"},
                "minecraft:weight": {"default": 40},
                "minecraft:herd": {"min_size": 1, "max_size": 3},
                "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==", "value": "overworld"},
            }],
        },
    })

    # ---- loot
    w(BP / "loot_tables/entities/forgotten_soul.json", {
        "pools": [
            {"rolls": 1, "entries": [{"type": "item", "name": "minecraft:phantom_membrane", "weight": 1,
                                      "functions": [{"function": "set_count", "count": {"min": 0, "max": 1}}]}]},
            {"rolls": 1, "entries": [{"type": "item", "name": "minecraft:bone", "weight": 1,
                                      "functions": [{"function": "set_count", "count": {"min": 0, "max": 2}}]}]},
            {"rolls": 1, "conditions": [{"condition": "random_chance", "chance": 0.05}],
             "entries": [{"type": "item", "name": "minecraft:ender_pearl", "weight": 1}]},
        ]
    })
    w(BP / "loot_tables/chests/graveyard.json", {
        "pools": [
            {"rolls": 2, "entries": [
                {"type": "item", "name": "minecraft:bone", "weight": 6,
                 "functions": [{"function": "set_count", "count": {"min": 1, "max": 4}}]},
                {"type": "item", "name": "minecraft:phantom_membrane", "weight": 3,
                 "functions": [{"function": "set_count", "count": {"min": 1, "max": 2}}]},
                {"type": "item", "name": "minecraft:soul_torch", "weight": 3,
                 "functions": [{"function": "set_count", "count": {"min": 1, "max": 3}}]},
                {"type": "item", "name": "minecraft:emerald", "weight": 1,
                 "functions": [{"function": "set_count", "count": {"min": 0, "max": 2}}]},
            ]},
            {"rolls": 1, "conditions": [{"condition": "random_chance", "chance": 0.08}],
             "entries": [{"type": "item", "name": "minecraft:golden_apple", "weight": 1}]},
        ]
    })

    # ---- structure feature + rule
    w(BP / "features/graveyard.json", {
        "format_version": "1.13.0",
        "minecraft:structure_template_feature": {
            "description": {"identifier": "neosmoremobs:graveyard"},
            "structure_name": "mystructure:graveyard",
            "adjustment_radius": 8,
            "facing_direction": "random",
            "constraints": {
                "grounded": {},
                "unburied": {},
                "block_intersection": {
                    "block_allowlist": [
                        "minecraft:air", "minecraft:grass_block", "minecraft:dirt",
                        "minecraft:coarse_dirt", "minecraft:podzol", "minecraft:short_grass",
                        "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern",
                        "minecraft:snow_layer", "minecraft:poppy", "minecraft:dandelion",
                        "minecraft:oxeye_daisy", "minecraft:cornflower", "minecraft:azure_bluet",
                        "minecraft:lily_of_the_valley", "minecraft:soul_soil",
                    ]
                },
            },
        },
    })
    w(BP / "feature_rules/graveyard_rule.json", {
        "format_version": "1.13.0",
        "minecraft:feature_rules": {
            "description": {
                "identifier": "neosmoremobs:graveyard_rule",
                "places_feature": "neosmoremobs:graveyard",
            },
            "conditions": {
                "placement_pass": "surface_pass",
                "minecraft:biome_filter": [{
                    "any_of": [
                        {"test": "has_biome_tag", "operator": "==", "value": t}
                        for t in ("forest", "taiga", "plains", "swamp", "savanna", "cherry_grove")
                    ]
                }],
            },
            "distribution": {
                "iterations": 1,
                "scatter_chance": 0.04,
                "x": 0,
                "y": "query.heightmap(variable.worldx, variable.worldz)",
                "z": 0,
            },
        },
    })

    (STAGE / "lang.txt").write_text(
        "entity.neosmoremobs:forgotten_soul.name=Forgotten Soul\n"
        "item.spawn_egg.entity.neosmoremobs:forgotten_soul.name=Forgotten Soul Spawn Egg\n"
    )
    print("staged graveyard assets at", STAGE)


if __name__ == "__main__":
    main()
