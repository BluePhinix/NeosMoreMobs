#!/usr/bin/env python3
"""Create Miner Zombie + Void Dealer assets for the unified pack."""
import copy
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path("/workspace/Neo's more mobs")
SAMPLES = Path("/workspace/bedrock-samples-v1.26.40.05-full (1)")
CHRONO = Path("/workspace/Chronoscape Echoes of the Shattered Epoch")
END = Path("/workspace/endreimagined/RP")
STAGE = ROOT / "work" / "more_mobs_assets"
BP = STAGE / "BP"
RP = STAGE / "RP"

ZOMBIE_TEX = SAMPLES / "resource_pack/textures/entity/zombie/zombie.png"
ZOMBIE_CLIENT = SAMPLES / "resource_pack/entity/zombie.entity.json"
MINER_GEO_SRC = ROOT / "model.geo (21).json"
MINER_TEX_SRC = ROOT / "texture (3) (16).png"


def w(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1) if not isinstance(data, str) else data)


def _box_faces(u, v, sx, sy, sz):
    return {
        "north": (u + sz, v + sz, u + sz + sx, v + sz + sy),
        "east": (u, v + sz, u + sz, v + sz + sy),
        "south": (u + 2 * sz + sx, v + sz, u + 2 * sz + 2 * sx, v + sz + sy),
        "west": (u + sz + sx, v + sz, u + 2 * sz + sx, v + sz + sy),
        "up": (u + sz, v, u + sz + sx, v + sz),
        "down": (u + sz + sx, v, u + 2 * sx + sz, v + sz),
    }


def _paint_patch(draw, uv, sx, sy, sz, base, top=None):
    for face, (x0, y0, x1, y1) in _box_faces(uv[0], uv[1], sx, sy, sz).items():
        colour = top if (face == "up" and top) else base
        draw.rectangle((int(x0), int(y0), int(x1) - 1, int(y1) - 1), fill=colour)


def _paint_helmet_patches(im):
    d = ImageDraw.Draw(im)
    yellow = (214, 166, 42, 255)
    yellow_top = (232, 185, 60, 255)
    yellow_dark = (188, 143, 30, 255)
    brim = (138, 100, 22, 255)
    brim_top = (160, 117, 28, 255)
    dark = (58, 52, 40, 255)
    lens = (255, 246, 194, 255)
    # unused hat-shell area: clear so it cannot render stray pixels
    d.rectangle((32, 19, 63, 34), fill=(0, 0, 0, 0))
    # dome faces
    d.rectangle((49, 35, 57, 43), fill=yellow)
    d.rectangle((49, 35, 57, 35), fill=yellow_top)
    d.rectangle((49, 43, 57, 43), fill=yellow_dark)
    d.rectangle((49, 44, 57, 52), fill=yellow_dark)
    for x0 in (0, 9, 18, 27):
        d.rectangle((x0, 57, x0 + 8, 61), fill=yellow)
        d.rectangle((x0, 62, x0 + 8, 62), fill=yellow_dark)
    # solid patches for brim / lamp housing / lens
    d.rectangle((36, 57, 39, 60), fill=brim)
    d.rectangle((36, 57, 39, 57), fill=brim_top)
    d.rectangle((41, 57, 44, 60), fill=dark)
    d.rectangle((46, 57, 49, 60), fill=lens)
    return im


def build_miner_texture(dst):
    """Use the user-provided 64x64 texture; paint the helmet into free space."""
    im = Image.open(MINER_TEX_SRC).convert("RGBA")
    if im.size != (64, 64):
        im = im.resize((64, 64), Image.NEAREST)
    _paint_helmet_patches(im).save(dst)


def paint_miner_icon(dst):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    yellow = (214, 166, 42, 255)
    yellow_top = (232, 185, 60, 255)
    brim = (138, 100, 22, 255)
    dark = (58, 52, 40, 255)
    lens = (255, 246, 194, 255)
    d.rectangle((1, 9, 14, 11), fill=brim)
    d.rectangle((3, 4, 12, 9), fill=yellow)
    d.rectangle((3, 4, 12, 5), fill=yellow_top)
    d.rectangle((7, 6, 8, 8), fill=dark)
    d.point((7, 6), fill=lens)
    im.save(dst)


def build_helmet_armor_texture(dst):
    """64x64 armor texture using the same helmet UV patches as the mob."""
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    _paint_helmet_patches(im).save(dst)


def build_helmet_armor_geometry():
    """Head-slot armor model wearing the same hard hat as the miner zombie."""
    faces = {
        "up": {"uv": [49, 35], "uv_size": [9, 9]},
        "down": {"uv": [49, 44], "uv_size": [9, 9]},
        "north": {"uv": [0, 57], "uv_size": [9, 6]},
        "south": {"uv": [9, 57], "uv_size": [9, 6]},
        "east": {"uv": [18, 57], "uv_size": [9, 6]},
        "west": {"uv": [27, 57], "uv_size": [9, 6]},
    }
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.neosmoremobs.miner_helmet_armor",
                "texture_width": 64,
                "texture_height": 64,
                "visible_bounds_width": 2,
                "visible_bounds_height": 3,
                "visible_bounds_offset": [0, 1.5, 0],
            },
            "bones": [{
                "name": "head", "pivot": [0, 24, 0],
                "cubes": [
                    {"origin": [-4.5, 30, -4.5], "size": [9, 4, 9], "uv": faces},
                    {"origin": [-5, 29, -5], "size": [10, 1, 10], "uv": _face_uv(37, 58, 1, 1)},
                    {"origin": [-1.5, 31, -5.5], "size": [3, 3, 1], "uv": _face_uv(42, 58, 1, 1)},
                    {"origin": [-1, 31.5, -6], "size": [2, 2, 1], "uv": _face_uv(47, 58, 1, 1)},
                ],
            }],
        }],
    }


def _face_uv(u, v, w, h):
    return {f: {"uv": [u, v], "uv_size": [w, h]}
            for f in ("north", "east", "south", "west", "up", "down")}


def build_miner_geometry():
    """The user's model.geo (21).json exactly (UVs and pickaxe grip kept),
    plus a helmet bone. Parsed in the left hand, so the pickaxe rides on
    leftArm for the animations."""
    geo = json.loads(MINER_GEO_SRC.read_text())
    g = geo["minecraft:geometry"][0]
    for bone in g["bones"]:
        if bone["name"] == "root_item":
            # attachable-only binding; makes the game re-bind the pickaxe to
            # an item-slot bone instead of the authored position
            bone.pop("binding", None)
            bone["parent"] = "leftArm"
    g["bones"].append({
        "name": "helmet", "parent": "head", "pivot": [0, 24, -0.25],
        "cubes": [
            {
                "origin": [-4.5, 30, -4.75], "size": [9, 4, 9],
                "uv": {
                    "up": {"uv": [49, 35], "uv_size": [9, 9]},
                    "down": {"uv": [49, 44], "uv_size": [9, 9]},
                    "north": {"uv": [0, 57], "uv_size": [9, 6]},
                    "south": {"uv": [9, 57], "uv_size": [9, 6]},
                    "east": {"uv": [18, 57], "uv_size": [9, 6]},
                    "west": {"uv": [27, 57], "uv_size": [9, 6]},
                },
            },
            {"origin": [-5, 29, -5.25], "size": [10, 1, 10], "uv": _face_uv(37, 58, 1, 1)},
            {"origin": [-1.5, 31, -5.75], "size": [3, 3, 1], "uv": _face_uv(42, 58, 1, 1)},
            {"origin": [-1, 31.5, -6.25], "size": [2, 2, 1], "uv": _face_uv(47, 58, 1, 1)},
        ],
    })
    return geo


def build_miner_animations():
    """Clips use full [x,y,z] keyframes only: Bedrock rejects per-axis
    keyframe objects ("child 'x' not valid here")."""
    import math as _m

    steps = 8

    def cycle(length, fn):
        return {f"{length * i / steps:.3f}": fn(2 * _m.pi * i / steps)
                for i in range(steps + 1)}

    def walk_clip(length, leg_amp, arm_amp, pickaxe_amp, bob, lean, twist):
        def side(amp):
            return cycle(length, lambda a: [amp * _m.sin(a), 0, 0])

        return {
            "loop": True,
            "animation_length": length,
            "bones": {
                "rightLeg": {"rotation": side(leg_amp)},
                "leftLeg": {"rotation": side(-leg_amp)},
                "rightArm": {"rotation": side(-arm_amp)},
                "leftArm": {"rotation": side(pickaxe_amp)},
                "body": {
                    "rotation": cycle(length, lambda a: [lean, twist * _m.sin(a), 0]),
                    "position": cycle(length, lambda a: [0, 0.1 + bob * abs(_m.sin(a)), 0]),
                },
            },
        }

    idle_times = [0, 0.5, 1.0, 1.5, 2.0]

    def keys(vals):
        return {str(t): v for t, v in zip(idle_times, vals)}

    idle = {
        "loop": True,
        "animation_length": 2.0,
        "bones": {
            "body": {
                "rotation": keys([
                    [0, 0, 0], [1.2, 0, -0.8], [0, 0, 0], [-1.2, 0, 0.8], [0, 0, 0],
                ]),
                "position": keys([
                    [0, 0, 0], [0, 0.15, 0], [0, 0, 0], [0, 0.15, 0], [0, 0, 0],
                ]),
            },
            "rightArm": {
                "rotation": keys([
                    [0, 0, -1.5], [-2.5, 0, 0], [0, 0, 1.5], [2.5, 0, 0], [0, 0, -1.5],
                ]),
            },
            "leftArm": {
                "rotation": keys([
                    [0, 0, 1.5], [1.5, 0, 0], [0, 0, -1.5], [-1.5, 0, 0], [0, 0, 1.5],
                ]),
            },
        },
    }

    attack = {
        "loop": False,
        "animation_length": 0.62,
        "bones": {
            "leftArm": {
                "rotation": {
                    "0.0": [0, 0, 0],
                    "0.14": [-62, -8, -6],
                    "0.3": [72, 6, 8],
                    "0.42": [34, 3, 4],
                    "0.62": [0, 0, 0],
                },
            },
            "rightArm": {
                "rotation": {
                    "0.0": [0, 0, 0],
                    "0.14": [18, 0, 0],
                    "0.3": [-14, 0, 0],
                    "0.62": [0, 0, 0],
                },
            },
            "body": {
                "rotation": {
                    "0.0": [0, 0, 0],
                    "0.14": [0, -9, 0],
                    "0.3": [6, 9, 0],
                    "0.62": [0, 0, 0],
                },
            },
        },
    }

    return {
        "format_version": "1.8.0",
        "animations": {
            "animation.neosmoremobs.miner_zombie.idle": idle,
            "animation.neosmoremobs.miner_zombie.walk": walk_clip(0.9, 31, 23, 12, 0.3, 1.5, 4),
            "animation.neosmoremobs.miner_zombie.run": walk_clip(0.7, 42, 34, 20, 0.5, 8, 7),
            "animation.neosmoremobs.miner_zombie.attack": attack,
        },
    }


MINER_ATTACK_CONTROLLER = {
    "format_version": "1.10.0",
    "animation_controllers": {
        "controller.animation.neosmoremobs.miner_zombie.attack": {
            "initial_state": "default",
            "states": {
                "default": {
                    "transitions": [{"attack": "variable.attack_time >= 0.0"}],
                },
                "attack": {
                    "blend_transition": 0.1,
                    "animations": ["attack"],
                    "transitions": [{"default": "variable.attack_time < 0.0"}],
                },
            },
        },
    },
}


def main():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    for d in ("entities", "spawn_rules", "loot_tables/entities", "scripts",
              "items", "recipes"):
        (BP / d).mkdir(parents=True, exist_ok=True)
    for d in ("entity", "models/entity", "animations", "render_controllers",
              "attachables", "textures/entity/neosmoremobs", "textures/items",
              "textures/models/armor"):
        (RP / d).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------ miner zombie
    build_miner_texture(RP / "textures/entity/neosmoremobs/miner_zombie.png")
    w(RP / "models/entity/miner_zombie.geo.json", build_miner_geometry())
    w(RP / "animations/miner_zombie.animation.json", build_miner_animations())
    w(RP / "animation_controllers/miner_zombie.animation_controllers.json",
      MINER_ATTACK_CONTROLLER)

    zc = json.loads(ZOMBIE_CLIENT.read_text())
    desc = zc["minecraft:client_entity"]["description"]
    desc["identifier"] = "neosmoremobs:miner_zombie"
    desc["textures"]["default"] = "textures/entity/neosmoremobs/miner_zombie"
    desc["textures"]["baby"] = "textures/entity/neosmoremobs/miner_zombie"
    desc["geometry"]["default"] = "geometry.miner_zombie"
    desc["render_controllers"] = ["controller.render.neosmoremobs.miner_zombie"]
    desc["spawn_egg"] = {"base_color": "#3B5B3B", "overlay_color": "#D6A62A"}
    # Drop the vanilla controller set inherited from the zombie client; the
    # miner uses its own idle/walk/run/attack wiring below.
    desc.pop("animation_controllers", None)
    desc["animations"] = {
        "humanoid_big_head": "animation.humanoid.big_head",
        "look_at_target_default": "animation.humanoid.look_at_target.default",
        "look_at_target_gliding": "animation.humanoid.look_at_target.gliding",
        "look_at_target_swimming": "animation.humanoid.look_at_target.swimming",
        "idle": "animation.neosmoremobs.miner_zombie.idle",
        "walk": "animation.neosmoremobs.miner_zombie.walk",
        "run": "animation.neosmoremobs.miner_zombie.run",
        "attack": "animation.neosmoremobs.miner_zombie.attack",
        "look_at_target_controller": "controller.animation.humanoid.look_at_target",
        "humanoid_big_head_controller": "controller.animation.humanoid.baby_big_head",
        "move_controller": "controller.animation.neosmoremobs.locomotion",
        "attack_controller": "controller.animation.neosmoremobs.miner_zombie.attack",
    }
    desc["scripts"]["animate"] = [
        "look_at_target_controller",
        "move_controller",
        "attack_controller",
        "humanoid_big_head_controller",
    ]
    w(RP / "entity/miner_zombie.entity.json", zc)

    w(BP / "entities/miner_zombie.json", {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {
                "identifier": "neosmoremobs:miner_zombie",
                "is_spawnable": True,
                "is_summonable": True,
                "spawn_category": "monster",
            },
            "components": {
                "minecraft:type_family": {"family": ["zombie", "undead", "monster"]},
                "minecraft:collision_box": {"width": 0.6, "height": 1.9},
                "minecraft:health": {"value": 20, "max": 20},
                "minecraft:attack": {"damage": 3},
                "minecraft:movement": {"value": 0.23},
                "minecraft:navigation.walk": {"can_path_over_water": True, "avoid_water": True, "avoid_damage_blocks": True},
                "minecraft:physics": {},
                "minecraft:breathable": {"total_supply": 15, "suffocate_time": 0},
                "minecraft:nameable": {},
                "minecraft:pushable_by_entity": {},
                "minecraft:pushable_by_block": {},
                "minecraft:despawn": {"despawn_from_distance": {}},
                "minecraft:conditional_bandwidth_optimization": {},
                "minecraft:behavior.hurt_by_target": {"priority": 1},
                "minecraft:behavior.nearest_attackable_target": {
                    "priority": 2, "must_see": True, "reselect_targets": True, "within_radius": 25,
                    "entity_types": [{"filters": {"test": "is_family", "subject": "other", "value": "player"}, "max_dist": 35}],
                },
                "minecraft:behavior.melee_attack": {"priority": 3, "speed_multiplier": 1.0, "track_target": True},
                "minecraft:behavior.random_stroll": {"priority": 6, "speed_multiplier": 1.0},
                "minecraft:behavior.look_at_player": {"priority": 7, "look_distance": 6, "probability": 0.02},
                "minecraft:behavior.random_look_around": {"priority": 8},
                "minecraft:loot": {"table": "loot_tables/entities/miner_zombie.json"},
                "minecraft:experience_reward": {"on_death": "query.last_hit_by_player ? Math.Random(2,4) : 0"},
            },
        },
    })
    w(BP / "spawn_rules/miner_zombie.json", {
        "format_version": "1.8.0",
        "minecraft:spawn_rules": {
            "description": {"identifier": "neosmoremobs:miner_zombie", "population_control": "monster"},
            "conditions": [
                {
                    "minecraft:spawns_underground": {},
                    "minecraft:brightness_filter": {"min": 0, "max": 7, "adjust_for_weather": False},
                    "minecraft:difficulty_filter": {"min": "easy", "max": "hard"},
                    "minecraft:weight": {"default": 12},
                    "minecraft:herd": {"min_size": 1, "max_size": 2},
                    "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==", "value": "overworld"},
                },
                {
                    "minecraft:spawns_on_surface": {},
                    "minecraft:brightness_filter": {"min": 0, "max": 7, "adjust_for_weather": False},
                    "minecraft:difficulty_filter": {"min": "easy", "max": "hard"},
                    "minecraft:weight": {"default": 6},
                    "minecraft:herd": {"min_size": 1, "max_size": 2},
                    "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==", "value": "overworld"},
                },
            ],
        },
    })
    w(BP / "loot_tables/entities/miner_zombie.json", {
        "pools": [
            {"rolls": 1, "entries": [{"type": "item", "name": "minecraft:rotten_flesh", "weight": 1,
                                      "functions": [{"function": "set_count", "count": {"min": 0, "max": 2}}]}]},
            {"rolls": 1, "entries": [{"type": "item", "name": "minecraft:coal", "weight": 1,
                                      "functions": [{"function": "set_count", "count": {"min": 0, "max": 2}}]}]},
            {"rolls": 1, "entries": [{"type": "item", "name": "minecraft:iron_nugget", "weight": 1,
                                      "functions": [{"function": "set_count", "count": {"min": 0, "max": 1}}]}]},
            {"rolls": 1, "conditions": [{"condition": "random_chance", "chance": 0.05}],
             "entries": [{"type": "item", "name": "minecraft:iron_pickaxe", "weight": 1}]},
            {"rolls": 1, "conditions": [{"condition": "random_chance_with_looting",
                                         "chance": 0.08, "looting_multiplier": 0.02}],
             "entries": [{"type": "item", "name": "neosmoremobs:miner_helmet", "weight": 1}]},
        ]
    })

    # ------------------------------------------------------- miner helmet item
    HELMET = "neosmoremobs:miner_helmet"
    paint_miner_icon(RP / "textures/items/miner_helmet.png")
    build_helmet_armor_texture(RP / "textures/models/armor/miner_helmet_layer_1.png")
    w(RP / "models/entity/miner_helmet_armor.geo.json", build_helmet_armor_geometry())
    w(RP / "textures/item_texture.json", {
        "resource_pack_name": "neosmoremobs",
        "texture_name": "atlas.items",
        "texture_data": {
            "neosmoremobs_miner_helmet": {"textures": "textures/items/miner_helmet"},
        },
    })
    w(BP / "items/miner_helmet.json", {
        "format_version": "1.21.40",
        "minecraft:item": {
            "description": {
                "identifier": HELMET,
                "menu_category": {"category": "equipment"},
            },
            "components": {
                "minecraft:icon": {"textures": {"default": "neosmoremobs_miner_helmet"}},
                "minecraft:display_name": {"value": "item.neosmoremobs:miner_helmet.name"},
                "minecraft:max_stack_size": 1,
                "minecraft:wearable": {"slot": "slot.armor.head", "protection": 2},
                "minecraft:durability": {"max_durability": 275},
                "minecraft:enchantable": {"slot": "armor_head", "value": 10},
                "minecraft:repairable": {
                    "repair_items": [{"items": ["minecraft:iron_ingot"], "repair_amount": 90}],
                },
                "minecraft:tags": {"tags": ["minecraft:is_armor"]},
            },
        },
    })
    w(BP / "recipes/miner_helmet.json", {
        "format_version": "1.21.0",
        "minecraft:recipe_shaped": {
            "description": {"identifier": "neosmoremobs:miner_helmet"},
            "tags": ["crafting_table"],
            "pattern": ["III", "ITI"],
            "key": {
                "I": {"item": "minecraft:iron_ingot"},
                "T": {"item": "minecraft:torch"},
            },
            "unlock": [{"item": "minecraft:iron_ingot"}],
            "result": {"item": HELMET, "count": 1},
        },
    })
    w(RP / "attachables/miner_helmet.attachable.json", {
        "format_version": "1.8.0",
        "minecraft:attachable": {
            "description": {
                "identifier": HELMET,
                "materials": {"default": "armor", "enchanted": "armor_enchanted"},
                "textures": {
                    "default": "textures/models/armor/miner_helmet_layer_1",
                    "enchanted": "textures/misc/enchanted_actor_glint",
                },
                "geometry": {"default": "geometry.neosmoremobs.miner_helmet_armor"},
                "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
                "render_controllers": ["controller.render.armor"],
            },
        },
    })
    w(RP / "attachables/miner_helmet.player.attachable.json", {
        "format_version": "1.10.0",
        "minecraft:attachable": {
            "description": {
                "identifier": HELMET + ".player",
                "item": {HELMET: "query.owner_identifier == 'minecraft:player'"},
                "materials": {"default": "armor", "enchanted": "armor_enchanted"},
                "textures": {
                    "default": "textures/models/armor/miner_helmet_layer_1",
                    "enchanted": "textures/misc/enchanted_actor_glint",
                },
                "geometry": {"default": "geometry.neosmoremobs.miner_helmet_armor"},
                "scripts": {"parent_setup": "variable.helmet_layer_visible = 0.0;"},
                "render_controllers": ["controller.render.armor"],
            },
        },
    })

    # ------------------------------------------------------------- void dealer
    geo = json.loads((END / "model.geo.json").read_text())
    for g in geo["minecraft:geometry"]:
        if g["description"]["identifier"] == "geometry.void_dealer":
            g["description"]["identifier"] = "geometry.neosmoremobs.void_dealer"
    w(RP / "models/entity/void_dealer.geo.json", geo)
    shutil.copyfile(END / "texture.png", RP / "textures/entity/neosmoremobs/void_dealer.png")

    w(RP / "entity/void_dealer.entity.json", {
        "format_version": "1.10.0",
        "minecraft:client_entity": {
            "description": {
                "identifier": "neosmoremobs:void_dealer",
                "materials": {"default": "entity_alphatest"},
                "textures": {"default": "textures/entity/neosmoremobs/void_dealer"},
                "geometry": {"default": "geometry.neosmoremobs.void_dealer"},
                "animations": {
                    "look_at_target_default": "animation.humanoid.look_at_target.default",
                    "look_at_target_gliding": "animation.humanoid.look_at_target.gliding",
                    "look_at_target_swimming": "animation.humanoid.look_at_target.swimming",
                    "move": "animation.humanoid.move",
                    "attack.rotations": "animation.humanoid.attack.rotations",
                    "bob": "animation.humanoid.bob",
                    "base_pose": "animation.enderman.base_pose",
                    "arms_legs": "animation.enderman.arms_legs",
                    "carrying": "animation.enderman.carrying",
                    "scary_face": "animation.enderman.scary_face",
                    "look_at_target_controller": "controller.animation.humanoid.look_at_target",
                    "move_controller": "controller.animation.humanoid.move",
                    "attack_controller": "controller.animation.humanoid.attack",
                    "bob_controller": "controller.animation.humanoid.bob",
                    "base_pose_controller": "controller.animation.enderman.base_pose",
                    "carrying_controller": "controller.animation.enderman.carrying",
                    "scary_face_controller": "controller.animation.enderman.scary_face",
                },
                "scripts": {
                    "pre_animation": [
                        "variable.tcos0 = (Math.cos(query.modified_distance_moved * 38.17) * query.modified_move_speed / variable.gliding_speed_value) * 28.65;"
                    ],
                    "animate": [
                        "look_at_target_controller", "move_controller", "attack_controller",
                        "bob_controller", "base_pose_controller", "carrying_controller",
                        "scary_face_controller",
                    ],
                },
                "render_controllers": ["controller.render.neosmoremobs.void_dealer"],
                "spawn_egg": {"base_color": "#1B1B2A", "overlay_color": "#6C4BD6"},
            }
        },
    })
    w(RP / "render_controllers/more_mobs.render_controllers.json", {
        "format_version": "1.8.0",
        "render_controllers": {
            "controller.render.neosmoremobs.miner_zombie": {
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": ["Texture.default"],
            },
            "controller.render.neosmoremobs.void_dealer": {
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": ["Texture.default"],
            },
        },
    })

    w(BP / "entities/void_dealer.json", {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {
                "identifier": "neosmoremobs:void_dealer",
                "is_spawnable": True,
                "is_summonable": True,
                "spawn_category": "creature",
            },
            "components": {
                "minecraft:type_family": {"family": ["void_dealer", "mob"]},
                "minecraft:collision_box": {"width": 1.2, "height": 3.5},
                "minecraft:health": {"value": 40, "max": 40},
                "minecraft:physics": {},
                "minecraft:breathable": {"total_supply": 15, "suffocate_time": 0},
                "minecraft:nameable": {},
                "minecraft:persistent": {},
                "minecraft:knockback_resistance": {"value": 1.0},
                "minecraft:movement": {"value": 0.25},
                "minecraft:navigation.walk": {"can_path_over_water": True, "avoid_water": True, "avoid_damage_blocks": True},
                "minecraft:jump.static": {},
                "minecraft:behavior.float": {"priority": 0},
                "minecraft:behavior.random_stroll": {"priority": 4, "speed_multiplier": 1.0},
                "minecraft:is_hidden_when_invisible": {},
                "minecraft:conditional_bandwidth_optimization": {},
                "minecraft:behavior.look_at_player": {"priority": 1, "look_distance": 8.0, "probability": 0.5},
                "minecraft:behavior.random_look_around": {"priority": 2},
                "minecraft:loot": {"table": "loot_tables/entities/void_dealer.json"},
                "minecraft:experience_reward": {"on_death": "query.last_hit_by_player ? Math.Random(3,6) : 0"},
            },
        },
    })
    w(BP / "spawn_rules/void_dealer.json", {
        "format_version": "1.8.0",
        "minecraft:spawn_rules": {
            "description": {"identifier": "neosmoremobs:void_dealer", "population_control": "animal"},
            "conditions": [
                {
                    "minecraft:spawns_on_surface": {},
                    "minecraft:brightness_filter": {"min": 0, "max": 15, "adjust_for_weather": False},
                    "minecraft:difficulty_filter": {"min": "easy", "max": "hard"},
                    "minecraft:weight": {"default": 1},
                    "minecraft:herd": {"min_size": 1, "max_size": 1},
                    "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==", "value": "overworld"},
                },
                {
                    "minecraft:spawns_on_surface": {},
                    "minecraft:brightness_filter": {"min": 0, "max": 15, "adjust_for_weather": False},
                    "minecraft:difficulty_filter": {"min": "easy", "max": "hard"},
                    "minecraft:weight": {"default": 2},
                    "minecraft:herd": {"min_size": 1, "max_size": 1},
                    "minecraft:biome_filter": {"test": "has_biome_tag", "operator": "==", "value": "the_end"},
                },
            ],
        },
    })
    w(BP / "loot_tables/entities/void_dealer.json", {
        "pools": [
            {"rolls": 1, "entries": [{"type": "item", "name": "minecraft:ender_pearl", "weight": 1,
                                      "functions": [{"function": "set_count", "count": {"min": 0, "max": 2}}]}]},
            {"rolls": 1, "entries": [{"type": "item", "name": "minecraft:paper", "weight": 1,
                                      "functions": [{"function": "set_count", "count": {"min": 0, "max": 3}}]}]},
            {"rolls": 1, "conditions": [{"condition": "random_chance", "chance": 0.25}],
             "entries": [{"type": "item", "name": "minecraft:diamond", "weight": 1}]},
        ]
    })

    # ------------------------------------------------------------- trade script
    (BP / "scripts/void_dealer_trade.js").write_text(TRADE_JS)
    (BP / "scripts/miner_helmet_light.js").write_text(MINER_HELMET_LIGHT_JS)
    (BP / "scripts/main.js").write_text(
        'import "./raccoon_theft.js";\n'
        'import "./void_dealer_trade.js";\n'
        'import "./miner_helmet_light.js";\n')

    (STAGE / "lang.txt").write_text(
        "entity.neosmoremobs:miner_zombie.name=Miner Zombie\n"
        "item.spawn_egg.entity.neosmoremobs:miner_zombie.name=Miner Zombie Spawn Egg\n"
        "entity.neosmoremobs:void_dealer.name=Void Dealer\n"
        "item.spawn_egg.entity.neosmoremobs:void_dealer.name=Void Dealer Spawn Egg\n"
        "item.neosmoremobs:miner_helmet.name=Miner Helmet\n"
    )
    print("staged", STAGE)


TRADE_JS = r'''
import { world, system, ItemStack } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

const OFFERS = [
  { label: "16 Obsidian", cost: 1, item: "minecraft:obsidian", count: 16 },
  { label: "4 Ender Pearls", cost: 1, item: "minecraft:ender_pearl", count: 4 },
  { label: "2 Eyes of Ender", cost: 2, item: "minecraft:ender_eye", count: 2 },
  { label: "1 Ender Chest", cost: 2, item: "minecraft:ender_chest", count: 1 },
  { label: "8 Chorus Fruit", cost: 2, item: "minecraft:chorus_fruit", count: 8 },
  { label: "1 Shulker Shell", cost: 3, item: "minecraft:shulker_shell", count: 1 },
  { label: "1 Netherite Ingot", cost: 5, item: "minecraft:netherite_ingot", count: 1 },
  { label: "1 Totem of Undying", cost: 5, item: "minecraft:totem_of_undying", count: 1 },
];

function containerOf(player) {
  return player.getComponent("minecraft:inventory")?.container;
}

function countItem(container, id) {
  let total = 0;
  for (let i = 0; i < container.size; i++) {
    const item = container.getItem(i);
    if (item?.typeId === id) total += item.amount;
  }
  return total;
}

function takeItem(container, id, amount) {
  let left = amount;
  for (let i = 0; i < container.size && left > 0; i++) {
    const item = container.getItem(i);
    if (item?.typeId !== id) continue;
    const used = Math.min(left, item.amount);
    left -= used;
    if (item.amount === used) container.setItem(i);
    else container.setItem(i, new ItemStack(id, item.amount - used));
  }
  return left === 0;
}

function giveItem(player, id, amount) {
  const container = containerOf(player);
  try {
    const left = container.addItem(new ItemStack(id, amount));
    if (left) player.dimension.spawnItem(left, player.location);
  } catch {
    player.dimension.spawnItem(new ItemStack(id, amount), player.location);
  }
}

function showShop(player, tries = 0) {
  const form = new ActionFormData()
    .title("Void Dealer")
    .body("The void trades. Bring diamonds.");
  for (const offer of OFFERS) {
    form.button(`${offer.label}\n§b${offer.cost} Diamond${offer.cost > 1 ? "s" : ""}`);
  }
  form.show(player).then((res) => {
    if (res.canceled || res.selection === undefined) return;
    const offer = OFFERS[res.selection];
    const container = containerOf(player);
    if (!container || countItem(container, "minecraft:diamond") < offer.cost) {
      player.onScreenDisplay.setActionBar("§cNot enough diamonds.");
      return;
    }
    takeItem(container, "minecraft:diamond", offer.cost);
    giveItem(player, offer.item, offer.count);
    player.onScreenDisplay.setActionBar(`§5Bought ${offer.label}`);
    player.playSound("random.orb", { pitch: 0.8 });
  }).catch(() => {
    if (tries < 2) system.runTimeout(() => showShop(player, tries + 1), 20);
  });
}

world.afterEvents.playerInteractWithEntity.subscribe(({ player, target }) => {
  if (target?.typeId === "neosmoremobs:void_dealer") showShop(player);
});
'''

MINER_HELMET_LIGHT_JS = r'''
import { world, system } from "@minecraft/server";

const HELMET_ID = "neosmoremobs:miner_helmet";
const LIGHT_ID = "minecraft:light_block_15";
const SAVE_KEY = "neosmoremobs:miner_helmet_lights";
const PLAYER_INTERVAL = 5;
const MOB_EVERY = 2;
const MOB_RANGE = 40;

const lights = new Map();
let dirty = false;
let tick = 0;

function key3(loc) {
  return `${Math.floor(loc.x)},${Math.floor(loc.y)},${Math.floor(loc.z)}`;
}

function removeTracked(info) {
  try {
    const dim = world.getDimension(info.dimensionId);
    const loc = { x: info.x, y: info.y, z: info.z };
    const block = dim.getBlock(loc);
    if (block && typeof block.typeId === "string" && block.typeId.startsWith("minecraft:light_block")) {
      dim.setBlockType(loc, "minecraft:air");
    }
  } catch {
    /* chunk not loaded */
  }
}

function clearLight(key) {
  const prev = lights.get(key);
  if (!prev) return;
  removeTracked(prev);
  lights.delete(key);
  dirty = true;
}

function isDark(dimension, loc) {
  if (dimension.id !== "minecraft:overworld") return true;
  try {
    const hit = dimension.getBlockFromRay(
      { x: loc.x, y: loc.y + 1.62, z: loc.z },
      { x: 0, y: 1, z: 0 },
      { maxDistance: 320, includeLiquidBlocks: false, includePassableBlocks: false }
    );
    if (hit && hit.block && hit.block.typeId !== "minecraft:air") return true;
  } catch {
    /* unloaded chunk */
  }
  let time = 0;
  try { time = world.getTimeOfDay(); } catch {}
  return time >= 13000 && time <= 23000;
}

function placeLight(key, dimension, loc) {
  const candidates = [
    { x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) },
    { x: Math.floor(loc.x), y: Math.floor(loc.y) + 1, z: Math.floor(loc.z) },
  ];
  let target = undefined;
  for (const candidate of candidates) {
    try {
      const block = dimension.getBlock(candidate);
      if (block && block.typeId === "minecraft:air") { target = candidate; break; }
    } catch {
      return;
    }
  }
  if (!target) return;
  const prev = lights.get(key);
  if (prev && prev.dimensionId === dimension.id &&
      prev.x === target.x && prev.y === target.y && prev.z === target.z) {
    try {
      const block = dimension.getBlock(target);
      if (block && typeof block.typeId === "string" &&
          block.typeId.startsWith("minecraft:light_block")) return;
    } catch {
      return;
    }
  }
  try {
    dimension.setBlockType(target, LIGHT_ID);
  } catch {
    return;
  }
  if (prev) removeTracked(prev);
  lights.set(key, { dimensionId: dimension.id, x: target.x, y: target.y, z: target.z });
  dirty = true;
}

function persist() {
  try {
    world.setDynamicProperty(SAVE_KEY, JSON.stringify([...lights.values()]));
  } catch {}
}

function cleanupStale() {
  try {
    const raw = world.getDynamicProperty(SAVE_KEY);
    if (typeof raw === "string" && raw.length > 2) {
      for (const info of JSON.parse(raw)) removeTracked(info);
    }
    world.setDynamicProperty(SAVE_KEY, "[]");
  } catch {}
}

system.run(cleanupStale);

world.afterEvents.playerLeave.subscribe((event) => {
  try { clearLight("p:" + event.playerId); } catch {}
  persist();
});

system.runInterval(() => {
  tick++;
  const players = world.getPlayers();
  for (const player of players) {
    let wearing = false;
    try {
      const equippable = player.getComponent("minecraft:equippable");
      const helmet = equippable ? equippable.getEquipment("Head") : undefined;
      wearing = !!helmet && helmet.typeId === HELMET_ID;
    } catch {}
    if (wearing && isDark(player.dimension, player.location)) {
      placeLight("p:" + player.id, player.dimension, player.location);
    } else {
      clearLight("p:" + player.id);
    }
  }

  if (tick % MOB_EVERY === 0) {
    const seen = new Set();
    for (const player of players) {
      let mobs = [];
      try {
        mobs = player.dimension.getEntities({
          type: "neosmoremobs:miner_zombie",
          location: player.location,
          maxDistance: MOB_RANGE,
        });
      } catch {}
      for (const mob of mobs) {
        const key = "e:" + mob.id;
        if (seen.has(key)) continue;
        seen.add(key);
        try {
          if (isDark(mob.dimension, mob.location)) {
            placeLight(key, mob.dimension, mob.location);
          } else {
            clearLight(key);
          }
        } catch {}
      }
    }
    for (const key of [...lights.keys()]) {
      if (key.startsWith("e:") && !seen.has(key)) clearLight(key);
    }
  }

  if (dirty) { persist(); dirty = false; }
}, PLAYER_INTERVAL);
'''


if __name__ == "__main__":
    main()
