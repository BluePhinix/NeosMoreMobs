from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import copy
import math
import random
import shutil
import subprocess
import sys
import uuid
import zipfile

ROOT = Path("/workspace/Neo's more mobs")
WORK = ROOT / "work"
MODELS = WORK / "models"
TEXTURES = WORK / "textures"
RENDERS = WORK / "renders"
BP = ROOT / "NeosMoreMobs_BP"
RP = ROOT / "NeosMoreMobs_RP"
BB = Path("/root/work/bb-mcp")
BUN = Path("/root/.bun/bin/bun")
ROOT_STR = str(ROOT)

FACES = ("north", "east", "south", "west", "up", "down")
TEX_SIZE = 128
MARGIN = 2

def C(name, bone, start, end, role):
    return {"name": name, "bone": bone, "from": start, "to": end, "role": role}

def B(name, parent, origin):
    return {"name": name, "parent": parent, "origin": origin}

BEAR = {
    "id": "bear",
    "name": "Grizzly Bear",
    "texture": "textures/entity/neosmoremobs/bear",
    "geometry": "geometry.neosmoremobs.bear",
    "families": ["bear", "grizzly_bear", "mob"],
    "health": 30,
    "speed": 0.25,
    "collision": [1.4, 1.4],
    "damage": 6,
    "scale": 0.85,
    "egg": ["#6B4A32", "#2F2118"],
    "bones": [
        B("body", None, [0, 15, 0]),
        B("head", "body", [0, 21, -13]),
        B("ear_l", "head", [4.5, 26, -21.5]),
        B("ear_r", "head", [-4.5, 26, -21.5]),
        B("leg_front_l", "body", [5, 9, -5]),
        B("leg_front_r", "body", [-5, 9, -5]),
        B("leg_back_l", "body", [5, 9, 6]),
        B("leg_back_r", "body", [-5, 9, 6]),
        B("tail", "body", [0, 18, 14]),
    ],
    "cubes": [
        C("belly", "body", [-7, 9, -8], [7, 17, 10], "bear_body"),
        C("back", "body", [-6, 16, -8], [6, 21, 8], "bear_body"),
        C("chest", "body", [-6, 14, -13], [6, 21, -4], "bear_body"),
        C("rump", "body", [-6, 13, 7], [6, 18, 14], "bear_body"),
        C("skull", "head", [-6, 17, -25], [6, 26, -13], "bear_head"),
        C("snout", "head", [-4, 18, -29], [4, 22, -24], "bear_snout"),
        C("nose", "head", [-2, 20, -30], [2, 22, -29], "bear_nose"),
        C("ear_l_cube", "ear_l", [3, 26, -23], [6, 29, -20], "bear_ear"),
        C("ear_r_cube", "ear_r", [-6, 26, -23], [-3, 29, -20], "bear_ear"),
        C("leg_front_l_cube", "leg_front_l", [3, 0, -9], [7, 9, -2], "bear_leg"),
        C("paw_front_l", "leg_front_l", [2, 0, -10], [8, 3, -1], "bear_paw"),
        C("leg_front_r_cube", "leg_front_r", [-7, 0, -9], [-3, 9, -2], "bear_leg"),
        C("paw_front_r", "leg_front_r", [-8, 0, -10], [-2, 3, -1], "bear_paw"),
        C("leg_back_l_cube", "leg_back_l", [3, 0, 3], [7, 9, 10], "bear_leg"),
        C("haunch_l", "leg_back_l", [3, 3, 2], [8, 9, 10], "bear_leg"),
        C("paw_back_l", "leg_back_l", [2, 0, 2], [8, 3, 11], "bear_paw"),
        C("leg_back_r_cube", "leg_back_r", [-7, 0, 3], [-3, 9, 10], "bear_leg"),
        C("haunch_r", "leg_back_r", [-8, 3, 2], [-3, 9, 10], "bear_leg"),
        C("paw_back_r", "leg_back_r", [-8, 0, 2], [-2, 3, 11], "bear_paw"),
        C("tail_cube", "tail", [-2, 16, 14], [2, 21, 18], "bear_tail"),
    ],
    "loot": [("minecraft:beef", 1, 3, 3), ("minecraft:leather", 0, 2, 2)],
    "spawn": {"tag": "taiga", "weight": 3, "herd": [1, 2]},
}




TIGER = {
    "id": "tiger",
    "name": "Bengal Tiger",
    "texture": "textures/entity/neosmoremobs/tiger",
    "geometry": "geometry.neosmoremobs.tiger",
    "families": ["tiger", "mob"],
    "health": 30,
    "speed": 0.34,
    "collision": [1.2, 1.4],
    "damage": 7,
    "scale": 0.9,
    "egg": ["#C97A2B", "#211A16"],
    "bones": [
        B("body", None, [0, 13, 0]),
        B("head", "body", [0, 19, -12]),
        B("ear_l", "head", [4.5, 24, -19.5]),
        B("ear_r", "head", [-4.5, 24, -19.5]),
        B("leg_front_l", "body", [5, 8, -6]),
        B("leg_front_r", "body", [-5, 8, -6]),
        B("leg_back_l", "body", [5, 8, 6]),
        B("leg_back_r", "body", [-5, 8, 6]),
        B("tail1", "body", [0, 14, 12]),
        B("tail2", "tail1", [0, 14, 18]),
        B("tail3", "tail2", [0, 14, 24]),
    ],
    "cubes": [
        C("torso", "body", [-7, 8, -12], [7, 21, 12], "tiger_body"),
        C("chest", "body", [-6, 16, -13], [6, 21, -4], "tiger_body"),
        C("skull", "head", [-6, 15, -24], [6, 24, -13], "tiger_head"),
        C("snout", "head", [-3, 15, -27], [3, 19, -23], "tiger_snout"),
        C("nose", "head", [-1, 17, -28], [1, 19, -27], "tiger_nose"),
        C("ear_l_cube", "ear_l", [3, 24, -22], [6, 27, -19], "tiger_ear"),
        C("ear_r_cube", "ear_r", [-6, 24, -22], [-3, 27, -19], "tiger_ear"),
        C("leg_front_l_cube", "leg_front_l", [2, 0, -10], [7, 8, -3], "tiger_leg"),
        C("paw_front_l", "leg_front_l", [1, 0, -11], [7, 3, -2], "tiger_paw"),
        C("leg_front_r_cube", "leg_front_r", [-7, 0, -10], [-2, 8, -3], "tiger_leg"),
        C("paw_front_r", "leg_front_r", [-7, 0, -11], [-1, 3, -2], "tiger_paw"),
        C("leg_back_l_cube", "leg_back_l", [2, 0, 2], [7, 8, 9], "tiger_leg"),
        C("paw_back_l", "leg_back_l", [1, 0, 1], [7, 3, 10], "tiger_paw"),
        C("leg_back_r_cube", "leg_back_r", [-7, 0, 2], [-2, 8, 9], "tiger_leg"),
        C("paw_back_r", "leg_back_r", [-7, 0, 1], [-1, 3, 10], "tiger_paw"),
        C("tail1_cube", "tail1", [-1, 12, 12], [1, 16, 18], "tiger_tail"),
        C("tail2_cube", "tail2", [-1, 14, 18], [1, 17, 24], "tiger_tail"),
        C("tail3_cube", "tail3", [-1, 15, 24], [1, 17, 30], "tiger_tail_tip"),
    ],
    "loot": [("minecraft:beef", 1, 3, 3), ("minecraft:leather", 0, 2, 2)],
    "spawn": {"tag": "jungle", "weight": 2, "herd": [1, 2]},
}


MONKEY = {
    "id": "monkey",
    "name": "Capuchin Monkey",
    "texture": "textures/entity/neosmoremobs/monkey",
    "geometry": "geometry.neosmoremobs.monkey",
    "families": ["monkey", "mob"],
    "health": 14,
    "speed": 0.3,
    "collision": [0.6, 1.1],
    "damage": 0,
    "scale": 0.9,
    "egg": ["#4A3324", "#D8C3A1"],
    "bones": [
        B("body", None, [0, 12, 0]),
        B("head", "body", [0, 17, -4]),
        B("ear_l", "head", [4, 18, -6]),
        B("ear_r", "head", [-4, 18, -6]),
        B("arm_l", "body", [4.5, 15, 0]),
        B("forearm_l", "arm_l", [4.5, 8, 0]),
        B("hand_l", "forearm_l", [4.5, 3, 0]),
        B("arm_r", "body", [-4.5, 15, 0]),
        B("forearm_r", "arm_r", [-4.5, 8, 0]),
        B("hand_r", "forearm_r", [-4.5, 3, 0]),
        B("leg_l", "body", [3, 7, 0]),
        B("shin_l", "leg_l", [3, 3, 0]),
        B("foot_l", "shin_l", [3, 1, -1]),
        B("leg_r", "body", [-3, 7, 0]),
        B("shin_r", "leg_r", [-3, 3, 0]),
        B("foot_r", "shin_r", [-3, 1, -1]),
        B("tail1", "body", [0, 11, 4]),
        B("tail2", "tail1", [0, 10, 10]),
        B("tail3", "tail2", [0, 9, 16]),
        B("tail4", "tail3", [0, 8, 22]),
    ],
    "cubes": [
        C("torso", "body", [-4, 7, -4], [4, 16, 4], "monkey_body"),
        C("skull", "head", [-3, 14, -8], [3, 20, -4], "monkey_head"),
        C("muzzle", "head", [-2, 14, -10], [2, 16, -8], "monkey_muzzle"),
        C("crown", "head", [-3, 20, -7], [3, 22, -4], "monkey_head"),
        C("ear_l_cube", "ear_l", [3, 17, -7], [5, 19, -5], "monkey_ear"),
        C("ear_r_cube", "ear_r", [-5, 17, -7], [-3, 19, -5], "monkey_ear"),
        C("upperarm_l", "arm_l", [4, 8, -1], [7, 15, 2], "monkey_arm"),
        C("forearm_l_cube", "forearm_l", [4, 3, -1], [6, 8, 1], "monkey_arm"),
        C("hand_l_cube", "hand_l", [4, 1, -1], [6, 3, 2], "monkey_hand"),
        C("upperarm_r", "arm_r", [-7, 8, -1], [-4, 15, 2], "monkey_arm"),
        C("forearm_r_cube", "forearm_r", [-6, 3, -1], [-4, 8, 1], "monkey_arm"),
        C("hand_r_cube", "hand_r", [-6, 1, -1], [-4, 3, 2], "monkey_hand"),
        C("thigh_l", "leg_l", [1.5, 3, -1], [4.5, 7, 2], "monkey_leg"),
        C("shin_l_cube", "shin_l", [1.5, 1, -1], [4.5, 3, 1], "monkey_leg"),
        C("foot_l_cube", "foot_l", [1, 0, -3], [5, 1, 1], "monkey_foot"),
        C("thigh_r", "leg_r", [-4.5, 3, -1], [-1.5, 7, 2], "monkey_leg"),
        C("shin_r_cube", "shin_r", [-4.5, 1, -1], [-1.5, 3, 1], "monkey_leg"),
        C("foot_r_cube", "foot_r", [-5, 0, -3], [-1, 1, 1], "monkey_foot"),
        C("tail1_cube", "tail1", [-1, 9, 4], [1, 12, 10], "monkey_tail"),
        C("tail2_cube", "tail2", [-1, 9, 10], [1, 11, 16], "monkey_tail"),
        C("tail3_cube", "tail3", [-1, 8, 16], [1, 10, 22], "monkey_tail"),
        C("tail4_cube", "tail4", [-1, 7, 22], [1, 9, 27], "monkey_tail_tip"),
    ],
    "loot": [("minecraft:apple", 0, 1, 1)],
    "spawn": {"tag": "jungle", "weight": 6, "herd": [2, 4]},
}



PENGUIN = {
    "id": "penguin",
    "name": "Emperor Penguin",
    "texture": "textures/entity/neosmoremobs/penguin",
    "geometry": "geometry.neosmoremobs.penguin",
    "families": ["penguin", "bird", "mob"],
    "health": 10,
    "speed": 0.22,
    "collision": [0.6, 1.2],
    "damage": 0,
    "scale": 0.75,
    "egg": ["#1B2630", "#F2EFE5"],
    "bones": [
        B("body", None, [0, 12, 0]),
        B("head", "body", [0, 23, 0]),
        B("flipper_l", "body", [5, 18, 0]),
        B("flipper_r", "body", [-5, 18, 0]),
        B("foot_l", "body", [2.5, 2, 0]),
        B("foot_r", "body", [-2.5, 2, 0]),
        B("tail", "body", [0, 4, 4]),
    ],
    "cubes": [
        C("lower_body", "body", [-5, 2, -4], [5, 14, 4], "penguin_body"),
        C("upper_body", "body", [-4, 13, -3], [4, 22, 3], "penguin_body"),
        C("skull", "head", [-3, 22, -4], [3, 28, 2], "penguin_head"),
        C("beak", "head", [-1, 24, -8], [1, 26, -4], "penguin_beak"),
        C("flipper_l_cube", "flipper_l", [4, 5, -2], [6, 19, 1], "penguin_flipper"),
        C("flipper_r_cube", "flipper_r", [-6, 5, -2], [-4, 19, 1], "penguin_flipper"),
        C("foot_l_cube", "foot_l", [1, 0, -3], [4, 2, 2], "penguin_foot"),
        C("foot_r_cube", "foot_r", [-4, 0, -3], [-1, 2, 2], "penguin_foot"),
        C("tail_cube", "tail", [-2, 2, 4], [2, 4, 7], "penguin_tail"),
    ],
    "loot": [("minecraft:feather", 1, 3, 3), ("minecraft:fish", 0, 1, 1)],
    "spawn": {"tag": "frozen", "weight": 8, "herd": [2, 5]},
}



SNAKE = {
    "id": "snake",
    "name": "Emerald Snake",
    "texture": "textures/entity/neosmoremobs/snake",
    "geometry": "geometry.neosmoremobs.snake",
    "families": ["snake", "serpent", "mob"],
    "health": 8,
    "speed": 0.26,
    "collision": [1.2, 0.6],
    "damage": 3,
    "scale": 0.8,
    "egg": ["#2F5B33", "#8FBF74"],
    "bones": [
        B("body0", None, [0, 3, 8]),
        B("body1", "body0", [0, 3, 3]),
        B("body2", "body1", [0, 3, -2]),
        B("body3", "body2", [0, 3, -7]),
        B("body4", "body3", [0, 3, -12]),
        B("body5", "body4", [0, 3, -17]),
        B("body6", "body5", [0, 3, -22]),
        B("head", "body6", [0, 3, -29]),
        B("jaw", "head", [0, 2, -29]),
        B("tongue", "jaw", [0, 1.5, -38]),
        B("tail", "body0", [0, 3, 8]),
        B("tail2", "tail", [0, 3, 14]),
    ],
    "cubes": [
        C("body0_cube", "body0", [-4, 1, 1], [4, 6, 8], "snake_body"),
        C("body1_cube", "body1", [-4, 1, -4], [4, 6, 3], "snake_body"),
        C("body2_cube", "body2", [-4, 1, -9], [4, 6, -2], "snake_body"),
        C("body3_cube", "body3", [-4, 1, -14], [4, 6, -7], "snake_body"),
        C("body4_cube", "body4", [-4, 1, -19], [4, 6, -12], "snake_body"),
        C("body5_cube", "body5", [-3, 1, -24], [3, 6, -17], "snake_body"),
        C("body6_cube", "body6", [-3, 1, -29], [3, 5, -22], "snake_body"),
        C("head_cube", "head", [-5, 2, -36], [5, 8, -29], "snake_head"),
        C("snout_cube", "head", [-4, 2, -39], [4, 6, -36], "snake_head"),
        C("jaw_cube", "jaw", [-4, 1, -39], [4, 2, -29], "snake_jaw"),
        C("tongue_cube", "tongue", [-1, 1, -42], [1, 2, -39], "snake_tongue"),
        C("tail_cube", "tail", [-2, 2, 8], [2, 5, 14], "snake_tail"),
        C("tail2_cube", "tail2", [-1, 2, 14], [1, 4, 19], "snake_tail_tip"),
    ],
    "loot": [("minecraft:slime_ball", 0, 1, 1)],
    "spawn": {"tag": "swamp", "weight": 4, "herd": [1, 2]},
}



BLACK_BEAR = copy.deepcopy(BEAR)
BLACK_BEAR.update({
    "id": "blackbear",
    "name": "Black Bear",
    "texture": "textures/entity/neosmoremobs/blackbear",
    "geometry": "geometry.neosmoremobs.blackbear",
    "families": ["bear", "black_bear", "mob"],
    "health": 24,
    "speed": 0.28,
    "collision": [1.2, 1.3],
    "damage": 5,
    "scale": 0.78,
    "egg": ["#1C1A17", "#B08A63"],
    "loot": [("minecraft:beef", 1, 2, 3), ("minecraft:leather", 0, 2, 2)],
    "spawn": {"tags": ["forest", "taiga"], "weight": 4, "herd": [1, 2]},
})
BLACK_BEAR["cubes"] = [c for c in BLACK_BEAR["cubes"] if c["name"] != "back"]

LION = copy.deepcopy(TIGER)
LION.update({
    "id": "lion",
    "name": "Lion",
    "texture": "textures/entity/neosmoremobs/lion",
    "geometry": "geometry.neosmoremobs.lion",
    "families": ["lion", "mob"],
    "health": 32,
    "speed": 0.36,
    "collision": [1.3, 1.5],
    "damage": 8,
    "scale": 0.98,
    "egg": ["#D3A45C", "#6B4428"],
    "loot": [("minecraft:beef", 1, 3, 3), ("minecraft:leather", 0, 2, 2)],
    "spawn": {"tags": ["savanna"], "weight": 1, "herd": [1, 1]},
})
LION["cubes"] = LION["cubes"] + [
    C("mane_top", "head", [-7, 24, -23], [7, 27, -14], "lion_mane"),
    C("mane_l", "head", [5, 16, -23], [7, 26, -13], "lion_mane"),
    C("mane_r", "head", [-7, 16, -23], [-5, 26, -13], "lion_mane"),
    C("mane_chin", "head", [-5, 14, -23], [5, 16, -13], "lion_mane"),
    C("tail_tuft", "tail3", [-2, 13, 30], [2, 20, 34], "lion_tuft"),
]

LIONESS = copy.deepcopy(LION)
LIONESS.update({
    "id": "lioness",
    "name": "Lioness",
    "texture": "textures/entity/neosmoremobs/lioness",
    "geometry": "geometry.neosmoremobs.lioness",
    "families": ["lioness", "mob"],
    "health": 24,
    "speed": 0.38,
    "collision": [1.1, 1.3],
    "damage": 6,
    "scale": 0.9,
    "egg": ["#C99A5E", "#B98748"],
    "loot": [("minecraft:beef", 1, 2, 3), ("minecraft:leather", 0, 1, 2)],
    "no_spawn_rule": True,
})
LIONESS["cubes"] = [c for c in LION["cubes"] if not c["name"].startswith("mane_")]

CROCODILE = {
    "id": "crocodile",
    "name": "Crocodile",
    "texture": "textures/entity/neosmoremobs/crocodile",
    "geometry": "geometry.neosmoremobs.crocodile",
    "families": ["crocodile", "reptile", "mob"],
    "health": 32,
    "speed": 0.22,
    "collision": [1.4, 0.7],
    "damage": 9,
    "scale": 0.8,
    "egg": ["#3F5638", "#C9B98B"],
    "bones": [
        B("body", None, [0, 6, 0]),
        B("head", "body", [0, 6, -12]),
        B("jaw", "head", [0, 5, -12]),
        B("tail1", "body", [0, 6, 10]),
        B("tail2", "tail1", [0, 6, 17]),
        B("tail3", "tail2", [0, 6, 24]),
        B("leg_front_l", "body", [5, 3, -7]),
        B("leg_front_r", "body", [-5, 3, -7]),
        B("leg_back_l", "body", [5, 3, 6]),
        B("leg_back_r", "body", [-5, 3, 6]),
    ],
    "cubes": [
        C("torso", "body", [-7, 3, -12], [7, 9, 10], "croc_body"),
        C("back_ridge", "body", [-4, 9, -9], [4, 10, 8], "croc_ridge"),
        C("head_cube", "head", [-5, 4, -20], [5, 8, -12], "croc_head"),
        C("snout", "head", [-4, 4, -26], [4, 6, -20], "croc_snout"),
        C("jaw_cube", "jaw", [-4, 2, -26], [4, 4, -12], "croc_jaw"),
        C("tail1_cube", "tail1", [-4, 4, 10], [4, 8, 17], "croc_body"),
        C("tail1_ridge", "tail1", [-3, 8, 11], [3, 9, 17], "croc_ridge"),
        C("tail2_cube", "tail2", [-3, 4, 17], [3, 7, 24], "croc_body"),
        C("tail2_ridge", "tail2", [-2, 7, 18], [2, 8, 24], "croc_ridge"),
        C("tail3_cube", "tail3", [-2, 5, 24], [2, 7, 30], "croc_body"),
        C("leg_front_l_cube", "leg_front_l", [3, 0, -10], [7, 3, -5], "croc_leg"),
        C("leg_front_r_cube", "leg_front_r", [-7, 0, -10], [-3, 3, -5], "croc_leg"),
        C("leg_back_l_cube", "leg_back_l", [3, 0, 5], [7, 3, 10], "croc_leg"),
        C("leg_back_r_cube", "leg_back_r", [-7, 0, 5], [-3, 3, 10], "croc_leg"),
    ],
    "loot": [("minecraft:leather", 1, 3, 3), ("minecraft:fish", 0, 2, 2)],
    "spawn": {"tags": ["swamp", "mangrove_swamp"], "weight": 4, "herd": [1, 2]},
}

SHARK = {
    "id": "shark",
    "name": "Shark",
    "texture": "textures/entity/neosmoremobs/shark",
    "geometry": "geometry.neosmoremobs.shark",
    "families": ["aquatic", "shark", "mob"],
    "health": 30,
    "speed": 0.12,
    "collision": [1.2, 0.8],
    "damage": 7,
    "scale": 0.8,
    "egg": ["#5B6F78", "#E8EEF0"],
    "bones": [
        B("body", None, [0, 8, 0]),
        B("head", "body", [0, 8, -13]),
        B("jaw", "head", [0, 6, -13]),
        B("tail1", "body", [0, 8, 14]),
        B("tail2", "tail1", [0, 8, 20]),
        B("tail_fin", "tail2", [0, 8, 26]),
        B("fin_l", "body", [5, 7, -2]),
        B("fin_r", "body", [-5, 7, -2]),
    ],
    "cubes": [
        C("mid_body", "body", [-6, 3, -8], [6, 12, 8], "shark_body"),
        C("front_body", "body", [-5, 4, -13], [5, 11, -7], "shark_body"),
        C("rear_body", "body", [-4, 4, 8], [4, 11, 14], "shark_body"),
        C("head_cube", "head", [-4, 6, -19], [4, 11, -13], "shark_head"),
        C("snout", "head", [-3, 6, -23], [3, 10, -19], "shark_snout"),
        C("jaw_cube", "jaw", [-3, 4, -23], [3, 6, -13], "shark_jaw"),
        C("dorsal_fin", "body", [-1, 12, -4], [1, 18, 3], "shark_fin"),
        C("tail1_cube", "tail1", [-3, 4, 14], [3, 10, 20], "shark_body"),
        C("tail2_cube", "tail2", [-2, 5, 20], [2, 9, 26], "shark_body"),
        C("tail_upper", "tail_fin", [-1, 9, 26], [1, 18, 32], "shark_fin"),
        C("tail_lower", "tail_fin", [-1, 2, 26], [1, 9, 32], "shark_fin"),
        C("fin_l_cube", "fin_l", [5, 6, -5], [10, 8, 2], "shark_fin"),
        C("fin_r_cube", "fin_r", [-10, 6, -5], [-5, 8, 2], "shark_fin"),
    ],
    "loot": [("minecraft:fish", 1, 2, 2)],
    "spawn": {"tags": ["ocean"], "exclude": ["frozen", "cold"], "underwater": True, "weight": 2, "herd": [1, 2]},
}

DEER = {
    "id": "deer",
    "name": "Deer",
    "texture": "textures/entity/neosmoremobs/deer",
    "geometry": "geometry.neosmoremobs.deer",
    "families": ["deer", "mob"],
    "health": 14,
    "speed": 0.33,
    "collision": [0.8, 1.8],
    "damage": 0,
    "scale": 0.72,
    "egg": ["#8B5A3C", "#D9C2A3"],
    "bones": [
        B("body", None, [0, 17, 0]),
        B("neck", "body", [0, 20, -8]),
        B("head", "neck", [0, 30, -10]),
        B("ear_l", "head", [3, 35, -12]),
        B("ear_r", "head", [-3, 35, -12]),
        B("antler_l", "head", [2, 36, -12]),
        B("antler_r", "head", [-2, 36, -12]),
        B("tail", "body", [0, 17, 8]),
        B("leg_front_l", "body", [3, 10, -5]),
        B("leg_front_r", "body", [-3, 10, -5]),
        B("leg_back_l", "body", [3, 10, 5]),
        B("leg_back_r", "body", [-3, 10, 5]),
    ],
    "cubes": [
        C("torso", "body", [-5, 10, -8], [5, 20, 8], "deer_body"),
        C("chest", "body", [-4, 13, -10], [4, 20, -4], "deer_body"),
        C("neck_cube", "neck", [-2, 20, -12], [2, 30, -8], "deer_neck"),
        C("skull", "head", [-3, 30, -14], [3, 36, -8], "deer_head"),
        C("snout", "head", [-2, 31, -17], [2, 34, -14], "deer_snout"),
        C("ear_l_cube", "ear_l", [3, 35, -13], [5, 37, -10], "deer_ear"),
        C("ear_r_cube", "ear_r", [-5, 35, -13], [-3, 37, -10], "deer_ear"),
        C("antler_l_main", "antler_l", [2, 36, -13], [4, 42, -11], "deer_antler"),
        C("antler_l_branch", "antler_l", [3, 39, -12], [6, 41, -10], "deer_antler"),
        C("antler_r_main", "antler_r", [-4, 36, -13], [-2, 42, -11], "deer_antler"),
        C("antler_r_branch", "antler_r", [-6, 39, -12], [-3, 41, -10], "deer_antler"),
        C("tail_cube", "tail", [0, 16, 8], [2, 20, 11], "deer_tail"),
        C("leg_front_l_cube", "leg_front_l", [2, 0, -7], [4, 10, -4], "deer_leg"),
        C("leg_front_r_cube", "leg_front_r", [-4, 0, -7], [-2, 10, -4], "deer_leg"),
        C("leg_back_l_cube", "leg_back_l", [2, 0, 4], [4, 10, 7], "deer_leg"),
        C("leg_back_r_cube", "leg_back_r", [-4, 0, 4], [-2, 10, 7], "deer_leg"),
    ],
    "loot": [("minecraft:leather", 0, 2, 2), ("minecraft:mutton", 1, 2, 3)],
    "spawn": {"tags": ["forest", "meadow"], "weight": 8, "herd": [2, 4]},
}

ELEPHANT = {
    "id": "elephant",
    "name": "Elephant",
    "texture": "textures/entity/neosmoremobs/elephant",
    "geometry": "geometry.neosmoremobs.elephant",
    "families": ["elephant", "mob"],
    "health": 60,
    "speed": 0.18,
    "collision": [2.4, 2.4],
    "damage": 10,
    "scale": 0.7,
    "egg": ["#6E6A63", "#D6C9AE"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:leather", 3, 6, 4)],
    "spawn": {"tags": ["savanna"], "weight": 1, "herd": [1, 2]},
    "import": {"gltf": "work/imported_elephant/source/model.gltf", "texture": "work/imported_elephant/textures/gltf_embedded_0.png", "rig": "elephant"},
}

BEAR["import"] = {"gltf": "work/imported_bear/source/model.gltf", "texture": "work/imported_bear/textures/gltf_embedded_0.png", "rig": "bear"}
BEAR["scale"] = 1.15
BLACK_BEAR["import"] = {"gltf": "work/imported_bear/source/model.gltf", "texture": "work/imported_bear/textures/gltf_embedded_0.png", "rig": "bear", "recolor": "black"}
BLACK_BEAR["scale"] = 1.0

DEER["import"] = {"gltf": "work/imported_deer2/source/model.gltf", "texture": "work/imported_deer2/textures/gltf_embedded_0.png", "rig": "hierarchy", "unit_scale": 16, "root_bone": "bodyb"}
DEER["scale"] = 0.95

SCORPION = {
    "id": "scorpion",
    "name": "Scorpion Girl",
    "texture": "textures/entity/neosmoremobs/scorpion",
    "geometry": "geometry.neosmoremobs.scorpion",
    "families": ["scorpion_girl", "scorpion", "mob"],
    "health": 30,
    "speed": 0.3,
    "collision": [0.9, 1.9],
    "damage": 6,
    "scale": 0.9,
    "egg": ["#6B4E3A", "#3E6A4E"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:spider_eye", 0, 1, 2), ("minecraft:string", 0, 2, 1)],
    "spawn_category": "monster",
    "spawn": {"tags": ["desert", "mesa"], "weight": 2, "herd": [1, 2], "population_control": "monster", "brightness": {"min": 0, "max": 7, "adjust_for_weather": False}},
    "import": {"gltf": "work/imported_scorpion/source/model.gltf", "texture": "work/imported_scorpion/textures/gltf_embedded_0.png", "rig": "hierarchy", "unit_scale": 1, "synthetic_root": "root"},
}

WHALE = {
    "id": "whale",
    "name": "Whale",
    "texture": "textures/entity/neosmoremobs/whale",
    "geometry": "geometry.neosmoremobs.whale",
    "families": ["aquatic", "whale", "mob"],
    "health": 60,
    "speed": 0.12,
    "collision": [2.0, 1.0],
    "damage": 0,
    "scale": 0.45,
    "egg": ["#4B5D6B", "#D6E0E4"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:fish", 2, 4, 3)],
    "spawn": {"tags": ["ocean"], "underwater": True, "weight": 1, "herd": [1, 2], "population_control": "water_animal"},
    "import": {"gltf": "work/imported_whale/source/model.gltf", "texture": "work/imported_whale/textures/gltf_embedded_0.png", "rig": "hierarchy", "unit_scale": 16, "root_bone": "Body"},
}

JELLY = {
    "id": "jelly",
    "name": "Blue Comb Jelly",
    "texture": "textures/entity/neosmoremobs/jelly",
    "geometry": "geometry.neosmoremobs.jelly",
    "families": ["aquatic", "jelly", "mob"],
    "health": 8,
    "speed": 0.08,
    "collision": [0.6, 0.6],
    "damage": 0,
    "scale": 0.6,
    "egg": ["#3F9DD8", "#B7F0FF"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:glow_ink_sac", 0, 1, 1)],
    "spawn": {"tags": ["ocean"], "underwater": True, "weight": 4, "herd": [1, 3], "population_control": "water_animal"},
    "import": {"gltf": "work/imported_jelly/source/model.gltf", "texture": "work/imported_jelly/textures/gltf_embedded_0.png", "rig": "single", "unit_scale": 16},
}

BISON = {
    "id": "bison",
    "name": "Bison",
    "texture": "textures/entity/neosmoremobs/bison",
    "geometry": "geometry.neosmoremobs.bison",
    "families": ["bison", "mob"],
    "health": 40,
    "speed": 0.25,
    "collision": [1.6, 1.8],
    "damage": 7,
    "scale": 0.65,
    "egg": ["#3A2A1D", "#C7A86E"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:beef", 1, 3, 3), ("minecraft:leather", 1, 3, 2)],
    "spawn": {"tags": ["plains", "savanna"], "weight": 3, "herd": [2, 4]},
    "import": {"gltf": "work/imported_bison/source/model.gltf", "texture": "work/imported_bison/textures/gltf_embedded_0.png", "rig": "bison"},
}

GIRAFFE = {
    "id": "giraffe",
    "name": "Giraffe",
    "texture": "textures/entity/neosmoremobs/giraffe",
    "geometry": "geometry.neosmoremobs.giraffe",
    "texture_size": 256,
    "families": ["giraffe", "mob"],
    "health": 30,
    "speed": 0.3,
    "collision": [1.4, 4.7],
    "damage": 0,
    "scale": 0.7,
    "egg": ["#D8B04A", "#8B5A2B"],
    "bones": [
        B("body", None, [0, 40, 0]),
        B("neck1", "body", [0, 54, -8]),
        B("neck2", "neck1", [0, 70, -8]),
        B("neck3", "neck2", [0, 84, -7]),
        B("head", "neck3", [0, 92, -7]),
        B("ear_l", "head", [4, 99, -9]),
        B("ear_r", "head", [-4, 99, -9]),
        B("ossicone_l", "head", [2, 100, -9]),
        B("ossicone_r", "head", [-2, 100, -9]),
        B("tail1", "body", [0, 53, 12]),
        B("tail2", "tail1", [0, 49, 18]),
        B("leg_front_l", "body", [6, 26, -6]),
        B("leg_front_r", "body", [-6, 26, -6]),
        B("leg_back_l", "body", [6, 26, 6]),
        B("leg_back_r", "body", [-6, 26, 6]),
    ],
    "cubes": [
        C("torso", "body", [-9, 26, -12], [9, 54, 12], "giraffe_body"),
        C("chest", "body", [-7, 32, -14], [7, 54, -6], "giraffe_body"),
        C("rump", "body", [-7, 30, 8], [7, 50, 13], "giraffe_body"),
        C("neck1_cube", "neck1", [-3, 54, -11], [3, 70, -5], "giraffe_body"),
        C("neck1_mane", "neck1", [-1, 54, -5], [1, 70, -4], "giraffe_mane"),
        C("neck2_cube", "neck2", [-2, 70, -11], [2, 84, -5], "giraffe_body"),
        C("neck2_mane", "neck2", [-1, 70, -5], [1, 84, -4], "giraffe_mane"),
        C("neck3_cube", "neck3", [-2, 84, -10], [2, 94, -4], "giraffe_body"),
        C("neck3_mane", "neck3", [-1, 84, -4], [1, 94, -3], "giraffe_mane"),
        C("skull", "head", [-4, 92, -14], [4, 100, -6], "giraffe_head"),
        C("snout", "head", [-3, 93, -18], [3, 97, -14], "giraffe_snout"),
        C("nose", "head", [-2, 94, -19], [2, 97, -18], "giraffe_nose"),
        C("ear_l_cube", "ear_l", [3, 99, -10], [5, 102, -8], "giraffe_ear"),
        C("ear_r_cube", "ear_r", [-5, 99, -10], [-3, 102, -8], "giraffe_ear"),
        C("ossicone_l_cube", "ossicone_l", [1, 100, -10], [3, 108, -8], "giraffe_ossicone"),
        C("ossicone_r_cube", "ossicone_r", [-3, 100, -10], [-1, 108, -8], "giraffe_ossicone"),
        C("tail1_cube", "tail1", [-1, 50, 12], [1, 56, 18], "giraffe_tail"),
        C("tail2_cube", "tail2", [-1, 46, 18], [1, 52, 22], "giraffe_tail_tip"),
        C("leg_front_l_cube", "leg_front_l", [4, 0, -9], [8, 26, -3], "giraffe_leg"),
        C("leg_front_r_cube", "leg_front_r", [-8, 0, -9], [-4, 26, -3], "giraffe_leg"),
        C("leg_back_l_cube", "leg_back_l", [4, 0, 3], [8, 26, 9], "giraffe_leg"),
        C("leg_back_r_cube", "leg_back_r", [-8, 0, 3], [-4, 26, 9], "giraffe_leg"),
    ],
    "loot": [("minecraft:leather", 1, 3, 3)],
    "spawn": {"tags": ["savanna"], "weight": 3, "herd": [1, 2]},
}

RACCOON = {
    "id": "raccoon",
    "name": "Raccoon",
    "texture": "textures/entity/neosmoremobs/raccoon",
    "geometry": "geometry.neosmoremobs.raccoon",
    "texture_size": 256,
    "families": ["raccoon", "mob"],
    "health": 10,
    "speed": 0.32,
    "collision": [0.7, 0.9],
    "damage": 0,
    "scale": 0.7,
    "egg": ["#7D807B", "#2B2C2B"],
    "bones": [
        B("body", None, [0, 8, 0]),
        B("head", "body", [0, 12, -6]),
        B("ear_l", "head", [2, 18, -9]),
        B("ear_r", "head", [-2, 18, -9]),
        B("leg_front_l", "body", [3, 5, -4]),
        B("leg_front_r", "body", [-3, 5, -4]),
        B("leg_back_l", "body", [3, 5, 4]),
        B("leg_back_r", "body", [-3, 5, 4]),
        B("tail1", "body", [0, 9, 6]),
        B("tail2", "tail1", [0, 10, 10]),
        B("tail3", "tail2", [0, 11, 14]),
        B("tail4", "tail3", [0, 12, 18]),
    ],
    "cubes": [
        C("torso", "body", [-4, 5, -6], [4, 12, 6], "raccoon_body"),
        C("chest_fur", "body", [-3, 8, -9], [3, 12, -5], "raccoon_body"),
        C("rump_fur", "body", [-3, 6, 5], [3, 11, 8], "raccoon_body"),
        C("skull", "head", [-3, 11, -11], [3, 18, -5], "raccoon_head"),
        C("cheek_l", "head", [-4, 12, -11], [-3, 15, -8], "raccoon_cheek"),
        C("cheek_r", "head", [3, 12, -11], [4, 15, -8], "raccoon_cheek"),
        C("snout", "head", [-1, 12, -14], [1, 15, -11], "raccoon_snout"),
        C("nose", "head", [-1, 13, -15], [1, 15, -14], "raccoon_nose"),
        C("ear_l_cube", "ear_l", [2, 18, -9], [4, 21, -7], "raccoon_ear"),
        C("ear_r_cube", "ear_r", [-4, 18, -9], [-2, 21, -7], "raccoon_ear"),
        C("leg_front_l_cube", "leg_front_l", [2, 0, -6], [5, 5, -3], "raccoon_leg"),
        C("paw_front_l", "leg_front_l", [1, 0, -7], [5, 2, -2], "raccoon_paw"),
        C("leg_front_r_cube", "leg_front_r", [-5, 0, -6], [-2, 5, -3], "raccoon_leg"),
        C("paw_front_r", "leg_front_r", [-5, 0, -7], [-1, 2, -2], "raccoon_paw"),
        C("leg_back_l_cube", "leg_back_l", [2, 0, 3], [5, 5, 6], "raccoon_leg"),
        C("paw_back_l", "leg_back_l", [1, 0, 2], [5, 2, 7], "raccoon_paw"),
        C("leg_back_r_cube", "leg_back_r", [-5, 0, 3], [-2, 5, 6], "raccoon_leg"),
        C("paw_back_r", "leg_back_r", [-5, 0, 2], [-1, 2, 7], "raccoon_paw"),
        C("tail1_cube", "tail1", [-2, 7, 6], [2, 11, 10], "raccoon_tail"),
        C("tail2_cube", "tail2", [-2, 8, 10], [2, 12, 14], "raccoon_tail"),
        C("tail3_cube", "tail3", [-2, 9, 14], [2, 13, 18], "raccoon_tail"),
        C("tail4_cube", "tail4", [-1, 10, 18], [1, 14, 22], "raccoon_tail_tip"),
    ],
    "loot": [("minecraft:leather", 0, 1, 1)],
    "spawn": {"tags": ["forest", "swamp"], "weight": 5, "herd": [1, 2]},
}

PLATYPUS = {
    "id": "platypus",
    "name": "Platypus",
    "texture": "textures/entity/neosmoremobs/platypus",
    "geometry": "geometry.neosmoremobs.platypus",
    "families": ["platypus", "mob"],
    "health": 10,
    "speed": 0.22,
    "collision": [0.7, 0.5],
    "damage": 0,
    "scale": 0.7,
    "egg": ["#6B4A32", "#C9A56B"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:fish", 0, 1, 1)],
    "spawn": {"tags": ["river", "swamp"], "weight": 4, "herd": [1, 2]},
    "import": {"gltf": "work/imported_australia/source/model.gltf", "texture": "work/imported_australia/source/image_0.png", "rig": "hierarchy", "unit_scale": 16, "root_bone": "platpyus", "rebase_root": True},
}

KANGAROO = {
    "id": "kangaroo",
    "name": "Kangaroo",
    "texture": "textures/entity/neosmoremobs/kangaroo",
    "geometry": "geometry.neosmoremobs.kangaroo",
    "families": ["kangaroo", "mob"],
    "health": 20,
    "speed": 0.34,
    "collision": [0.9, 1.4],
    "damage": 0,
    "scale": 1.0,
    "egg": ["#A87345", "#D6B37A"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:leather", 0, 1, 1)],
    "spawn": {"tags": ["savanna", "plains"], "weight": 4, "herd": [2, 3]},
    "import": {"gltf": "work/imported_australia/source/model.gltf", "texture": "work/imported_australia/source/image_1.png", "rig": "hierarchy", "unit_scale": 16, "root_bone": "kangaroo", "rebase_root": True},
}

EMU = {
    "id": "emu",
    "name": "Emu",
    "texture": "textures/entity/neosmoremobs/emu",
    "geometry": "geometry.neosmoremobs.emu",
    "families": ["emu", "bird", "mob"],
    "health": 16,
    "speed": 0.35,
    "collision": [0.7, 1.7],
    "damage": 0,
    "scale": 0.75,
    "egg": ["#4A3B2E", "#B8945C"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:feather", 1, 3, 3)],
    "spawn": {"tags": ["savanna", "plains"], "weight": 4, "herd": [1, 3]},
    "import": {"gltf": "work/imported_australia/source/model.gltf", "texture": "work/imported_australia/source/image_2.png", "rig": "hierarchy", "unit_scale": 16, "root_bone": "Emu", "rebase_root": True},
}

SPIDER = {
    "id": "spider",
    "name": "Australian Spider",
    "texture": "textures/entity/neosmoremobs/spider",
    "geometry": "geometry.neosmoremobs.spider",
    "families": ["spider", "arthropod", "mob"],
    "health": 16,
    "speed": 0.3,
    "collision": [1.4, 0.6],
    "damage": 3,
    "scale": 0.55,
    "egg": ["#3B2C23", "#8A6B3F"],
    "bones": [],
    "cubes": [],
    "loot": [("minecraft:string", 0, 2, 2)],
    "spawn_category": "monster",
    "spawn": {"tags": ["desert", "mesa"], "weight": 3, "herd": [1, 2], "population_control": "monster", "brightness": {"min": 0, "max": 7, "adjust_for_weather": False}},
    "import": {"gltf": "work/imported_australia/source/model.gltf", "texture": "work/imported_australia/source/image_3.png", "rig": "hierarchy", "unit_scale": 16, "root_bone": "spider", "rebase_root": True},
}

MOBS = [BEAR, TIGER, MONKEY, PENGUIN, SNAKE, BLACK_BEAR, CROCODILE, SHARK, DEER, LION, LIONESS, ELEPHANT, BISON, SCORPION, WHALE, JELLY, GIRAFFE, RACCOON, PLATYPUS, KANGAROO, EMU, SPIDER]
MOB_BY_ID = {m["id"]: m for m in MOBS}

def clip(length, loop, bones):
    return {"length": length, "loop": loop, "bones": bones}

def rot(**kwargs):
    return kwargs

def make_clips():
    BEAR["clips"] = {
        "idle": clip(4.0, True, {
            "body": {"position": {"0": [0, 0, 0], "1": [0, 0.35, 0], "2": [0, 0.1, 0], "3": [0, 0.3, 0], "4": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "1": [1, 4, 1], "2": [0, -4, -1], "3": [2, 2, 0], "4": [0, 0, 0]}},
            "ear_l": {"rotation": {"0": [0, 0, 0], "2": [0, 0, 8], "2.25": [0, 0, 0], "4": [0, 0, 0]}},
            "ear_r": {"rotation": {"0": [0, 0, 0], "3": [0, 0, -8], "3.25": [0, 0, 0], "4": [0, 0, 0]}},
            "tail": {"rotation": {"0": [0, 0, 0], "2": [0, 8, 0], "4": [0, 0, 0]}},
        }),
        "walk": clip(1.2, True, {
            "body": {"position": {"0": [0, 1.35, 0], "0.3": [0, 1.9, 0], "0.6": [0, 1.35, 0], "0.9": [0, 1.9, 0], "1.2": [0, 1.35, 0]}},
            "leg_front_l": {"rotation": {"0": [26, 0, 0], "0.6": [-26, 0, 0], "1.2": [26, 0, 0]}},
            "leg_front_r": {"rotation": {"0": [-26, 0, 0], "0.6": [26, 0, 0], "1.2": [-26, 0, 0]}},
            "leg_back_l": {"rotation": {"0": [-26, 0, 0], "0.6": [26, 0, 0], "1.2": [-26, 0, 0]}},
            "leg_back_r": {"rotation": {"0": [26, 0, 0], "0.6": [-26, 0, 0], "1.2": [26, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.3": [2, 2, 0], "0.6": [0, 0, 0], "0.9": [-2, -2, 0], "1.2": [0, 0, 0]}},
            "tail": {"rotation": {"0": [0, -6, 0], "0.6": [0, 6, 0], "1.2": [0, -6, 0]}},
        }),
        "run": clip(0.65, True, {
            "body": {"position": {"0": [0, 1.2, 0], "0.16": [0, 2.0, 0], "0.32": [0, 1.3, 0], "0.48": [0, 2.0, 0], "0.65": [0, 1.2, 0]}},
            "leg_front_l": {"rotation": {"0": [44, 0, 0], "0.32": [-44, 0, 0], "0.65": [44, 0, 0]}},
            "leg_front_r": {"rotation": {"0": [-44, 0, 0], "0.32": [44, 0, 0], "0.65": [-44, 0, 0]}},
            "leg_back_l": {"rotation": {"0": [-40, 0, 0], "0.32": [40, 0, 0], "0.65": [-40, 0, 0]}},
            "leg_back_r": {"rotation": {"0": [40, 0, 0], "0.32": [-40, 0, 0], "0.65": [40, 0, 0]}},
            "head": {"rotation": {"0": [3, 0, 0], "0.32": [-2, 0, 0], "0.65": [3, 0, 0]}},
            "tail": {"rotation": {"0": [0, -10, 0], "0.32": [0, 10, 0], "0.65": [0, -10, 0]}},
        }),
        "attack": clip(0.9, False, {
            "body": {"position": {"0": [0, 0.5, 0], "0.28": [0, 1.5, -1.5], "0.5": [0, 0.9, -2.4], "0.9": [0, 0.5, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.28": [-18, 6, 0], "0.5": [8, -4, 0], "0.9": [0, 0, 0]}},
            "leg_front_l": {"rotation": {"0": [0, 0, 0], "0.28": [-55, 0, 0], "0.5": [-10, 0, 0], "0.9": [0, 0, 0]}},
            "leg_front_r": {"rotation": {"0": [0, 0, 0], "0.28": [-20, 0, 0], "0.5": [5, 0, 0], "0.9": [0, 0, 0]}},
            "tail": {"rotation": {"0": [0, 0, 0], "0.3": [0, 12, 0], "0.9": [0, 0, 0]}},
        }),
    }

    TIGER["clips"] = {
        "idle": clip(3.5, True, {
            "body": {"position": {"0": [0, 0, 0], "0.9": [0, 0.3, 0], "1.8": [0, 0, 0], "2.7": [0, 0.25, 0], "3.5": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.8": [1, 7, 1], "1.8": [0, -3, 0], "2.8": [2, -7, -1], "3.5": [0, 0, 0]}},
            "ear_l": {"rotation": {"0": [0, 0, 0], "1.4": [0, 0, 7], "1.65": [0, 0, 0], "3.5": [0, 0, 0]}},
            "ear_r": {"rotation": {"0": [0, 0, 0], "2.8": [0, 0, -7], "3.05": [0, 0, 0], "3.5": [0, 0, 0]}},
            "tail1": {"rotation": {"0": [0, -8, 0], "0.9": [0, 8, 0], "1.8": [0, -8, 0], "2.7": [0, 8, 0], "3.5": [0, -8, 0]}},
            "tail2": {"rotation": {"0": [0, 6, 0], "0.9": [0, -10, 0], "1.8": [0, 6, 0], "2.7": [0, -10, 0], "3.5": [0, 6, 0]}},
            "tail3": {"rotation": {"0": [0, 8, 0], "0.9": [0, -12, 0], "1.8": [0, 8, 0], "2.7": [0, -12, 0], "3.5": [0, 8, 0]}},
        }),
        "walk": clip(1.0, True, {
            "body": {"position": {"0": [0, 1.5, 0], "0.25": [0, 1.95, 0], "0.5": [0, 1.5, 0], "0.75": [0, 1.95, 0], "1.0": [0, 1.5, 0]}},
            "leg_front_l": {"rotation": {"0": [30, 0, 0], "0.5": [-30, 0, 0], "1.0": [30, 0, 0]}},
            "leg_front_r": {"rotation": {"0": [-30, 0, 0], "0.5": [30, 0, 0], "1.0": [-30, 0, 0]}},
            "leg_back_l": {"rotation": {"0": [-30, 0, 0], "0.5": [30, 0, 0], "1.0": [-30, 0, 0]}},
            "leg_back_r": {"rotation": {"0": [30, 0, 0], "0.5": [-30, 0, 0], "1.0": [30, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.25": [1, 2, 0], "0.5": [0, 0, 0], "0.75": [-1, -2, 0], "1.0": [0, 0, 0]}},
            "tail1": {"rotation": {"0": [0, 10, 0], "0.5": [0, -10, 0], "1.0": [0, 10, 0]}},
            "tail2": {"rotation": {"0": [0, -12, 0], "0.5": [0, 12, 0], "1.0": [0, -12, 0]}},
            "tail3": {"rotation": {"0": [0, 14, 0], "0.5": [0, -14, 0], "1.0": [0, 14, 0]}},
        }),
        "run": clip(0.6, True, {
            "body": {"position": {"0": [0, 1.4, 0], "0.15": [0, 2.3, 0], "0.3": [0, 1.45, 0], "0.45": [0, 2.3, 0], "0.6": [0, 1.4, 0]}},
            "leg_front_l": {"rotation": {"0": [50, 0, 0], "0.3": [-50, 0, 0], "0.6": [50, 0, 0]}},
            "leg_front_r": {"rotation": {"0": [-50, 0, 0], "0.3": [50, 0, 0], "0.6": [-50, 0, 0]}},
            "leg_back_l": {"rotation": {"0": [-45, 0, 0], "0.3": [45, 0, 0], "0.6": [-45, 0, 0]}},
            "leg_back_r": {"rotation": {"0": [45, 0, 0], "0.3": [-45, 0, 0], "0.6": [45, 0, 0]}},
            "head": {"rotation": {"0": [4, 0, 0], "0.3": [-3, 0, 0], "0.6": [4, 0, 0]}},
            "tail1": {"rotation": {"0": [0, 16, 0], "0.3": [0, -16, 0], "0.6": [0, 16, 0]}},
            "tail2": {"rotation": {"0": [0, -18, 0], "0.3": [0, 18, 0], "0.6": [0, -18, 0]}},
            "tail3": {"rotation": {"0": [0, 20, 0], "0.3": [0, -20, 0], "0.6": [0, 20, 0]}},
        }),
        "attack": clip(0.8, False, {
            "body": {"position": {"0": [0, 0, 0], "0.22": [0, 3.0, -3.0], "0.45": [0, 2.2, -4.0], "0.8": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.22": [-15, 5, 0], "0.45": [7, -4, 0], "0.8": [0, 0, 0]}},
            "leg_front_l": {"rotation": {"0": [0, 0, 0], "0.22": [-70, 0, 0], "0.45": [-35, 0, 0], "0.8": [0, 0, 0]}},
            "leg_front_r": {"rotation": {"0": [0, 0, 0], "0.22": [-70, 0, 0], "0.45": [-35, 0, 0], "0.8": [0, 0, 0]}},
            "leg_back_l": {"rotation": {"0": [0, 0, 0], "0.22": [35, 0, 0], "0.45": [15, 0, 0], "0.8": [0, 0, 0]}},
            "leg_back_r": {"rotation": {"0": [0, 0, 0], "0.22": [35, 0, 0], "0.45": [15, 0, 0], "0.8": [0, 0, 0]}},
            "tail1": {"rotation": {"0": [0, 0, 0], "0.22": [-16, 0, 0], "0.8": [0, 0, 0]}},
        }),
    }

    MONKEY["clips"] = {
        "idle": clip(4.0, True, {
            "body": {"position": {"0": [0, 0, 0], "1": [0, 0.25, 0], "2": [0, 0, 0], "3": [0, 0.25, 0], "4": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.9": [2, 8, 1], "1.8": [0, -5, 0], "2.8": [1, -9, -1], "4": [0, 0, 0]}},
            "ear_l": {"rotation": {"0": [0, 0, 0], "1.8": [0, 0, 10], "2.05": [0, 0, 0], "4": [0, 0, 0]}},
            "ear_r": {"rotation": {"0": [0, 0, 0], "3.2": [0, 0, -10], "3.45": [0, 0, 0], "4": [0, 0, 0]}},
            "arm_l": {"rotation": {"0": [0, 0, 0], "2": [3, 0, -3], "4": [0, 0, 0]}},
            "arm_r": {"rotation": {"0": [0, 0, 0], "2": [3, 0, 3], "4": [0, 0, 0]}},
            "tail1": {"rotation": {"0": [0, 0, 0], "1": [0, 8, 3], "2": [0, 0, 0], "3": [0, -8, -3], "4": [0, 0, 0]}},
            "tail2": {"rotation": {"0": [0, 0, 0], "1": [0, -12, 8], "2": [0, 0, 0], "3": [0, 12, -8], "4": [0, 0, 0]}},
            "tail3": {"rotation": {"0": [0, 0, 0], "1": [0, 15, 12], "2": [0, 0, 0], "3": [0, -15, -12], "4": [0, 0, 0]}},
        }),
        "walk": clip(0.9, True, {
            "body": {"position": {"0": [0, 0.8, 0], "0.225": [0, 1.15, 0], "0.45": [0, 0.8, 0], "0.675": [0, 1.15, 0], "0.9": [0, 0.8, 0]}},
            "leg_l": {"rotation": {"0": [28, 0, 0], "0.45": [-28, 0, 0], "0.9": [28, 0, 0]}},
            "leg_r": {"rotation": {"0": [-28, 0, 0], "0.45": [28, 0, 0], "0.9": [-28, 0, 0]}},
            "shin_l": {"rotation": {"0": [-10, 0, 0], "0.225": [12, 0, 0], "0.45": [-10, 0, 0], "0.9": [-10, 0, 0]}},
            "shin_r": {"rotation": {"0": [12, 0, 0], "0.225": [-10, 0, 0], "0.45": [12, 0, 0], "0.9": [12, 0, 0]}},
            "arm_l": {"rotation": {"0": [-24, 0, 0], "0.45": [24, 0, 0], "0.9": [-24, 0, 0]}},
            "arm_r": {"rotation": {"0": [24, 0, 0], "0.45": [-24, 0, 0], "0.9": [24, 0, 0]}},
            "forearm_l": {"rotation": {"0": [8, 0, 0], "0.45": [-10, 0, 0], "0.9": [8, 0, 0]}},
            "forearm_r": {"rotation": {"0": [-10, 0, 0], "0.45": [8, 0, 0], "0.9": [-10, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.225": [1, 3, 0], "0.45": [0, 0, 0], "0.675": [-1, -3, 0], "0.9": [0, 0, 0]}},
            "tail1": {"rotation": {"0": [0, 8, 0], "0.45": [0, -8, 0], "0.9": [0, 8, 0]}},
            "tail2": {"rotation": {"0": [0, -10, 0], "0.45": [0, 10, 0], "0.9": [0, -10, 0]}},
            "tail3": {"rotation": {"0": [0, 12, 0], "0.45": [0, -12, 0], "0.9": [0, 12, 0]}},
        }),
        "run": clip(0.55, True, {
            "body": {"position": {"0": [0, 0, 0], "0.14": [0, 0.7, 0], "0.28": [0, 0.1, 0], "0.41": [0, 0.7, 0], "0.55": [0, 0, 0]}},
            "leg_l": {"rotation": {"0": [44, 0, 0], "0.28": [-44, 0, 0], "0.55": [44, 0, 0]}},
            "leg_r": {"rotation": {"0": [-44, 0, 0], "0.28": [44, 0, 0], "0.55": [-44, 0, 0]}},
            "shin_l": {"rotation": {"0": [-20, 0, 0], "0.28": [20, 0, 0], "0.55": [-20, 0, 0]}},
            "shin_r": {"rotation": {"0": [20, 0, 0], "0.28": [-20, 0, 0], "0.55": [20, 0, 0]}},
            "arm_l": {"rotation": {"0": [-48, 0, 0], "0.28": [48, 0, 0], "0.55": [-48, 0, 0]}},
            "arm_r": {"rotation": {"0": [48, 0, 0], "0.28": [-48, 0, 0], "0.55": [48, 0, 0]}},
            "forearm_l": {"rotation": {"0": [-30, 0, 0], "0.55": [-30, 0, 0]}},
            "forearm_r": {"rotation": {"0": [-30, 0, 0], "0.55": [-30, 0, 0]}},
            "head": {"rotation": {"0": [3, 0, 0], "0.28": [-2, 0, 0], "0.55": [3, 0, 0]}},
            "tail1": {"rotation": {"0": [0, 12, 8], "0.28": [0, -12, 8], "0.55": [0, 12, 8]}},
            "tail2": {"rotation": {"0": [0, -15, 10], "0.28": [0, 15, 10], "0.55": [0, -15, 10]}},
            "tail3": {"rotation": {"0": [0, 18, 12], "0.28": [0, -18, 12], "0.55": [0, 18, 12]}},
        }),
        "attack": clip(0.75, False, {
            "body": {"position": {"0": [0, 0, 0], "0.25": [0, 0.6, -1.0], "0.5": [0, 0.2, -1.5], "0.75": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.25": [-8, 8, 0], "0.5": [5, -6, 0], "0.75": [0, 0, 0]}},
            "arm_l": {"rotation": {"0": [0, 0, 0], "0.25": [-118, 0, -12], "0.5": [-18, 0, 8], "0.75": [0, 0, 0]}},
            "forearm_l": {"rotation": {"0": [0, 0, 0], "0.25": [-80, 0, 0], "0.5": [-8, 0, 0], "0.75": [0, 0, 0]}},
            "arm_r": {"rotation": {"0": [0, 0, 0], "0.3": [-95, 0, 10], "0.55": [-12, 0, -5], "0.75": [0, 0, 0]}},
            "forearm_r": {"rotation": {"0": [0, 0, 0], "0.3": [-70, 0, 0], "0.55": [-5, 0, 0], "0.75": [0, 0, 0]}},
            "tail1": {"rotation": {"0": [0, 0, 0], "0.25": [0, -20, 10], "0.75": [0, 0, 0]}},
            "tail2": {"rotation": {"0": [0, 0, 0], "0.25": [0, 26, 12], "0.75": [0, 0, 0]}},
        }),
    }

    PENGUIN["clips"] = {
        "idle": clip(4.0, True, {
            "body": {"position": {"0": [0, 0, 0], "1.0": [0, 0.25, 0], "2.0": [0, 0, 0], "3.0": [0, 0.25, 0], "4.0": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.8": [4, 10, 0], "1.6": [0, -8, 0], "2.6": [-3, 6, 0], "4.0": [0, 0, 0]}},
            "flipper_l": {"rotation": {"0": [0, 0, -4], "1.0": [0, 0, -12], "2.0": [0, 0, -4], "3.0": [0, 0, -12], "4.0": [0, 0, -4]}},
            "flipper_r": {"rotation": {"0": [0, 0, 4], "1.0": [0, 0, 12], "2.0": [0, 0, 4], "3.0": [0, 0, 12], "4.0": [0, 0, 4]}},
            "tail": {"rotation": {"0": [0, 0, 0], "1.5": [0, 8, 0], "3.0": [0, -8, 0], "4.0": [0, 0, 0]}},
        }),
        "walk": clip(1.0, True, {
            "body": {"rotation": {"0": [0, 0, -4], "0.25": [0, 0, 0], "0.5": [0, 0, 4], "0.75": [0, 0, 0], "1.0": [0, 0, -4]}, "position": {"0": [0, 0.65, 0], "0.25": [0, 0.8, 0], "0.5": [0, 0.65, 0], "0.75": [0, 0.8, 0], "1.0": [0, 0.65, 0]}},
            "foot_l": {"rotation": {"0": [-12, 0, 0], "0.5": [12, 0, 0], "1.0": [-12, 0, 0]}},
            "foot_r": {"rotation": {"0": [12, 0, 0], "0.5": [-12, 0, 0], "1.0": [12, 0, 0]}},
            "flipper_l": {"rotation": {"0": [0, 0, -16], "0.5": [0, 0, -26], "1.0": [0, 0, -16]}},
            "flipper_r": {"rotation": {"0": [0, 0, 16], "0.5": [0, 0, 26], "1.0": [0, 0, 16]}},
            "head": {"rotation": {"0": [0, 0, 4], "0.5": [0, 0, -4], "1.0": [0, 0, 4]}},
            "tail": {"rotation": {"0": [0, -8, 0], "0.5": [0, 8, 0], "1.0": [0, -8, 0]}},
        }),
        "run": clip(0.7, True, {
            "body": {"rotation": {"0": [0, 0, -6], "0.175": [0, 0, 0], "0.35": [0, 0, 6], "0.525": [0, 0, 0], "0.7": [0, 0, -6]}, "position": {"0": [0, 0.85, 0], "0.175": [0, 1.05, 0], "0.35": [0, 0.85, 0], "0.525": [0, 1.05, 0], "0.7": [0, 0.85, 0]}},
            "foot_l": {"rotation": {"0": [-16, 0, 0], "0.35": [16, 0, 0], "0.7": [-16, 0, 0]}},
            "foot_r": {"rotation": {"0": [16, 0, 0], "0.35": [-16, 0, 0], "0.7": [16, 0, 0]}},
            "flipper_l": {"rotation": {"0": [0, 0, -26], "0.35": [0, 0, -40], "0.7": [0, 0, -26]}},
            "flipper_r": {"rotation": {"0": [0, 0, 26], "0.35": [0, 0, 40], "0.7": [0, 0, 26]}},
            "head": {"rotation": {"0": [0, 0, 6], "0.35": [0, 0, -6], "0.7": [0, 0, 6]}},
            "tail": {"rotation": {"0": [0, -12, 0], "0.35": [0, 12, 0], "0.7": [0, -12, 0]}},
        }),
        "swim": clip(1.2, True, {
            "body": {"rotation": {"0": [-72, 0, 0], "1.2": [-72, 0, 0]}, "position": {"0": [0, 2.0, 0], "1.2": [0, 2.0, 0]}},
            "head": {"rotation": {"0": [58, 0, 0], "0.6": [64, 0, 0], "1.2": [58, 0, 0]}},
            "flipper_l": {"rotation": {"0": [0, 0, -12], "0.3": [0, 0, -38], "0.6": [0, 0, -12], "0.9": [0, 0, -38], "1.2": [0, 0, -12]}},
            "flipper_r": {"rotation": {"0": [0, 0, 12], "0.3": [0, 0, 38], "0.6": [0, 0, 12], "0.9": [0, 0, 38], "1.2": [0, 0, 12]}},
            "foot_l": {"rotation": {"0": [48, 0, 0], "0.6": [56, 0, 0], "1.2": [48, 0, 0]}},
            "foot_r": {"rotation": {"0": [48, 0, 0], "0.6": [56, 0, 0], "1.2": [48, 0, 0]}},
            "tail": {"rotation": {"0": [0, -12, 0], "0.6": [0, 12, 0], "1.2": [0, -12, 0]}},
        }),
    }

    SNAKE["clips"] = {
        "idle": clip(4.0, True, {
            "body1": {"rotation": {"0": [0, 0, 0], "1.0": [0, 4, 0], "2.0": [0, 0, 0], "3.0": [0, -4, 0], "4.0": [0, 0, 0]}},
            "body2": {"rotation": {"0": [0, 0, 0], "1.0": [0, -5, 0], "2.0": [0, 0, 0], "3.0": [0, 5, 0], "4.0": [0, 0, 0]}},
            "body3": {"rotation": {"0": [0, 0, 0], "1.0": [0, 5, 0], "2.0": [0, 0, 0], "3.0": [0, -5, 0], "4.0": [0, 0, 0]}},
            "body4": {"rotation": {"0": [0, 0, 0], "1.0": [0, -4, 0], "2.0": [0, 0, 0], "3.0": [0, 4, 0], "4.0": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.8": [1, 7, 1], "1.6": [0, -5, 0], "2.6": [2, 9, -1], "4.0": [0, 0, 0]}},
            "jaw": {"rotation": {"0": [0, 0, 0], "1.8": [0, 0, 0], "2.0": [7, 0, 0], "2.2": [0, 0, 0], "4.0": [0, 0, 0]}},
            "tongue": {"rotation": {"0": [0, 0, 0], "1.9": [0, 0, 0], "2.05": [12, 0, 0], "2.2": [0, 0, 0], "3.7": [0, 0, 0], "3.85": [12, 0, 0], "4.0": [0, 0, 0]}},
            "tail": {"rotation": {"0": [0, 0, 0], "1.0": [0, 10, 0], "2.0": [0, 0, 0], "3.0": [0, -10, 0], "4.0": [0, 0, 0]}},
        }),
        "walk": clip(1.2, True, {
            "body1": {"rotation": {"0": [0, 0, 0], "0.3": [0, 10, 0], "0.6": [0, 0, 0], "0.9": [0, -10, 0], "1.2": [0, 0, 0]}},
            "body2": {"rotation": {"0": [0, 0, 0], "0.3": [0, -13, 0], "0.6": [0, 0, 0], "0.9": [0, 13, 0], "1.2": [0, 0, 0]}},
            "body3": {"rotation": {"0": [0, 0, 0], "0.3": [0, 15, 0], "0.6": [0, 0, 0], "0.9": [0, -15, 0], "1.2": [0, 0, 0]}},
            "body4": {"rotation": {"0": [0, 0, 0], "0.3": [0, -15, 0], "0.6": [0, 0, 0], "0.9": [0, 15, 0], "1.2": [0, 0, 0]}},
            "body5": {"rotation": {"0": [0, 0, 0], "0.3": [0, 13, 0], "0.6": [0, 0, 0], "0.9": [0, -13, 0], "1.2": [0, 0, 0]}},
            "body6": {"rotation": {"0": [0, 0, 0], "0.3": [0, -10, 0], "0.6": [0, 0, 0], "0.9": [0, 10, 0], "1.2": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.3": [1, -8, 0], "0.6": [0, 0, 0], "0.9": [1, 8, 0], "1.2": [0, 0, 0]}},
            "tail": {"rotation": {"0": [0, 12, 0], "0.6": [0, -12, 0], "1.2": [0, 12, 0]}},
        }),
        "run": clip(0.7, True, {
            "body1": {"rotation": {"0": [0, 0, 0], "0.175": [0, 16, 0], "0.35": [0, 0, 0], "0.525": [0, -16, 0], "0.7": [0, 0, 0]}},
            "body2": {"rotation": {"0": [0, 0, 0], "0.175": [0, -20, 0], "0.35": [0, 0, 0], "0.525": [0, 20, 0], "0.7": [0, 0, 0]}},
            "body3": {"rotation": {"0": [0, 0, 0], "0.175": [0, 23, 0], "0.35": [0, 0, 0], "0.525": [0, -23, 0], "0.7": [0, 0, 0]}},
            "body4": {"rotation": {"0": [0, 0, 0], "0.175": [0, -23, 0], "0.35": [0, 0, 0], "0.525": [0, 23, 0], "0.7": [0, 0, 0]}},
            "body5": {"rotation": {"0": [0, 0, 0], "0.175": [0, 20, 0], "0.35": [0, 0, 0], "0.525": [0, -20, 0], "0.7": [0, 0, 0]}},
            "body6": {"rotation": {"0": [0, 0, 0], "0.175": [0, -16, 0], "0.35": [0, 0, 0], "0.525": [0, 16, 0], "0.7": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.175": [1, -12, 0], "0.35": [0, 0, 0], "0.525": [1, 12, 0], "0.7": [0, 0, 0]}},
            "tail": {"rotation": {"0": [0, 18, 0], "0.35": [0, -18, 0], "0.7": [0, 18, 0]}},
        }),
        "attack": clip(0.9, False, {
            "body0": {"position": {"0": [0, 0, 0], "0.3": [0, 1.1, -2.0], "0.5": [0, 0.75, -3.0], "0.9": [0, 0, 0]}},
            "body1": {"rotation": {"0": [0, 0, 0], "0.3": [0, 14, 0], "0.5": [0, 6, 0], "0.9": [0, 0, 0]}},
            "body2": {"rotation": {"0": [0, 0, 0], "0.3": [0, -20, 0], "0.5": [0, -8, 0], "0.9": [0, 0, 0]}},
            "body3": {"rotation": {"0": [0, 0, 0], "0.3": [0, 18, 0], "0.5": [0, 8, 0], "0.9": [0, 0, 0]}},
            "head": {"rotation": {"0": [0, 0, 0], "0.3": [-8, 0, 0], "0.5": [6, 0, 0], "0.9": [0, 0, 0]}},
            "jaw": {"rotation": {"0": [0, 0, 0], "0.2": [24, 0, 0], "0.55": [24, 0, 0], "0.9": [0, 0, 0]}},
            "tongue": {"rotation": {"0": [0, 0, 0], "0.25": [12, 0, 0], "0.6": [0, 0, 0], "0.9": [0, 0, 0]}},
            "tail": {"rotation": {"0": [0, 0, 0], "0.3": [0, -18, 0], "0.9": [0, 0, 0]}},
        }),
    }

make_clips()

MONKEY["clips"].pop("attack", None)
MONKEY["clips"]["idle"]["bones"]["tail4"] = {"rotation": {"0": [0, 0, 0], "1": [0, -18, 14], "2": [0, 0, 0], "3": [0, 18, -14], "4": [0, 0, 0]}}
MONKEY["clips"]["walk"]["bones"]["tail4"] = {"rotation": {"0": [0, -14, 0], "0.45": [0, 14, 0], "0.9": [0, -14, 0]}}
MONKEY["clips"]["run"]["bones"]["tail4"] = {"rotation": {"0": [0, -20, 10], "0.28": [0, 20, 10], "0.55": [0, -20, 10]}}
SNAKE["clips"]["idle"]["bones"]["tail2"] = {"rotation": {"0": [0, 0, 0], "1.0": [0, 14, 0], "2.0": [0, 0, 0], "3.0": [0, -14, 0], "4.0": [0, 0, 0]}}
SNAKE["clips"]["walk"]["bones"]["tail2"] = {"rotation": {"0": [0, 16, 0], "0.6": [0, -16, 0], "1.2": [0, 16, 0]}}
SNAKE["clips"]["run"]["bones"]["tail2"] = {"rotation": {"0": [0, 22, 0], "0.35": [0, -22, 0], "0.7": [0, 22, 0]}}
SNAKE["clips"]["attack"]["bones"]["tail2"] = {"rotation": {"0": [0, 0, 0], "0.3": [0, 20, 0], "0.9": [0, 0, 0]}}
for _snake_clip in ("idle", "walk", "run"):
    for _bone, _offset in (("body1", 5), ("body2", -6), ("body3", 7), ("body4", -7), ("body5", 5), ("body6", -4)):
        if _bone not in SNAKE["clips"][_snake_clip]["bones"]:
            continue
        for _value in SNAKE["clips"][_snake_clip]["bones"][_bone]["rotation"].values():
            _value[1] += _offset

BLACK_BEAR["clips"] = copy.deepcopy(BEAR["clips"])
LION["clips"] = copy.deepcopy(TIGER["clips"])
LIONESS["clips"] = copy.deepcopy(LION["clips"])

DEER["clips"] = {
    "idle": clip(4.0, True, {
        "bodyb": {"position": {"0": [0, 0, 0], "1.0": [0, 0.18, 0], "2.0": [0, 0, 0], "3.0": [0, 0.16, 0], "4.0": [0, 0, 0]}},
        "neck": {"rotation": {"0": [0, 0, 0], "0.8": [2, 4, 0], "1.8": [0, -3, 0], "2.8": [-2, 5, 0], "4.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.8": [1, 8, 0], "1.8": [0, -5, 0], "2.8": [-1, 9, 0], "4.0": [0, 0, 0]}},
        "ear1": {"rotation": {"0": [0, 0, 0], "1.6": [0, 0, 9], "1.8": [0, 0, 0], "4.0": [0, 0, 0]}},
        "ear2": {"rotation": {"0": [0, 0, 0], "3.1": [0, 0, -9], "3.3": [0, 0, 0], "4.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 0, 0], "1.5": [0, 10, 0], "2.0": [0, 0, 0], "3.5": [0, -8, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.0, True, {
        "bodyb": {"position": {"0": [0, 0, 0], "0.25": [0, 0.3, 0], "0.5": [0, 0, 0], "0.75": [0, 0.3, 0], "1.0": [0, 0, 0]}},
        "leg0": {"rotation": {"0": [28, 0, 0], "0.5": [-28, 0, 0], "1.0": [28, 0, 0]}},
        "leg2": {"rotation": {"0": [28, 0, 0], "0.5": [-28, 0, 0], "1.0": [28, 0, 0]}},
        "leg1": {"rotation": {"0": [-28, 0, 0], "0.5": [28, 0, 0], "1.0": [-28, 0, 0]}},
        "leg3": {"rotation": {"0": [-28, 0, 0], "0.5": [28, 0, 0], "1.0": [-28, 0, 0]}},
        "neck": {"rotation": {"0": [0, 0, 0], "0.25": [1, 2, 0], "0.5": [0, 0, 0], "0.75": [-1, -2, 0], "1.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.25": [1, 3, 0], "0.5": [0, 0, 0], "0.75": [-1, -3, 0], "1.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 6, 0], "0.5": [0, -6, 0], "1.0": [0, 6, 0]}},
    }),
    "run": clip(0.6, True, {
        "bodyb": {"position": {"0": [0, 0, 0], "0.15": [0, 0.55, 0], "0.3": [0, 0.05, 0], "0.45": [0, 0.55, 0], "0.6": [0, 0, 0]}},
        "leg0": {"rotation": {"0": [44, 0, 0], "0.3": [-44, 0, 0], "0.6": [44, 0, 0]}},
        "leg2": {"rotation": {"0": [44, 0, 0], "0.3": [-44, 0, 0], "0.6": [44, 0, 0]}},
        "leg1": {"rotation": {"0": [-44, 0, 0], "0.3": [44, 0, 0], "0.6": [-44, 0, 0]}},
        "leg3": {"rotation": {"0": [-44, 0, 0], "0.3": [44, 0, 0], "0.6": [-44, 0, 0]}},
        "neck": {"rotation": {"0": [-4, 0, 0], "0.3": [-2, 0, 0], "0.6": [-4, 0, 0]}},
        "head": {"rotation": {"0": [3, 0, 0], "0.3": [0, 0, 0], "0.6": [3, 0, 0]}},
    }),
}

SCORPION["clips"] = {
    "idle": clip(4.0, True, {
        "root": {"position": {"0": [0, 0, 0], "1.2": [0, 0.25, 0], "2.4": [0, 0.05, 0], "3.4": [0, 0.2, 0], "4.0": [0, 0, 0]}},
        "body": {"rotation": {"0": [0, 0, 0], "1.0": [0, 4, 0], "2.0": [0, 0, 0], "3.0": [0, -4, 0], "4.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.8": [1, 7, 0], "1.8": [0, -5, 0], "2.8": [-1, 8, 0], "4.0": [0, 0, 0]}},
        "left_arm": {"rotation": {"0": [0, 0, 0], "2.0": [4, 0, -3], "4.0": [0, 0, 0]}},
        "right_arm": {"rotation": {"0": [0, 0, 0], "2.0": [4, 0, 3], "4.0": [0, 0, 0]}},
        "hcost": {"rotation": {"0": [0, 0, 0], "1.0": [0, 8, 0], "2.0": [0, 0, 0], "3.0": [0, -8, 0], "4.0": [0, 0, 0]}},
        "bone3": {"rotation": {"0": [0, 0, 0], "1.0": [0, 6, 0], "2.0": [0, 0, 0], "3.0": [0, -6, 0], "4.0": [0, 0, 0]}},
        "bone5": {"rotation": {"0": [0, 0, 0], "1.0": [0, -6, 0], "2.0": [0, 0, 0], "3.0": [0, 6, 0], "4.0": [0, 0, 0]}},
        "bone7": {"rotation": {"0": [0, 0, 0], "1.0": [0, 8, 0], "2.0": [0, 0, 0], "3.0": [0, -8, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.0, True, {
        "root": {"position": {"0": [0, 0, 0], "0.25": [0, 0.35, 0], "0.5": [0, 0, 0], "0.75": [0, 0.35, 0], "1.0": [0, 0, 0]}},
        "left_leg": {"rotation": {"0": [24, 0, 0], "0.5": [-24, 0, 0], "1.0": [24, 0, 0]}},
        "right_leg": {"rotation": {"0": [-24, 0, 0], "0.5": [24, 0, 0], "1.0": [-24, 0, 0]}},
        "left_leg2": {"rotation": {"0": [-20, 0, 0], "0.5": [20, 0, 0], "1.0": [-20, 0, 0]}},
        "right_leg2": {"rotation": {"0": [20, 0, 0], "0.5": [-20, 0, 0], "1.0": [20, 0, 0]}},
        "left_arm": {"rotation": {"0": [-18, 0, 0], "0.5": [18, 0, 0], "1.0": [-18, 0, 0]}},
        "right_arm": {"rotation": {"0": [18, 0, 0], "0.5": [-18, 0, 0], "1.0": [18, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.25": [1, 3, 0], "0.5": [0, 0, 0], "0.75": [-1, -3, 0], "1.0": [0, 0, 0]}},
        "hcost": {"rotation": {"0": [0, 10, 0], "0.5": [0, -10, 0], "1.0": [0, 10, 0]}},
        "bone3": {"rotation": {"0": [0, -8, 0], "0.5": [0, 8, 0], "1.0": [0, -8, 0]}},
        "bone5": {"rotation": {"0": [0, 10, 0], "0.5": [0, -10, 0], "1.0": [0, 10, 0]}},
    }),
    "run": clip(0.7, True, {
        "root": {"position": {"0": [0, 1.8, 0], "0.175": [0, 2.4, 0], "0.35": [0, 1.8, 0], "0.525": [0, 2.4, 0], "0.7": [0, 1.8, 0]}},
        "left_leg": {"rotation": {"0": [38, 0, 0], "0.35": [-38, 0, 0], "0.7": [38, 0, 0]}},
        "right_leg": {"rotation": {"0": [-38, 0, 0], "0.35": [38, 0, 0], "0.7": [-38, 0, 0]}},
        "left_leg2": {"rotation": {"0": [-32, 0, 0], "0.35": [32, 0, 0], "0.7": [-32, 0, 0]}},
        "right_leg2": {"rotation": {"0": [32, 0, 0], "0.35": [-32, 0, 0], "0.7": [32, 0, 0]}},
        "left_arm": {"rotation": {"0": [-32, 0, 0], "0.35": [32, 0, 0], "0.7": [-32, 0, 0]}},
        "right_arm": {"rotation": {"0": [32, 0, 0], "0.35": [-32, 0, 0], "0.7": [32, 0, 0]}},
        "head": {"rotation": {"0": [3, 0, 0], "0.35": [-2, 0, 0], "0.7": [3, 0, 0]}},
        "hcost": {"rotation": {"0": [0, 16, 0], "0.35": [0, -16, 0], "0.7": [0, 16, 0]}},
    }),
    "attack": clip(1.0, False, {
        "root": {"position": {"0": [0, 0, 0], "0.3": [0, 0.5, -1.4], "0.55": [0, 0.2, -2.2], "1.0": [0, 0, 0]}},
        "body": {"rotation": {"0": [0, 0, 0], "0.3": [0, 12, 0], "0.55": [0, -6, 0], "1.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.3": [-8, 10, 0], "0.55": [5, -6, 0], "1.0": [0, 0, 0]}},
        "left_arm": {"rotation": {"0": [0, 0, 0], "0.3": [-70, 0, -20], "0.55": [-20, 0, 8], "1.0": [0, 0, 0]}},
        "right_arm": {"rotation": {"0": [0, 0, 0], "0.3": [-60, 0, 20], "0.55": [-15, 0, -8], "1.0": [0, 0, 0]}},
        "hcost": {"rotation": {"0": [0, 0, 0], "0.3": [-35, 20, 0], "0.55": [10, -10, 0], "1.0": [0, 0, 0]}},
        "bone3": {"rotation": {"0": [0, 0, 0], "0.3": [-25, -15, 0], "0.55": [15, 10, 0], "1.0": [0, 0, 0]}},
        "bone5": {"rotation": {"0": [0, 0, 0], "0.3": [-30, 15, 0], "0.55": [12, -8, 0], "1.0": [0, 0, 0]}},
        "bone7": {"rotation": {"0": [0, 0, 0], "0.3": [-20, -20, 0], "0.55": [10, 12, 0], "1.0": [0, 0, 0]}},
    }),
}

WHALE["clips"] = {
    "idle": clip(4.0, True, {
        "Body": {"rotation": {"0": [0, 0, -1.5], "2.0": [0, 0, 1.5], "4.0": [0, 0, -1.5]}, "position": {"0": [0, 3.0, 0], "2.0": [0, 3.25, 0], "4.0": [0, 3.0, 0]}},
        "Head": {"rotation": {"0": [0, 0, 0], "1.2": [0, 4, 0], "2.8": [0, -4, 0], "4.0": [0, 0, 0]}},
        "Tail": {"rotation": {"0": [0, -8, 0], "2.0": [0, 8, 0], "4.0": [0, -8, 0]}},
        "Tail2": {"rotation": {"0": [0, 10, 0], "2.0": [0, -10, 0], "4.0": [0, 10, 0]}},
        "Tail3": {"rotation": {"0": [0, -14, 0], "2.0": [0, 14, 0], "4.0": [0, -14, 0]}},
        "Tail4": {"rotation": {"0": [0, 18, 0], "2.0": [0, -18, 0], "4.0": [0, 18, 0]}},
        "Fin": {"rotation": {"0": [0, -22, 0], "2.0": [0, 22, 0], "4.0": [0, -22, 0]}},
        "Finleft": {"rotation": {"0": [0, 0, 6], "2.0": [0, 0, 14], "4.0": [0, 0, 6]}},
        "Finright": {"rotation": {"0": [0, 0, -6], "2.0": [0, 0, -14], "4.0": [0, 0, -6]}},
    }),
    "walk": clip(1.2, True, {
        "Body": {"rotation": {"0": [0, 0, -3], "0.6": [0, 0, 3], "1.2": [0, 0, -3]}, "position": {"0": [0, 3.0, 0], "0.6": [0, 3.35, 0], "1.2": [0, 3.0, 0]}},
        "Head": {"rotation": {"0": [0, -3, 0], "0.6": [0, 3, 0], "1.2": [0, -3, 0]}},
        "Tail": {"rotation": {"0": [0, 16, 0], "0.6": [0, -16, 0], "1.2": [0, 16, 0]}},
        "Tail2": {"rotation": {"0": [0, -22, 0], "0.6": [0, 22, 0], "1.2": [0, -22, 0]}},
        "Tail3": {"rotation": {"0": [0, 26, 0], "0.6": [0, -26, 0], "1.2": [0, 26, 0]}},
        "Tail4": {"rotation": {"0": [0, -30, 0], "0.6": [0, 30, 0], "1.2": [0, -30, 0]}},
        "Fin": {"rotation": {"0": [0, 34, 0], "0.6": [0, -34, 0], "1.2": [0, 34, 0]}},
        "Finleft": {"rotation": {"0": [0, 0, 10], "0.6": [0, 0, 20], "1.2": [0, 0, 10]}},
        "Finright": {"rotation": {"0": [0, 0, -10], "0.6": [0, 0, -20], "1.2": [0, 0, -10]}},
    }),
    "run": clip(0.8, True, {
        "Body": {"rotation": {"0": [0, 0, -4], "0.4": [0, 0, 4], "0.8": [0, 0, -4]}, "position": {"0": [0, 3.0, 0], "0.4": [0, 3.5, 0], "0.8": [0, 3.0, 0]}},
        "Head": {"rotation": {"0": [0, -4, 0], "0.4": [0, 4, 0], "0.8": [0, -4, 0]}},
        "Tail": {"rotation": {"0": [0, 22, 0], "0.4": [0, -22, 0], "0.8": [0, 22, 0]}},
        "Tail2": {"rotation": {"0": [0, -28, 0], "0.4": [0, 28, 0], "0.8": [0, -28, 0]}},
        "Tail3": {"rotation": {"0": [0, 32, 0], "0.4": [0, -32, 0], "0.8": [0, 32, 0]}},
        "Tail4": {"rotation": {"0": [0, -38, 0], "0.4": [0, 38, 0], "0.8": [0, -38, 0]}},
        "Fin": {"rotation": {"0": [0, 42, 0], "0.4": [0, -42, 0], "0.8": [0, 42, 0]}},
        "Finleft": {"rotation": {"0": [0, 0, 16], "0.4": [0, 0, 28], "0.8": [0, 0, 16]}},
        "Finright": {"rotation": {"0": [0, 0, -16], "0.4": [0, 0, -28], "0.8": [0, 0, -16]}},
    }),
}

JELLY["clips"] = {
    "idle": clip(4.0, True, {
        "body": {"position": {"0": [0, 0, 0], "1.0": [0, 0.4, 0], "2.0": [0, 0.1, 0], "3.0": [0, 0.45, 0], "4.0": [0, 0, 0]}, "scale": {"0": [1, 1, 1], "1.0": [1.15, 0.85, 1.15], "2.0": [1, 1, 1], "3.0": [1.1, 0.9, 1.1], "4.0": [1, 1, 1]}, "rotation": {"0": [0, 0, 0], "2.0": [0, 8, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.2, True, {
        "body": {"position": {"0": [0, 0, 0], "0.3": [0, 0.45, 0], "0.6": [0, 0.1, 0], "0.9": [0, 0.45, 0], "1.2": [0, 0, 0]}, "scale": {"0": [1, 1, 1], "0.3": [1.2, 0.8, 1.2], "0.6": [1, 1, 1], "0.9": [1.15, 0.85, 1.15], "1.2": [1, 1, 1]}, "rotation": {"0": [0, 0, 0], "0.6": [0, 12, 0], "1.2": [0, 0, 0]}},
    }),
    "run": clip(0.8, True, {
        "body": {"position": {"0": [0, 0, 0], "0.2": [0, 0.55, 0], "0.4": [0, 0.15, 0], "0.6": [0, 0.55, 0], "0.8": [0, 0, 0]}, "scale": {"0": [1, 1, 1], "0.2": [1.22, 0.78, 1.22], "0.4": [1, 1, 1], "0.6": [1.18, 0.82, 1.18], "0.8": [1, 1, 1]}, "rotation": {"0": [0, 0, 0], "0.4": [0, 16, 0], "0.8": [0, 0, 0]}},
    }),
}


CROCODILE["clips"] = {
    "idle": clip(4.0, True, {
        "body": {"position": {"0": [0, 0, 0], "1.2": [0, 0.3, 0], "2.4": [0, 0.1, 0], "3.4": [0, 0.25, 0], "4.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "1.0": [1, 5, 0], "2.0": [0, 0, 0], "3.0": [-1, -5, 0], "4.0": [0, 0, 0]}},
        "jaw": {"rotation": {"0": [0, 0, 0], "2.0": [-3, 0, 0], "2.2": [0, 0, 0], "4.0": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, -8, 0], "2.0": [0, 8, 0], "4.0": [0, -8, 0]}},
        "tail2": {"rotation": {"0": [0, 10, 0], "2.0": [0, -10, 0], "4.0": [0, 10, 0]}},
        "tail3": {"rotation": {"0": [0, -12, 0], "2.0": [0, 12, 0], "4.0": [0, -12, 0]}},
    }),
    "walk": clip(1.4, True, {
        "body": {"position": {"0": [0, 1.2, 0], "0.35": [0, 1.55, 0], "0.7": [0, 1.2, 0], "1.05": [0, 1.55, 0], "1.4": [0, 1.2, 0]}},
        "leg_front_l": {"rotation": {"0": [24, 0, 0], "0.7": [-24, 0, 0], "1.4": [24, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-24, 0, 0], "0.7": [24, 0, 0], "1.4": [-24, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-24, 0, 0], "0.7": [24, 0, 0], "1.4": [-24, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [24, 0, 0], "0.7": [-24, 0, 0], "1.4": [24, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.35": [1, 3, 0], "0.7": [0, 0, 0], "1.05": [-1, -3, 0], "1.4": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 10, 0], "0.7": [0, -10, 0], "1.4": [0, 10, 0]}},
        "tail2": {"rotation": {"0": [0, -15, 0], "0.7": [0, 15, 0], "1.4": [0, -15, 0]}},
        "tail3": {"rotation": {"0": [0, 18, 0], "0.7": [0, -18, 0], "1.4": [0, 18, 0]}},
    }),
    "run": clip(0.9, True, {
        "body": {"position": {"0": [0, 1.4, 0], "0.225": [0, 1.8, 0], "0.45": [0, 1.4, 0], "0.675": [0, 1.8, 0], "0.9": [0, 1.4, 0]}},
        "leg_front_l": {"rotation": {"0": [34, 0, 0], "0.45": [-34, 0, 0], "0.9": [34, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-34, 0, 0], "0.45": [34, 0, 0], "0.9": [-34, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-34, 0, 0], "0.45": [34, 0, 0], "0.9": [-34, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [34, 0, 0], "0.45": [-34, 0, 0], "0.9": [34, 0, 0]}},
        "head": {"rotation": {"0": [2, 0, 0], "0.45": [-1, 0, 0], "0.9": [2, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 16, 0], "0.45": [0, -16, 0], "0.9": [0, 16, 0]}},
        "tail2": {"rotation": {"0": [0, -20, 0], "0.45": [0, 20, 0], "0.9": [0, -20, 0]}},
        "tail3": {"rotation": {"0": [0, 24, 0], "0.45": [0, -24, 0], "0.9": [0, 24, 0]}},
    }),
    "attack": clip(1.0, False, {
        "body": {"position": {"0": [0, 0, 0], "0.3": [0, 3.0, -1.5], "0.5": [0, 2.5, -2.5], "1.0": [0, 0, 0]}, "rotation": {"0": [0, 0, 0], "0.3": [0, 10, 0], "0.55": [0, -5, 0], "1.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.3": [-10, 0, 0], "0.55": [5, 0, 0], "1.0": [0, 0, 0]}},
        "jaw": {"rotation": {"0": [0, 0, 0], "0.25": [-10, 0, 0], "0.55": [-10, 0, 0], "0.9": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 0, 0], "0.3": [0, -18, 0], "1.0": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, 0, 0], "0.3": [0, 22, 0], "1.0": [0, 0, 0]}},
    }),
}

SHARK["clips"] = {
    "idle": clip(4.0, True, {
        "tail1": {"rotation": {"0": [0, -6, 0], "2.0": [0, 6, 0], "4.0": [0, -6, 0]}},
        "tail2": {"rotation": {"0": [0, 8, 0], "2.0": [0, -8, 0], "4.0": [0, 8, 0]}},
        "tail_fin": {"rotation": {"0": [0, -10, 0], "2.0": [0, 10, 0], "4.0": [0, -10, 0]}},
        "body": {"rotation": {"0": [0, 0, -1.5], "2.0": [0, 0, 1.5], "4.0": [0, 0, -1.5]}},
        "head": {"rotation": {"0": [0, 0, 0], "1.2": [0, 5, 0], "2.8": [0, -5, 0], "4.0": [0, 0, 0]}},
        "fin_l": {"rotation": {"0": [0, 0, 5], "2.0": [0, 0, 10], "4.0": [0, 0, 5]}},
        "fin_r": {"rotation": {"0": [0, 0, -5], "2.0": [0, 0, -10], "4.0": [0, 0, -5]}},
    }),
    "walk": clip(1.0, True, {
        "tail1": {"rotation": {"0": [0, 16, 0], "0.5": [0, -16, 0], "1.0": [0, 16, 0]}},
        "tail2": {"rotation": {"0": [0, -22, 0], "0.5": [0, 22, 0], "1.0": [0, -22, 0]}},
        "tail_fin": {"rotation": {"0": [0, 25, 0], "0.5": [0, -25, 0], "1.0": [0, 25, 0]}},
        "body": {"rotation": {"0": [0, 0, -3], "0.5": [0, 0, 3], "1.0": [0, 0, -3]}},
        "head": {"rotation": {"0": [0, -3, 0], "0.5": [0, 3, 0], "1.0": [0, -3, 0]}},
        "fin_l": {"rotation": {"0": [0, 0, 6], "0.5": [0, 0, 14], "1.0": [0, 0, 6]}},
        "fin_r": {"rotation": {"0": [0, 0, -6], "0.5": [0, 0, -14], "1.0": [0, 0, -6]}},
    }),
    "run": clip(0.6, True, {
        "tail1": {"rotation": {"0": [0, 24, 0], "0.3": [0, -24, 0], "0.6": [0, 24, 0]}},
        "tail2": {"rotation": {"0": [0, -30, 0], "0.3": [0, 30, 0], "0.6": [0, -30, 0]}},
        "tail_fin": {"rotation": {"0": [0, 34, 0], "0.3": [0, -34, 0], "0.6": [0, 34, 0]}},
        "body": {"rotation": {"0": [0, 0, -4], "0.3": [0, 0, 4], "0.6": [0, 0, -4]}},
        "head": {"rotation": {"0": [0, -4, 0], "0.3": [0, 4, 0], "0.6": [0, -4, 0]}},
        "fin_l": {"rotation": {"0": [0, 0, 10], "0.3": [0, 0, 20], "0.6": [0, 0, 10]}},
        "fin_r": {"rotation": {"0": [0, 0, -10], "0.3": [0, 0, -20], "0.6": [0, 0, -10]}},
    }),
    "attack": clip(0.8, False, {
        "body": {"position": {"0": [0, 0, 0], "0.25": [0, 1.0, -2.0], "0.5": [0, 0.6, -1.0], "0.8": [0, 0, 0]}, "rotation": {"0": [0, 0, 0], "0.25": [0, 8, 0], "0.8": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.2": [-6, 0, 0], "0.5": [3, 0, 0], "0.8": [0, 0, 0]}},
        "jaw": {"rotation": {"0": [0, 0, 0], "0.2": [-8, 0, 0], "0.45": [-8, 0, 0], "0.7": [0, 0, 0], "0.8": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 0, 0], "0.25": [0, -20, 0], "0.8": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, 0, 0], "0.25": [0, 24, 0], "0.8": [0, 0, 0]}},
    }),
}

ELEPHANT["clips"] = {
    "idle": clip(4.0, True, {
        "body": {"position": {"0": [0, 0, 0], "1.2": [0, 0.3, 0], "2.4": [0, 0.08, 0], "3.4": [0, 0.25, 0], "4.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "1.0": [1, 5, 0], "2.0": [0, 0, 0], "3.0": [-1, -5, 0], "4.0": [0, 0, 0]}},
        "ear_l": {"rotation": {"0": [0, 0, 4], "1.4": [0, 0, 14], "2.4": [0, 0, 4], "4.0": [0, 0, 4]}},
        "ear_r": {"rotation": {"0": [0, 0, -4], "1.4": [0, 0, -14], "2.4": [0, 0, -4], "4.0": [0, 0, -4]}},
        "trunk1": {"rotation": {"0": [0, 0, 0], "1.0": [-4, 5, 0], "2.0": [0, 0, 0], "3.0": [4, -5, 0], "4.0": [0, 0, 0]}},
        "trunk2": {"rotation": {"0": [0, 0, 0], "1.0": [8, -8, 0], "2.0": [0, 0, 0], "3.0": [-6, 8, 0], "4.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 0, 0], "1.5": [0, 10, 0], "2.5": [0, 0, 0], "3.5": [0, -8, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.4, True, {
        "body": {"position": {"0": [0, 0.1, 0], "0.35": [0, 0.55, 0], "0.7": [0, 0.1, 0], "1.05": [0, 0.55, 0], "1.4": [0, 0.1, 0]}},
        "leg_front_l": {"rotation": {"0": [20, 0, 0], "0.7": [-20, 0, 0], "1.4": [20, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-20, 0, 0], "0.7": [20, 0, 0], "1.4": [-20, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-18, 0, 0], "0.7": [18, 0, 0], "1.4": [-18, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [18, 0, 0], "0.7": [-18, 0, 0], "1.4": [18, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.35": [1, 3, 0], "0.7": [0, 0, 0], "1.05": [-1, -3, 0], "1.4": [0, 0, 0]}},
        "ear_l": {"rotation": {"0": [0, 0, 5], "0.35": [0, 0, 12], "0.7": [0, 0, 5], "1.4": [0, 0, 5]}},
        "ear_r": {"rotation": {"0": [0, 0, -5], "0.35": [0, 0, -12], "0.7": [0, 0, -5], "1.4": [0, 0, -5]}},
        "trunk1": {"rotation": {"0": [0, 0, 0], "0.35": [-4, 3, 0], "0.7": [0, 0, 0], "1.05": [4, -3, 0], "1.4": [0, 0, 0]}},
        "trunk2": {"rotation": {"0": [0, 0, 0], "0.35": [5, -4, 0], "0.7": [0, 0, 0], "1.05": [-5, 4, 0], "1.4": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 7, 0], "0.7": [0, -7, 0], "1.4": [0, 7, 0]}},
    }),
    "run": clip(1.0, True, {
        "body": {"position": {"0": [0, 0.3, 0], "0.25": [0, 0.8, 0], "0.5": [0, 0.3, 0], "0.75": [0, 0.8, 0], "1.0": [0, 0.3, 0]}},
        "leg_front_l": {"rotation": {"0": [32, 0, 0], "0.5": [-32, 0, 0], "1.0": [32, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-32, 0, 0], "0.5": [32, 0, 0], "1.0": [-32, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-28, 0, 0], "0.5": [28, 0, 0], "1.0": [-28, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [28, 0, 0], "0.5": [-28, 0, 0], "1.0": [28, 0, 0]}},
        "head": {"rotation": {"0": [2, 0, 0], "0.5": [-1, 0, 0], "1.0": [2, 0, 0]}},
        "ear_l": {"rotation": {"0": [0, 0, 8], "0.5": [0, 0, 18], "1.0": [0, 0, 8]}},
        "ear_r": {"rotation": {"0": [0, 0, -8], "0.5": [0, 0, -18], "1.0": [0, 0, -8]}},
        "trunk1": {"rotation": {"0": [-6, 0, 0], "0.5": [4, 0, 0], "1.0": [-6, 0, 0]}},
        "trunk2": {"rotation": {"0": [8, 0, 0], "0.5": [-6, 0, 0], "1.0": [8, 0, 0]}},
        "tail": {"rotation": {"0": [0, 12, 0], "0.5": [0, -12, 0], "1.0": [0, 12, 0]}},
    }),
    "attack": clip(1.0, False, {
        "body": {"position": {"0": [0, 0, 0], "0.3": [0, 0.6, -1.2], "0.55": [0, 0.3, -2.0], "1.0": [0, 0, 0]}, "rotation": {"0": [0, 0, 0], "0.3": [0, 10, 0], "0.55": [0, -6, 0], "1.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.3": [-8, 12, 0], "0.55": [4, -8, 0], "1.0": [0, 0, 0]}},
        "trunk1": {"rotation": {"0": [0, 0, 0], "0.3": [-48, 18, 0], "0.55": [12, -10, 0], "1.0": [0, 0, 0]}},
        "trunk2": {"rotation": {"0": [0, 0, 0], "0.3": [-28, 15, 0], "0.55": [18, -8, 0], "1.0": [0, 0, 0]}},
        "ear_l": {"rotation": {"0": [0, 0, 5], "0.3": [0, 0, 28], "0.55": [0, 0, 10], "1.0": [0, 0, 5]}},
        "ear_r": {"rotation": {"0": [0, 0, -5], "0.3": [0, 0, -28], "0.55": [0, 0, -10], "1.0": [0, 0, -5]}},
        "leg_front_l": {"rotation": {"0": [0, 0, 0], "0.3": [-35, 0, 0], "0.55": [10, 0, 0], "1.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 0, 0], "0.3": [0, -18, 0], "1.0": [0, 0, 0]}},
    }),
}

BISON["clips"] = {
    "idle": clip(4.0, True, {
        "body": {"position": {"0": [0, 0, 0], "1.0": [0, 0.25, 0], "2.0": [0, 0, 0], "3.0": [0, 0.2, 0], "4.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.9": [2, 6, 0], "1.8": [0, -4, 0], "2.8": [-2, 7, 0], "4.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 0, 0], "1.2": [0, 10, 0], "2.2": [0, 0, 0], "3.2": [0, -10, 0], "4.0": [0, 0, 0]}},
        "leg_front_l": {"rotation": {"0": [0, 0, 0], "2.0": [2, 0, 0], "4.0": [0, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [0, 0, 0], "2.6": [-2, 0, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.2, True, {
        "body": {"position": {"0": [0, 0, 0], "0.3": [0, 0.45, 0], "0.6": [0, 0, 0], "0.9": [0, 0.45, 0], "1.2": [0, 0, 0]}},
        "leg_front_l": {"rotation": {"0": [25, 0, 0], "0.6": [-25, 0, 0], "1.2": [25, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-25, 0, 0], "0.6": [25, 0, 0], "1.2": [-25, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-22, 0, 0], "0.6": [22, 0, 0], "1.2": [-22, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [22, 0, 0], "0.6": [-22, 0, 0], "1.2": [22, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.3": [2, 3, 0], "0.6": [0, 0, 0], "0.9": [-2, -3, 0], "1.2": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 8, 0], "0.6": [0, -8, 0], "1.2": [0, 8, 0]}},
    }),
    "run": clip(0.8, True, {
        "body": {"position": {"0": [0, 0, 0], "0.2": [0, 0.7, 0], "0.4": [0, 0, 0], "0.6": [0, 0.7, 0], "0.8": [0, 0, 0]}},
        "leg_front_l": {"rotation": {"0": [36, 0, 0], "0.4": [-36, 0, 0], "0.8": [36, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-36, 0, 0], "0.4": [36, 0, 0], "0.8": [-36, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-32, 0, 0], "0.4": [32, 0, 0], "0.8": [-32, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [32, 0, 0], "0.4": [-32, 0, 0], "0.8": [32, 0, 0]}},
        "head": {"rotation": {"0": [3, 0, 0], "0.4": [-2, 0, 0], "0.8": [3, 0, 0]}},
        "tail": {"rotation": {"0": [0, 14, 0], "0.4": [0, -14, 0], "0.8": [0, 14, 0]}},
    }),
    "attack": clip(1.0, False, {
        "body": {"position": {"0": [0, 0, 0], "0.3": [0, 0.5, -1.5], "0.55": [0, 0.2, -2.5], "1.0": [0, 0, 0]}, "rotation": {"0": [0, 0, 0], "0.3": [0, 8, 0], "0.55": [0, -4, 0], "1.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.3": [-18, 8, 0], "0.55": [8, -5, 0], "1.0": [0, 0, 0]}},
        "leg_front_l": {"rotation": {"0": [0, 0, 0], "0.3": [-25, 0, 0], "0.55": [8, 0, 0], "1.0": [0, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [0, 0, 0], "0.3": [-15, 0, 0], "0.55": [5, 0, 0], "1.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 0, 0], "0.3": [0, -18, 0], "1.0": [0, 0, 0]}},
    }),
}

GIRAFFE["clips"] = {
    "idle": clip(5.0, True, {
        "body": {"position": {"0": [0, 0, 0], "1.2": [0, 0.25, 0], "2.5": [0, 0.05, 0], "3.8": [0, 0.2, 0], "5.0": [0, 0, 0]}},
        "neck1": {"rotation": {"0": [0, 0, 0], "1.2": [-2, 4, 0], "2.5": [0, 0, 0], "3.8": [2, -4, 0], "5.0": [0, 0, 0]}},
        "neck2": {"rotation": {"0": [0, 0, 0], "1.2": [1, -3, 0], "2.5": [0, 0, 0], "3.8": [-1, 3, 0], "5.0": [0, 0, 0]}},
        "neck3": {"rotation": {"0": [0, 0, 0], "1.2": [-1, 3, 0], "2.5": [0, 0, 0], "3.8": [1, -3, 0], "5.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "1.0": [2, 7, 0], "2.4": [0, -5, 0], "3.6": [-2, 8, 0], "5.0": [0, 0, 0]}},
        "ear_l": {"rotation": {"0": [0, 0, 0], "2.0": [0, 0, 8], "2.2": [0, 0, 0], "5.0": [0, 0, 0]}},
        "ear_r": {"rotation": {"0": [0, 0, 0], "3.6": [0, 0, -8], "3.8": [0, 0, 0], "5.0": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 0, 0], "2.0": [0, 10, 0], "3.5": [0, -8, 0], "5.0": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, 0, 0], "2.0": [0, -12, 0], "3.5": [0, 12, 0], "5.0": [0, 0, 0]}},
    }),
    "walk": clip(1.4, True, {
        "body": {"position": {"0": [0, 0, 0], "0.35": [0, 0.35, 0], "0.7": [0, 0, 0], "1.05": [0, 0.35, 0], "1.4": [0, 0, 0]}},
        "leg_front_l": {"rotation": {"0": [24, 0, 0], "0.7": [-24, 0, 0], "1.4": [24, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-24, 0, 0], "0.7": [24, 0, 0], "1.4": [-24, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-24, 0, 0], "0.7": [24, 0, 0], "1.4": [-24, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [24, 0, 0], "0.7": [-24, 0, 0], "1.4": [24, 0, 0]}},
        "neck1": {"rotation": {"0": [0, 0, 0], "0.35": [-1, 2, 0], "0.7": [0, 0, 0], "1.05": [1, -2, 0], "1.4": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.35": [1, 3, 0], "0.7": [0, 0, 0], "1.05": [-1, -3, 0], "1.4": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 7, 0], "0.7": [0, -7, 0], "1.4": [0, 7, 0]}},
        "tail2": {"rotation": {"0": [0, -8, 0], "0.7": [0, 8, 0], "1.4": [0, -8, 0]}},
    }),
    "run": clip(1.0, True, {
        "body": {"position": {"0": [0, 0, 0], "0.25": [0, 0.55, 0], "0.5": [0, 0, 0], "0.75": [0, 0.55, 0], "1.0": [0, 0, 0]}},
        "leg_front_l": {"rotation": {"0": [40, 0, 0], "0.5": [-40, 0, 0], "1.0": [40, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-40, 0, 0], "0.5": [40, 0, 0], "1.0": [-40, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-40, 0, 0], "0.5": [40, 0, 0], "1.0": [-40, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [40, 0, 0], "0.5": [-40, 0, 0], "1.0": [40, 0, 0]}},
        "neck1": {"rotation": {"0": [-4, 0, 0], "0.5": [-2, 0, 0], "1.0": [-4, 0, 0]}},
        "head": {"rotation": {"0": [3, 0, 0], "0.5": [0, 0, 0], "1.0": [3, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 12, 0], "0.5": [0, -12, 0], "1.0": [0, 12, 0]}},
    }),
}

RACCOON["clips"] = {
    "idle": clip(4.0, True, {
        "body": {"position": {"0": [0, 0, 0], "1.0": [0, 0.18, 0], "2.0": [0, 0, 0], "3.0": [0, 0.18, 0], "4.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.8": [1, 8, 0], "1.8": [0, -6, 0], "2.8": [-1, 9, 0], "4.0": [0, 0, 0]}},
        "ear_l": {"rotation": {"0": [0, 0, 0], "1.5": [0, 0, 10], "1.7": [0, 0, 0], "4.0": [0, 0, 0]}},
        "ear_r": {"rotation": {"0": [0, 0, 0], "3.0": [0, 0, -10], "3.2": [0, 0, 0], "4.0": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 0, 0], "1.0": [0, 10, 0], "2.0": [0, 0, 0], "3.0": [0, -10, 0], "4.0": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, 0, 0], "1.0": [0, -12, 0], "2.0": [0, 0, 0], "3.0": [0, 12, 0], "4.0": [0, 0, 0]}},
        "tail3": {"rotation": {"0": [0, 0, 0], "1.0": [0, 14, 0], "2.0": [0, 0, 0], "3.0": [0, -14, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.0, True, {
        "body": {"position": {"0": [0, 0.9, 0], "0.25": [0, 1.2, 0], "0.5": [0, 0.9, 0], "0.75": [0, 1.2, 0], "1.0": [0, 0.9, 0]}},
        "leg_front_l": {"rotation": {"0": [26, 0, 0], "0.5": [-26, 0, 0], "1.0": [26, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-26, 0, 0], "0.5": [26, 0, 0], "1.0": [-26, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-26, 0, 0], "0.5": [26, 0, 0], "1.0": [-26, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [26, 0, 0], "0.5": [-26, 0, 0], "1.0": [26, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.25": [1, 3, 0], "0.5": [0, 0, 0], "0.75": [-1, -3, 0], "1.0": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 10, 0], "0.5": [0, -10, 0], "1.0": [0, 10, 0]}},
        "tail2": {"rotation": {"0": [0, -14, 0], "0.5": [0, 14, 0], "1.0": [0, -14, 0]}},
        "tail3": {"rotation": {"0": [0, 16, 0], "0.5": [0, -16, 0], "1.0": [0, 16, 0]}},
    }),
    "run": clip(0.6, True, {
        "body": {"position": {"0": [0, 0.9, 0], "0.15": [0, 1.45, 0], "0.3": [0, 0.9, 0], "0.45": [0, 1.45, 0], "0.6": [0, 0.9, 0]}},
        "leg_front_l": {"rotation": {"0": [40, 0, 0], "0.3": [-40, 0, 0], "0.6": [40, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [-40, 0, 0], "0.3": [40, 0, 0], "0.6": [-40, 0, 0]}},
        "leg_back_l": {"rotation": {"0": [-40, 0, 0], "0.3": [40, 0, 0], "0.6": [-40, 0, 0]}},
        "leg_back_r": {"rotation": {"0": [40, 0, 0], "0.3": [-40, 0, 0], "0.6": [40, 0, 0]}},
        "head": {"rotation": {"0": [3, 0, 0], "0.3": [-2, 0, 0], "0.6": [3, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 14, 0], "0.3": [0, -14, 0], "0.6": [0, 14, 0]}},
        "tail2": {"rotation": {"0": [0, -18, 0], "0.3": [0, 18, 0], "0.6": [0, -18, 0]}},
    }),
    "steal": clip(0.9, False, {
        "body": {"position": {"0": [0, 0, 0], "0.25": [0, 0.2, -0.8], "0.5": [0, 0.1, -1.2], "0.9": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.25": [-22, 8, 0], "0.5": [-28, 0, 0], "0.9": [0, 0, 0]}},
        "leg_front_l": {"rotation": {"0": [0, 0, 0], "0.25": [-18, 0, 0], "0.5": [6, 0, 0], "0.9": [0, 0, 0]}},
        "leg_front_r": {"rotation": {"0": [0, 0, 0], "0.25": [-12, 0, 0], "0.5": [4, 0, 0], "0.9": [0, 0, 0]}},
        "tail1": {"rotation": {"0": [0, 0, 0], "0.25": [0, -14, 0], "0.9": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, 0, 0], "0.25": [0, 16, 0], "0.9": [0, 0, 0]}},
    }),
}

RACCOON["clips"]["idle"]["bones"]["tail4"] = {"rotation": {"0": [0, 0, 0], "1.0": [0, -16, 0], "2.0": [0, 0, 0], "3.0": [0, 16, 0], "4.0": [0, 0, 0]}}
RACCOON["clips"]["walk"]["bones"]["tail4"] = {"rotation": {"0": [0, 18, 0], "0.5": [0, -18, 0], "1.0": [0, 18, 0]}}
RACCOON["clips"]["run"]["bones"]["tail4"] = {"rotation": {"0": [0, 22, 0], "0.3": [0, -22, 0], "0.6": [0, 22, 0]}}

for _clip in ("walk", "run"):
    SCORPION["clips"][_clip]["bones"].pop("left_leg2", None)
    SCORPION["clips"][_clip]["bones"].pop("right_leg2", None)
for _clip in ("idle", "walk", "run"):
    WHALE["clips"][_clip]["bones"].pop("Finleft", None)
    WHALE["clips"][_clip]["bones"].pop("Finright", None)

PLATYPUS["clips"] = {
    "idle": clip(4.0, True, {
        "platpyus": {"position": {"0": [0, 0, 0], "1.0": [0, 0.15, 0], "2.0": [0, 0, 0], "3.0": [0, 0.12, 0], "4.0": [0, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.8": [1, 7, 0], "1.8": [0, -5, 0], "2.8": [-1, 8, 0], "4.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, -8, 0], "2.0": [0, 8, 0], "4.0": [0, -8, 0]}},
        "leg1": {"rotation": {"0": [0, 0, 0], "2.0": [3, 0, 0], "4.0": [0, 0, 0]}},
        "leg2": {"rotation": {"0": [0, 0, 0], "2.0": [-3, 0, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.0, True, {
        "platpyus": {"position": {"0": [0, 0, 0], "0.25": [0, 0.2, 0], "0.5": [0, 0, 0], "0.75": [0, 0.2, 0], "1.0": [0, 0, 0]}},
        "leg1": {"rotation": {"0": [24, 0, 0], "0.5": [-24, 0, 0], "1.0": [24, 0, 0]}},
        "leg3": {"rotation": {"0": [24, 0, 0], "0.5": [-24, 0, 0], "1.0": [24, 0, 0]}},
        "leg2": {"rotation": {"0": [-24, 0, 0], "0.5": [24, 0, 0], "1.0": [-24, 0, 0]}},
        "leg4": {"rotation": {"0": [-24, 0, 0], "0.5": [24, 0, 0], "1.0": [-24, 0, 0]}},
        "head": {"rotation": {"0": [0, 0, 0], "0.25": [1, 3, 0], "0.5": [0, 0, 0], "0.75": [-1, -3, 0], "1.0": [0, 0, 0]}},
        "tail": {"rotation": {"0": [0, 8, 0], "0.5": [0, -8, 0], "1.0": [0, 8, 0]}},
    }),
    "run": clip(0.7, True, {
        "platpyus": {"position": {"0": [0, 0, 0], "0.175": [0, 0.35, 0], "0.35": [0, 0, 0], "0.525": [0, 0.35, 0], "0.7": [0, 0, 0]}},
        "leg1": {"rotation": {"0": [36, 0, 0], "0.35": [-36, 0, 0], "0.7": [36, 0, 0]}},
        "leg3": {"rotation": {"0": [36, 0, 0], "0.35": [-36, 0, 0], "0.7": [36, 0, 0]}},
        "leg2": {"rotation": {"0": [-36, 0, 0], "0.35": [36, 0, 0], "0.7": [-36, 0, 0]}},
        "leg4": {"rotation": {"0": [-36, 0, 0], "0.35": [36, 0, 0], "0.7": [-36, 0, 0]}},
        "tail": {"rotation": {"0": [0, 12, 0], "0.35": [0, -12, 0], "0.7": [0, 12, 0]}},
    }),
}

KANGAROO["clips"] = {
    "idle": clip(4.0, True, {
        "kangaroo": {"position": {"0": [0, 0, 0], "1.0": [0, 0.2, 0], "2.0": [0, 0, 0], "3.0": [0, 0.2, 0], "4.0": [0, 0, 0]}},
        "FULLHEAD2": {"rotation": {"0": [0, 0, 0], "0.8": [1, 8, 0], "1.8": [0, -6, 0], "2.8": [-1, 8, 0], "4.0": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, -8, 0], "2.0": [0, 8, 0], "4.0": [0, -8, 0]}},
        "left_arm": {"rotation": {"0": [0, 0, 0], "2.0": [4, 0, 0], "4.0": [0, 0, 0]}},
        "right_arm": {"rotation": {"0": [0, 0, 0], "2.0": [4, 0, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.0, True, {
        "kangaroo": {"position": {"0": [0, 0, 0], "0.25": [0, 1.2, 0], "0.5": [0, 0, 0], "0.75": [0, 1.2, 0], "1.0": [0, 0, 0]}},
        "left_thigh": {"rotation": {"0": [0, 0, 0], "0.25": [-22, 0, 0], "0.5": [0, 0, 0], "0.75": [-22, 0, 0], "1.0": [0, 0, 0]}},
        "right_thigh": {"rotation": {"0": [0, 0, 0], "0.25": [-22, 0, 0], "0.5": [0, 0, 0], "0.75": [-22, 0, 0], "1.0": [0, 0, 0]}},
        "left_foot": {"rotation": {"0": [0, 0, 0], "0.25": [28, 0, 0], "0.5": [0, 0, 0], "0.75": [28, 0, 0], "1.0": [0, 0, 0]}},
        "right_foot": {"rotation": {"0": [0, 0, 0], "0.25": [28, 0, 0], "0.5": [0, 0, 0], "0.75": [28, 0, 0], "1.0": [0, 0, 0]}},
        "left_arm": {"rotation": {"0": [0, 0, 0], "0.25": [-18, 0, 0], "0.5": [0, 0, 0], "0.75": [-18, 0, 0], "1.0": [0, 0, 0]}},
        "right_arm": {"rotation": {"0": [0, 0, 0], "0.25": [-18, 0, 0], "0.5": [0, 0, 0], "0.75": [-18, 0, 0], "1.0": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, 14, 0], "0.5": [0, -14, 0], "1.0": [0, 14, 0]}},
        "FULLHEAD2": {"rotation": {"0": [0, 0, 0], "0.25": [1, 3, 0], "0.5": [0, 0, 0], "0.75": [-1, -3, 0], "1.0": [0, 0, 0]}},
    }),
    "run": clip(0.7, True, {
        "kangaroo": {"position": {"0": [0, 0, 0], "0.175": [0, 1.8, 0], "0.35": [0, 0, 0], "0.525": [0, 1.8, 0], "0.7": [0, 0, 0]}},
        "left_thigh": {"rotation": {"0": [0, 0, 0], "0.175": [-34, 0, 0], "0.35": [0, 0, 0], "0.525": [-34, 0, 0], "0.7": [0, 0, 0]}},
        "right_thigh": {"rotation": {"0": [0, 0, 0], "0.175": [-34, 0, 0], "0.35": [0, 0, 0], "0.525": [-34, 0, 0], "0.7": [0, 0, 0]}},
        "left_foot": {"rotation": {"0": [0, 0, 0], "0.175": [40, 0, 0], "0.35": [0, 0, 0], "0.525": [40, 0, 0], "0.7": [0, 0, 0]}},
        "right_foot": {"rotation": {"0": [0, 0, 0], "0.175": [40, 0, 0], "0.35": [0, 0, 0], "0.525": [40, 0, 0], "0.7": [0, 0, 0]}},
        "tail2": {"rotation": {"0": [0, 22, 0], "0.35": [0, -22, 0], "0.7": [0, 22, 0]}},
        "left_arm": {"rotation": {"0": [0, 0, 0], "0.175": [-30, 0, 0], "0.7": [0, 0, 0]}},
        "right_arm": {"rotation": {"0": [0, 0, 0], "0.175": [-30, 0, 0], "0.7": [0, 0, 0]}},
    }),
}

EMU["clips"] = {
    "idle": clip(4.0, True, {
        "Emu": {"position": {"0": [0, 0, 0], "1.0": [0, 0.15, 0], "2.0": [0, 0, 0], "3.0": [0, 0.15, 0], "4.0": [0, 0, 0]}},
        "fullhead": {"rotation": {"0": [0, 0, 0], "0.8": [1, 7, 0], "1.8": [0, -5, 0], "2.8": [-1, 8, 0], "4.0": [0, 0, 0]}},
        "body3": {"rotation": {"0": [0, 0, 0], "2.0": [1, 0, 0], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.0, True, {
        "Emu": {"position": {"0": [0, 0, 0], "0.25": [0, 0.2, 0], "0.5": [0, 0, 0], "0.75": [0, 0.2, 0], "1.0": [0, 0, 0]}},
        "back_left_leg": {"rotation": {"0": [28, 0, 0], "0.5": [-28, 0, 0], "1.0": [28, 0, 0]}},
        "back_right_leg": {"rotation": {"0": [-28, 0, 0], "0.5": [28, 0, 0], "1.0": [-28, 0, 0]}},
        "fullhead": {"rotation": {"0": [0, 0, 0], "0.25": [1, 3, 0], "0.5": [0, 0, 0], "0.75": [-1, -3, 0], "1.0": [0, 0, 0]}},
        "body3": {"rotation": {"0": [0, 0, 0], "0.25": [1, 0, 0], "0.5": [0, 0, 0], "0.75": [1, 0, 0], "1.0": [0, 0, 0]}},
    }),
    "run": clip(0.7, True, {
        "Emu": {"position": {"0": [0, 0, 0], "0.175": [0, 0.35, 0], "0.35": [0, 0, 0], "0.525": [0, 0.35, 0], "0.7": [0, 0, 0]}},
        "back_left_leg": {"rotation": {"0": [40, 0, 0], "0.35": [-40, 0, 0], "0.7": [40, 0, 0]}},
        "back_right_leg": {"rotation": {"0": [-40, 0, 0], "0.35": [40, 0, 0], "0.7": [-40, 0, 0]}},
        "fullhead": {"rotation": {"0": [2, 0, 0], "0.35": [0, 0, 0], "0.7": [2, 0, 0]}},
    }),
}

SPIDER["clips"] = {
    "idle": clip(4.0, True, {
        "spider": {"position": {"0": [0, 0, 0], "1.0": [0, 0.12, 0], "2.0": [0, 0, 0], "3.0": [0, 0.12, 0], "4.0": [0, 0, 0]}},
        "head5": {"rotation": {"0": [0, 0, 0], "0.8": [1, 6, 0], "1.8": [0, -4, 0], "2.8": [-1, 6, 0], "4.0": [0, 0, 0]}},
        "body4": {"rotation": {"0": [0, 0, 0], "2.0": [1, 0, 0], "4.0": [0, 0, 0]}},
        "leg5": {"rotation": {"0": [0, 0, 0], "2.0": [3, 0, 2], "4.0": [0, 0, 0]}},
        "leg6": {"rotation": {"0": [0, 0, 0], "2.0": [3, 0, -2], "4.0": [0, 0, 0]}},
    }),
    "walk": clip(1.0, True, {
        "spider": {"position": {"0": [0, 0, 0], "0.25": [0, 0.15, 0], "0.5": [0, 0, 0], "0.75": [0, 0.15, 0], "1.0": [0, 0, 0]}},
        "leg5": {"rotation": {"0": [18, 0, 0], "0.5": [-18, 0, 0], "1.0": [18, 0, 0]}},
        "leg7": {"rotation": {"0": [-18, 0, 0], "0.5": [18, 0, 0], "1.0": [-18, 0, 0]}},
        "leg9": {"rotation": {"0": [18, 0, 0], "0.5": [-18, 0, 0], "1.0": [18, 0, 0]}},
        "leg11": {"rotation": {"0": [-18, 0, 0], "0.5": [18, 0, 0], "1.0": [-18, 0, 0]}},
        "leg6": {"rotation": {"0": [-18, 0, 0], "0.5": [18, 0, 0], "1.0": [-18, 0, 0]}},
        "leg8": {"rotation": {"0": [18, 0, 0], "0.5": [-18, 0, 0], "1.0": [18, 0, 0]}},
        "leg10": {"rotation": {"0": [-18, 0, 0], "0.5": [18, 0, 0], "1.0": [-18, 0, 0]}},
        "leg12": {"rotation": {"0": [18, 0, 0], "0.5": [-18, 0, 0], "1.0": [18, 0, 0]}},
        "head5": {"rotation": {"0": [0, 0, 0], "0.25": [1, 3, 0], "0.5": [0, 0, 0], "0.75": [-1, -3, 0], "1.0": [0, 0, 0]}},
    }),
    "run": clip(0.7, True, {
        "spider": {"position": {"0": [0, 0, 0], "0.175": [0, 0.25, 0], "0.35": [0, 0, 0], "0.525": [0, 0.25, 0], "0.7": [0, 0, 0]}},
        "leg5": {"rotation": {"0": [30, 0, 0], "0.35": [-30, 0, 0], "0.7": [30, 0, 0]}},
        "leg7": {"rotation": {"0": [-30, 0, 0], "0.35": [30, 0, 0], "0.7": [-30, 0, 0]}},
        "leg9": {"rotation": {"0": [30, 0, 0], "0.35": [-30, 0, 0], "0.7": [30, 0, 0]}},
        "leg11": {"rotation": {"0": [-30, 0, 0], "0.35": [30, 0, 0], "0.7": [-30, 0, 0]}},
        "leg6": {"rotation": {"0": [-30, 0, 0], "0.35": [30, 0, 0], "0.7": [-30, 0, 0]}},
        "leg8": {"rotation": {"0": [30, 0, 0], "0.35": [-30, 0, 0], "0.7": [30, 0, 0]}},
        "leg10": {"rotation": {"0": [-30, 0, 0], "0.35": [30, 0, 0], "0.7": [-30, 0, 0]}},
        "leg12": {"rotation": {"0": [30, 0, 0], "0.35": [-30, 0, 0], "0.7": [30, 0, 0]}},
        "head5": {"rotation": {"0": [2, 0, 0], "0.35": [0, 0, 0], "0.7": [2, 0, 0]}},
    }),
    "attack": clip(0.8, False, {
        "spider": {"position": {"0": [0, 0, 0], "0.25": [0, 0.3, -1.0], "0.5": [0, 0.2, -1.5], "0.8": [0, 0, 0]}},
        "head5": {"rotation": {"0": [0, 0, 0], "0.25": [-12, 6, 0], "0.5": [4, -4, 0], "0.8": [0, 0, 0]}},
        "body4": {"rotation": {"0": [0, 0, 0], "0.25": [0, 8, 0], "0.8": [0, 0, 0]}},
        "leg5": {"rotation": {"0": [0, 0, 0], "0.25": [-22, 0, 0], "0.8": [0, 0, 0]}},
        "leg7": {"rotation": {"0": [0, 0, 0], "0.25": [-22, 0, 0], "0.8": [0, 0, 0]}},
        "leg9": {"rotation": {"0": [0, 0, 0], "0.25": [22, 0, 0], "0.8": [0, 0, 0]}},
        "leg11": {"rotation": {"0": [0, 0, 0], "0.25": [22, 0, 0], "0.8": [0, 0, 0]}},
    }),
}

def cube_size(c):
    return [int(round(c["to"][i] - c["from"][i])) for i in range(3)]

def pack_cubes(cubes, size=TEX_SIZE, margin=MARGIN):
    for c in cubes:
        w, h, d = cube_size(c)
        c["size"] = [w, h, d]
        c["footprint"] = [2 * (w + d), h + d]
    ordered = sorted(cubes, key=lambda c: (-c["footprint"][1], -c["footprint"][0], c["name"]))
    x = margin
    y = margin
    row_h = 0
    for c in ordered:
        fw, fh = c["footprint"]
        if x + fw + margin > size:
            x = margin
            y += row_h + margin
            row_h = 0
        if y + fh + margin > size:
            raise RuntimeError(f"Texture atlas overflow: {c['name']}")
        c["uv_offset"] = [x, y]
        x += fw + margin
        row_h = max(row_h, fh)
    return max(y + row_h + margin, 1)

def face_rect(c, face):
    u, v = c["uv_offset"]
    w, h, d = c["size"]
    if face == "north":
        return (u + d, v + d, u + d + w, v + d + h)
    if face == "east":
        return (u, v + d, u + d, v + d + h)
    if face == "south":
        return (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h)
    if face == "west":
        return (u + d + w, v + d, u + 2 * d + w, v + d + h)
    if face == "up":
        return (u + d, v, u + d + w, v + d)
    if face == "down":
        return (u + d + w, v, u + d + 2 * w, v + d)
    raise ValueError(face)

def norm_rect(rect):
    x0, y0, x1, y1 = rect
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

def shade(value, amount):
    if isinstance(value, str):
        value = hex_rgb(value)
    return tuple(max(0, min(255, v + amount)) for v in value)

def sub(rect, fx0, fy0, fx1, fy1):
    x0, y0, x1, y1 = norm_rect(rect)
    w = x1 - x0
    h = y1 - y0
    return (
        int(x0 + fx0 * w), int(y0 + fy0 * h),
        max(int(x0 + fx1 * w), int(x0 + fx0 * w) + 1),
        max(int(y0 + fy1 * h), int(y0 + fy0 * h) + 1),
    )

def fill(draw, rect, color, rng=None, noise=0.15):
    x0, y0, x1, y1 = norm_rect(rect)
    draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill=color)
    if rng is None or x1 - x0 <= 2 or y1 - y0 <= 2:
        return
    base = hex_rgb(color) if isinstance(color, str) else color
    area = (x1 - x0) * (y1 - y0)
    for _ in range(max(1, int(area * noise * 0.18))):
        px = rng.randrange(x0, x1)
        py = rng.randrange(y0, y1)
        draw.point((px, py), fill=shade(base, rng.choice([-18, -10, 10, 18])))

def eye(draw, rect, cx, cy, rw=2, rh=2, iris="#111111", glint="#F2EEE4"):
    x0, y0, x1, y1 = norm_rect(rect)
    w = x1 - x0
    h = y1 - y0
    px = x0 + int(cx * w)
    py = y0 + int(cy * h)
    draw.rectangle((px, py, px + rw - 1, py + rh - 1), fill=iris)
    if rw >= 2 and rh >= 2:
        draw.point((px, py), fill=glint)

def diamond(draw, cx, cy, rx, ry, color):
    draw.polygon([(cx, cy - ry), (cx + rx, cy), (cx, cy + ry), (cx - rx, cy)], fill=color)

def paint_bear(c, draw, rng):
    role = c["role"]
    name = c["name"]
    black = c.get("mob") == "blackbear"
    fur = "#24211E" if black else "#7A5A3E"
    if name == "shoulder":
        fur = "#2E2A25" if black else "#8A6848"
    for face in FACES:
        rect = face_rect(c, face)
        base = fur
        if face == "up":
            base = shade(fur, 18)
        elif face == "down":
            base = "#151311" if black else "#523A28"
        if role == "bear_head":
            base = ("#27231F" if black else "#7E5E42") if face not in ("up", "down") else (("#34302B" if black else "#8D6D4C") if face == "up" else ("#151311" if black else "#4A3323"))
        elif role == "bear_snout":
            base = "#B08A63" if black else "#C9A77D"
            if face == "down":
                base = "#7E6248" if black else "#967655"
        elif role == "bear_nose":
            base = "#211712"
        elif role == "bear_ear":
            base = "#1B1815" if black else "#6A4C34"
        elif role == "bear_leg":
            base = ("#1E1B18" if black else "#5E432E") if face != "down" else ("#11100E" if black else "#3A271B")
        elif role == "bear_paw":
            base = ("#171512" if black else "#4E3725") if face != "down" else ("#0E0D0C" if black else "#2D1E14")
        elif role == "bear_tail":
            base = "#1C1916" if black else "#654934"
        fill(draw, rect, base, rng, 0.24)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role in ("bear_body", "bear_leg", "bear_tail") and face in ("east", "west", "north", "south"):
            for i in range(max(4, w // 3)):
                px = x0 + 1 + rng.randrange(max(1, w - 2))
                py = y0 + 1 + rng.randrange(max(1, h - 3))
                length = rng.randrange(2, max(3, h // 2 + 2))
                draw.line((px, py, px + rng.choice([0, 1, -1]), min(y1 - 1, py + length)), fill=shade(base, rng.choice([-18, -10, 12, 20])))
            if face in ("east", "west"):
                draw.rectangle((x0, y1 - max(2, h // 5), x1 - 1, y1 - 1), fill=shade(base, 12))
        if role == "bear_head" and face == "north":
            fill(draw, sub(rect, 0.18, 0.06, 0.82, 0.3), "#3A332C" if black else "#8C6A49", rng, 0.04)
            eye(draw, rect, 0.28, 0.37, 2, 2, "#17110D", "#F2E6C9")
            eye(draw, rect, 0.72, 0.37, 2, 2, "#17110D", "#F2E6C9")
            draw.line((x0 + 2, y0 + int(h * 0.24), x0 + int(w * 0.4), y0 + int(h * 0.27)), fill="#0F0D0B" if black else "#4D3524")
            draw.line((x1 - 2, y0 + int(h * 0.24), x0 + int(w * 0.6), y0 + int(h * 0.27)), fill="#0F0D0B" if black else "#4D3524")
            draw.rectangle(sub(rect, 0.44, 0.58, 0.56, 0.72), fill="#B38D64")
        if role == "bear_snout" and face == "north":
            draw.line((x0 + 2, y1 - 4, x1 - 2, y1 - 4), fill="#4D3524")
            draw.line((x0 + int(w * 0.5), y1 - 4, x0 + int(w * 0.5), y1 - 2), fill="#4D3524")
            draw.rectangle(sub(rect, 0.3, 0.12, 0.41, 0.32), fill="#3A271B")
            draw.rectangle(sub(rect, 0.59, 0.12, 0.7, 0.32), fill="#3A271B")
        if role == "bear_ear" and face == "north":
            fill(draw, sub(rect, 0.2, 0.2, 0.8, 0.8), "#3A271B", rng, 0)
        if role == "bear_paw" and face in ("north", "south"):
            for i in range(3):
                px = x0 + int((i + 0.7) * w / 3)
                draw.rectangle((px, y1 - 3, px + 1, y1 - 1), fill="#E7D9BE")
        if role == "bear_tail" and face in ("north", "south"):
            fill(draw, sub(rect, 0.2, 0.55, 0.8, 1.0), "#4E3725", rng, 0.04)

def paint_tiger(c, draw, rng):
    role = c["role"]
    lion = c.get("mob") in ("lion", "lioness")
    for face in FACES:
        rect = face_rect(c, face)
        if role == "lion_mane":
            base = "#5C3A22" if face == "up" else "#6B4428"
            fill(draw, rect, base, rng, 0.2)
            x0, y0, x1, y1 = norm_rect(rect)
            for i in range(max(3, (x1 - x0) // 3)):
                px = x0 + 1 + rng.randrange(max(1, x1 - x0 - 1))
                py = y0 + 1 + rng.randrange(max(1, y1 - y0 - 2))
                draw.line((px, py, px + rng.choice([0, 1, -1]), min(y1 - 1, py + rng.randrange(2, max(3, y1 - py)))), fill=shade(base, rng.choice([-20, -10, 14, 24])))
            continue
        if role == "lion_tuft":
            fill(draw, rect, "#4C2E1B" if face != "up" else "#5C3A22", rng, 0.25)
            continue
        base = "#C7985A" if lion else "#C97A2B"
        if face == "up":
            base = "#D3A566" if lion else "#D88A36"
        elif face == "down":
            base = "#E8D6B8" if lion else "#F0E2C8"
        if role == "tiger_head":
            base = ("#D0A264" if lion else "#D08131") if face not in ("up", "down") else (("#D9B072" if lion else "#E3A050") if face == "up" else ("#E8D6B8" if lion else "#F0E2C8"))
        elif role == "tiger_snout":
            base = "#F1E4C8"
        elif role == "tiger_nose":
            base = "#8B5A4A" if lion else "#9E5D56"
        elif role == "tiger_ear":
            base = "#B98748" if lion else "#C97A2B"
        elif role == "tiger_leg":
            base = ("#C7985A" if lion else "#C97A2B") if face != "down" else "#EADCC2"
        elif role == "tiger_paw":
            base = "#F1E4C8" if face != "down" else "#D9C9AD"
        elif role in ("tiger_tail", "tiger_tail_tip"):
            base = "#B98A4A" if lion else "#C57326"
        fill(draw, rect, base, rng, 0.16)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role in ("tiger_body", "tiger_head", "tiger_leg", "tiger_tail", "tiger_tail_tip"):
            if role == "tiger_body" and face in ("east", "west") and not lion:
                for i in range(7):
                    px = x0 + int((i + 0.15) * w / 7)
                    top = y0 + 1 + (i % 2)
                    bottom = y0 + int(h * (0.52 + 0.09 * (i % 3)))
                    draw.line((px, top, px, bottom), fill="#1F1A17")
                    if i % 2 == 0:
                        draw.line((px, y0 + int(h * 0.68), px + 1, y1 - 2), fill="#1F1A17")
            if role == "tiger_body" and face == "up" and not lion:
                for i in range(5):
                    py = y0 + int((i + 0.45) * h / 5)
                    draw.line((x0 + 1, py, x1 - 2, py + rng.choice([-1, 0, 1])), fill="#1F1A17")
            if role == "tiger_body" and face in ("north", "south") and not lion:
                for i in range(3):
                    px = x0 + int((i + 0.5) * w / 3)
                    draw.line((px, y0 + 1, px, y0 + int(h * 0.3)), fill="#1F1A17")
            if role == "tiger_head" and face == "north":
                fill(draw, sub(rect, 0.0, 0.5, 1.0, 1.0), "#F3E7D0", rng, 0.04)
                eye(draw, rect, 0.27, 0.35, 2, 2, "#E8C547")
                eye(draw, rect, 0.73, 0.35, 2, 2, "#E8C547")
                draw.rectangle(sub(rect, 0.49, 0.35, 0.51, 0.39), fill="#1F1A17")
                if not lion:
                    draw.line((x0 + 1, y0 + 2, x0 + int(w * 0.32), y0 + 4), fill="#1F1A17")
                    draw.line((x1 - 1, y0 + 2, x0 + int(w * 0.68), y0 + 4), fill="#1F1A17")
                    draw.line((x0 + int(w * 0.42), y0, x0 + int(w * 0.46), y0 + 4), fill="#1F1A17")
                    draw.line((x0 + int(w * 0.58), y0, x0 + int(w * 0.54), y0 + 4), fill="#1F1A17")
            if role == "tiger_head" and face in ("east", "west"):
                if not lion:
                    for i in range(4):
                        px = x0 + int((i + 0.35) * w / 4)
                        draw.line((px, y0 + 1, px, y0 + 3 + (i % 2)), fill="#1F1A17")
                fill(draw, sub(rect, 0.0, 0.68, 1.0, 1.0), "#F3E7D0", rng, 0.03)
            if role == "tiger_snout" and face == "north":
                draw.rectangle(sub(rect, 0.4, 0.05, 0.6, 0.42), fill="#9E5D56")
                draw.line((x0 + 2, y1 - 3, x0 + int(w * 0.5), y1 - 1), fill="#5B3429")
                draw.line((x1 - 2, y1 - 3, x0 + int(w * 0.5), y1 - 1), fill="#5B3429")
            if role == "tiger_ear" and face == "north":
                fill(draw, sub(rect, 0.24, 0.22, 0.76, 0.76), "#3A2921", rng, 0)
            if role == "tiger_leg" and face in ("north", "south", "east", "west") and not lion:
                for pyf in (0.3, 0.55, 0.78):
                    draw.line((x0, y0 + int(h * pyf), x1 - 1, y0 + int(h * pyf)), fill="#1F1A17")
            if role == "tiger_paw" and face in ("north", "south"):
                draw.line((x0 + 1, y1 - 2, x1 - 2, y1 - 2), fill="#C8B696")
            if role in ("tiger_tail", "tiger_tail_tip") and face in ("east", "west", "up", "down") and not lion:
                for i in range(3):
                    px = x0 + int((i + 0.4) * w / 3)
                    draw.rectangle((px, y0, px + 1, y1 - 1), fill="#1F1A17")
            if role == "tiger_tail_tip" and not lion:
                fill(draw, rect, "#1F1A17", rng, 0.02)

def paint_monkey(c, draw, rng):
    role = c["role"]
    for face in FACES:
        rect = face_rect(c, face)
        base = "#4A3324"
        if face == "up":
            base = "#5B402D"
        elif face == "down":
            base = "#2E2016"
        if role == "monkey_head":
            base = "#4A3324" if face not in ("up", "down") else ("#5B402D" if face == "up" else "#2E2016")
        elif role == "monkey_muzzle":
            base = "#E8D3AF"
        elif role == "monkey_ear":
            base = "#B59066"
        elif role in ("monkey_arm", "monkey_leg"):
            base = "#3A271B" if face != "down" else "#241810"
        elif role in ("monkey_hand", "monkey_foot"):
            base = "#8E6A48"
        elif role in ("monkey_tail", "monkey_tail_tip"):
            base = "#3A271B"
        fill(draw, rect, base, rng, 0.18)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role == "monkey_body" and face == "north":
            fill(draw, sub(rect, 0.08, 0.1, 0.92, 0.72), "#D8C3A1", rng, 0.05)
            fill(draw, sub(rect, 0.2, 0.72, 0.8, 1.0), "#6E4B33", rng, 0.05)
        if role == "monkey_head" and face == "north":
            fill(draw, sub(rect, 0.12, 0.28, 0.88, 0.98), "#E8D3AF", rng, 0.04)
            fill(draw, sub(rect, 0.0, 0.0, 1.0, 0.26), "#2F2118", rng, 0.07)
            eye(draw, rect, 0.29, 0.4, 2, 3, "#17110D", "#F8F1DF")
            eye(draw, rect, 0.71, 0.4, 2, 3, "#17110D", "#F8F1DF")
            draw.line((x0 + 3, y0 + 3, x0 + int(w * 0.36), y0 + 5), fill="#2F2118")
            draw.line((x1 - 3, y0 + 3, x0 + int(w * 0.64), y0 + 5), fill="#2F2118")
        if role == "monkey_head" and face in ("east", "west"):
            fill(draw, sub(rect, 0.0, 0.62, 1.0, 1.0), "#E8D3AF", rng, 0.03)
        if role == "monkey_muzzle" and face == "north":
            draw.rectangle(sub(rect, 0.3, 0.08, 0.4, 0.34), fill="#3A271B")
            draw.rectangle(sub(rect, 0.6, 0.08, 0.7, 0.34), fill="#3A271B")
            draw.line((x0 + 2, y1 - 4, x0 + int(w * 0.5), y1 - 2), fill="#6B4B33")
            draw.line((x1 - 2, y1 - 4, x0 + int(w * 0.5), y1 - 2), fill="#6B4B33")
        if role == "monkey_ear" and face in ("north", "south"):
            fill(draw, sub(rect, 0.2, 0.16, 0.8, 0.84), "#7A5A3E", rng, 0)
        if role == "monkey_arm" and face == "north":
            fill(draw, sub(rect, 0.0, 0.0, 1.0, 0.3), "#5B402D", rng, 0.04)
        if role == "monkey_tail_tip" and face in ("north", "south", "up", "down"):
            fill(draw, rect, "#2B1E15", rng, 0.02)

def paint_penguin(c, draw, rng):
    role = c["role"]
    for face in FACES:
        rect = face_rect(c, face)
        base = "#1B2630"
        if role == "penguin_body":
            if face == "north":
                fill(draw, rect, "#F2EFE5", rng, 0.05)
                x0, y0, x1, y1 = norm_rect(rect)
                side = max(1, (x1 - x0) // 7)
                draw.rectangle((x0, y0, x0 + side, y1 - 1), fill="#1B2630")
                draw.rectangle((x1 - side, y0, x1 - 1, y1 - 1), fill="#1B2630")
                if c["name"] == "upper_body":
                    draw.rectangle((x0, y0, x1 - 1, y0 + max(2, (y1 - y0) // 6)), fill="#E8B53C")
            else:
                fill(draw, rect, base, rng, 0.1)
            continue
        if role == "penguin_head":
            if face == "north":
                fill(draw, rect, base, rng, 0.08)
                fill(draw, sub(rect, 0.06, 0.38, 0.94, 0.99), "#F2EFE5", rng, 0.03)
                fill(draw, sub(rect, 0.0, 0.28, 0.17, 0.8), "#E8B53C", rng, 0)
                fill(draw, sub(rect, 0.83, 0.28, 1.0, 0.8), "#E8B53C", rng, 0)
                eye(draw, rect, 0.3, 0.44, 2, 2, "#111820", "#FFFFFF")
                eye(draw, rect, 0.7, 0.44, 2, 2, "#111820", "#FFFFFF")
            elif face in ("east", "west"):
                fill(draw, rect, base, rng, 0.08)
                fill(draw, sub(rect, 0.0, 0.5, 1.0, 0.86), "#E8B53C", rng, 0.02)
            else:
                fill(draw, rect, base, rng, 0.08)
            continue
        if role == "penguin_beak":
            fill(draw, rect, "#E58A2A", rng, 0.05)
            if face in ("north", "south"):
                x0, y0, x1, y1 = norm_rect(rect)
                draw.line((x0, y1 - 2, x1 - 1, y1 - 2), fill="#B8641D")
            continue
        if role == "penguin_foot":
            fill(draw, rect, "#D9821F", rng, 0.08)
            if face in ("north", "south"):
                x0, y0, x1, y1 = norm_rect(rect)
                for i in range(3):
                    px = x0 + int((i + 0.55) * (x1 - x0) / 3)
                    draw.line((px, y1 - 3, px, y1 - 1), fill="#8B4B12")
            continue
        if role == "penguin_flipper":
            fill(draw, rect, "#22303D" if face != "down" else "#141E27", rng, 0.1)
            if face in ("north", "south"):
                x0, y0, x1, y1 = norm_rect(rect)
                draw.line((x0 + 1, y0 + 2, x1 - 2, y1 - 2), fill="#3D5264")
            continue
        fill(draw, rect, base if face != "down" else "#131A20", rng, 0.1)

def paint_snake(c, draw, rng):
    role = c["role"]
    dark = "#2F5B33"
    mid = "#467B43"
    light = "#8FBF74"
    pale = "#C8E3A6"
    cream = "#D7C89A"
    for face in FACES:
        rect = face_rect(c, face)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role in ("snake_body", "snake_tail", "snake_tail_tip"):
            base = dark
            if face == "up":
                base = mid
            elif face == "down":
                base = "#A7B97E"
            fill(draw, rect, base, rng, 0.18)
            if face == "up":
                for _ in range(max(1, w // 5)):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 2))
                    rx = max(1, rng.randrange(1, max(2, w // 5)))
                    ry = max(1, rng.randrange(1, max(2, h // 5)))
                    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=light)
            elif face in ("east", "west"):
                for _ in range(max(1, w // 6)):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 3))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 1), min(y1 - 1, cy + 2)), fill=pale if rng.random() < 0.5 else light)
                draw.line((x0, y0 + int(h * 0.78), x1 - 1, y0 + int(h * 0.78)), fill="#8FA768")
            elif face in ("north", "south"):
                for _ in range(max(1, w // 5)):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 3))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 1), min(y1 - 1, cy + 1)), fill=light)
            if role == "snake_tail_tip":
                for _ in range(3):
                    draw.point((x0 + rng.randrange(w), y0 + rng.randrange(h)), fill="#1D3A22")
            continue
        if role == "snake_head":
            fill(draw, rect, mid if face == "up" else dark, rng, 0.12)
            if face == "north":
                fill(draw, sub(rect, 0.04, 0.62, 0.96, 0.96), pale, rng, 0.03)
                eye(draw, rect, 0.27, 0.36, 2, 2, "#E8C547")
                eye(draw, rect, 0.73, 0.36, 2, 2, "#E8C547")
                draw.rectangle(sub(rect, 0.295, 0.34, 0.305, 0.5), fill="#111111")
                draw.rectangle(sub(rect, 0.695, 0.34, 0.705, 0.5), fill="#111111")
                draw.rectangle(sub(rect, 0.28, 0.12, 0.34, 0.18), fill="#1D3A22")
                draw.rectangle(sub(rect, 0.66, 0.12, 0.72, 0.18), fill="#1D3A22")
            elif face in ("east", "west"):
                for _ in range(3):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 3))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 1), min(y1 - 1, cy + 1)), fill=pale)
                draw.line((x0, y1 - 2, x1 - 1, y1 - 2), fill=pale)
            elif face == "up":
                for _ in range(2):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 2))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 2), min(y1 - 1, cy + 1)), fill=light)
            continue
        if role == "snake_jaw":
            fill(draw, rect, cream if face != "down" else "#B9A878", rng, 0.05)
            if face in ("north", "south"):
                draw.line((x0 + 1, y0 + 1, x1 - 2, y0 + 1), fill="#8B744D")
            continue
        if role == "snake_tongue":
            fill(draw, rect, "#C84854", rng, 0.0)
            continue
        fill(draw, rect, dark, rng, 0.12)

def paint_crocodile(c, draw, rng):
    role = c["role"]
    for face in FACES:
        rect = face_rect(c, face)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role == "croc_body":
            base = "#C9B98B" if face == "down" else ("#4C6641" if face == "up" else "#3F5638")
            fill(draw, rect, base, rng, 0.18)
            if face == "down":
                for i in range(1, 4):
                    py = y0 + int(h * i / 4)
                    draw.line((x0 + 1, py, x1 - 2, py), fill="#B5A577")
            elif face in ("east", "west", "north", "south"):
                for _ in range(max(2, w // 4)):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 2))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 1), min(y1 - 1, cy + 2)), fill=shade("#3F5638", rng.choice([-18, 15, 22])))
            continue
        if role == "croc_ridge":
            fill(draw, rect, "#2E4129" if face != "up" else "#3A5132", rng, 0.14)
            if face in ("up", "east", "west"):
                for i in range(max(2, w // 3)):
                    px = x0 + 1 + int(i * (w - 2) / max(1, (w // 3)))
                    draw.rectangle((px, y0, min(x1 - 1, px + 1), y1 - 1), fill="#23321F")
            continue
        if role == "croc_head":
            fill(draw, rect, "#4C6641" if face == "up" else "#425C3B", rng, 0.14)
            if face in ("up", "north"):
                eye(draw, rect, 0.28, 0.4, 2, 2, "#E8C547")
                eye(draw, rect, 0.72, 0.4, 2, 2, "#E8C547")
                draw.rectangle(sub(rect, 0.29, 0.35, 0.305, 0.55), fill="#111111")
                draw.rectangle(sub(rect, 0.695, 0.35, 0.71, 0.55), fill="#111111")
            if face in ("east", "west"):
                for _ in range(4):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 2))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 1), min(y1 - 1, cy + 1)), fill="#32452E")
            continue
        if role == "croc_snout":
            fill(draw, rect, "#415A3A" if face != "down" else "#B9A879", rng, 0.16)
            if face == "north":
                draw.rectangle(sub(rect, 0.22, 0.18, 0.3, 0.32), fill="#1B2418")
                draw.rectangle(sub(rect, 0.7, 0.18, 0.78, 0.32), fill="#1B2418")
            if face in ("east", "west"):
                for _ in range(3):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 2))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 1), min(y1 - 1, cy + 1)), fill="#2F442B")
            continue
        if role == "croc_jaw":
            fill(draw, rect, "#C9B98B" if face != "down" else "#A9976B", rng, 0.08)
            if face == "north":
                draw.line((x0 + 1, y0 + 1, x1 - 2, y0 + 1), fill="#6C5E3F")
                for i in range(4):
                    px = x0 + 2 + int(i * (w - 4) / 4)
                    draw.point((px, y0 + 1), fill="#F2EBD8")
            continue
        if role == "croc_leg":
            fill(draw, rect, "#3A4E33" if face != "down" else "#263421", rng, 0.14)
            if face in ("north", "south"):
                for i in range(3):
                    px = x0 + int((i + 0.55) * w / 3)
                    draw.rectangle((px, y1 - 2, px + 1, y1 - 1), fill="#D8CBA5")
            continue
        fill(draw, rect, "#3F5638", rng, 0.1)

def paint_shark(c, draw, rng):
    role = c["role"]
    for face in FACES:
        rect = face_rect(c, face)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role in ("shark_body", "shark_head", "shark_snout"):
            top = "#536A75" if role != "shark_head" else "#5B737D"
            belly = "#E8EEF0"
            if face == "up":
                fill(draw, rect, top, rng, 0.12)
            elif face == "down":
                fill(draw, rect, belly, rng, 0.06)
            elif face in ("east", "west"):
                split = y0 + max(2, int(h * 0.55))
                fill(draw, (x0, y0, x1, split), top, rng, 0.12)
                fill(draw, (x0, split, x1, y1), belly, rng, 0.05)
                draw.line((x0, split, x1 - 1, split), fill="#BEC9CC")
                if role == "shark_body" and not c["name"].startswith("tail"):
                    for i in range(3):
                        gx = x0 + int(w * (0.58 + i * 0.06))
                        draw.line((gx, y0 + int(h * 0.35), gx, y0 + int(h * 0.62)), fill="#31444D")
            else:
                split = y0 + max(2, int(h * 0.6))
                fill(draw, (x0, y0, x1, split), top, rng, 0.1)
                fill(draw, (x0, split, x1, y1), belly, rng, 0.05)
            if role == "shark_head" and face in ("east", "west"):
                eye(draw, rect, 0.25, 0.36, 2, 2, "#0B0D0E", "#E8EEF0")
            if role == "shark_snout" and face == "north":
                draw.rectangle(sub(rect, 0.28, 0.2, 0.36, 0.3), fill="#26333A")
                draw.rectangle(sub(rect, 0.64, 0.2, 0.72, 0.3), fill="#26333A")
            continue
        if role == "shark_jaw":
            fill(draw, rect, "#DDE4E5" if face != "down" else "#B6C2C5", rng, 0.05)
            if face == "north":
                draw.rectangle((x0 + 1, y0 + 1, x1 - 2, max(y0 + 2, y1 - 2)), fill="#6B2630")
                for i in range(5):
                    px = x0 + 2 + int(i * (w - 4) / 5)
                    draw.point((px, y0 + 1), fill="#FFFFFF")
                    draw.point((px, y1 - 2), fill="#FFFFFF")
            continue
        if role == "shark_fin":
            fill(draw, rect, "#465D68" if face != "up" else "#5A737E", rng, 0.1)
            if face in ("east", "west"):
                draw.line((x0, y1 - 2, x1 - 1, y1 - 2), fill="#7F969E")
            continue
        fill(draw, rect, "#536A75", rng, 0.1)

def paint_deer(c, draw, rng):
    role = c["role"]
    for face in FACES:
        rect = face_rect(c, face)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role in ("deer_body", "deer_neck"):
            base = "#8B5A3C"
            if face == "up":
                base = "#9B6B45"
            elif face == "down":
                base = "#D9C2A3"
            fill(draw, rect, base, rng, 0.14)
            if face in ("east", "west", "up"):
                for _ in range(max(2, w // 4)):
                    cx = x0 + 1 + rng.randrange(max(1, w - 2))
                    cy = y0 + 1 + rng.randrange(max(1, h - 2))
                    draw.rectangle((cx, cy, min(x1 - 1, cx + 1), min(y1 - 1, cy + 1)), fill="#D8C2A0")
            if role == "deer_body" and face in ("south", "down"):
                fill(draw, sub(rect, 0.15, 0.55, 0.85, 1.0), "#E8D8BE", rng, 0.04)
            continue
        if role == "deer_head":
            base = "#9B6B45" if face == "up" else "#8B5A3C"
            fill(draw, rect, base, rng, 0.12)
            if face == "north":
                fill(draw, sub(rect, 0.1, 0.54, 0.9, 1.0), "#D9C2A3", rng, 0.04)
                eye(draw, rect, 0.3, 0.4, 2, 2, "#17110D", "#F2E8D5")
                eye(draw, rect, 0.7, 0.4, 2, 2, "#17110D", "#F2E8D5")
            continue
        if role == "deer_snout":
            fill(draw, rect, "#D9C2A3", rng, 0.06)
            if face == "north":
                draw.rectangle(sub(rect, 0.4, 0.1, 0.6, 0.5), fill="#211712")
                draw.line((x0 + 1, y1 - 2, x1 - 2, y1 - 2), fill="#6B4B33")
            continue
        if role == "deer_ear":
            fill(draw, rect, "#8B5A3C" if face != "down" else "#6B4428", rng, 0.12)
            if face == "north":
                fill(draw, sub(rect, 0.22, 0.2, 0.78, 0.8), "#C98F7A", rng, 0.04)
            continue
        if role == "deer_antler":
            fill(draw, rect, "#D7C4A0" if face != "down" else "#B8A57F", rng, 0.08)
            if face in ("north", "south"):
                draw.rectangle((x0, y0, x1 - 1, y0 + max(1, h // 4)), fill="#6B563A")
            continue
        if role == "deer_leg":
            fill(draw, rect, "#7A4E33" if face != "down" else "#5E3B26", rng, 0.12)
            if face in ("north", "south", "east", "west"):
                fill(draw, sub(rect, 0.0, 0.86, 1.0, 1.0), "#2B211A", rng, 0)
            continue
        if role == "deer_tail":
            fill(draw, rect, "#8B5A3C" if face != "down" else "#E8D8BE", rng, 0.1)
            if face in ("east", "west"):
                fill(draw, rect, "#E8D8BE", rng, 0.04)
            continue
        fill(draw, rect, "#8B5A3C", rng, 0.1)

def paint_giraffe(c, draw, rng):
    role = c["role"]
    for face in FACES:
        rect = face_rect(c, face)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        if role in ("giraffe_body", "giraffe_head", "giraffe_leg", "giraffe_tail"):
            base = "#D8B04A"
            if face == "up":
                base = "#E2C45D"
            elif face == "down":
                base = "#C49A34"
            if role == "giraffe_head":
                base = "#DDB652" if face != "down" else "#C49A34"
            if role == "giraffe_leg":
                base = "#D8B04A"
            fill(draw, rect, base, rng, 0.1)
            if role != "giraffe_tail" or face != "down":
                for _ in range(max(3, (w * h) // 60)):
                    px = x0 + 1 + rng.randrange(max(1, w - 3))
                    py = y0 + 1 + rng.randrange(max(1, h - 3))
                    pw = min(x1 - 1 - px, rng.randrange(3, max(4, w // 3 + 4)))
                    ph = min(y1 - 1 - py, rng.randrange(3, max(4, h // 3 + 4)))
                    draw.rectangle((px, py, px + pw, py + ph), fill="#8B5A2B")
                    if rng.random() < 0.55:
                        draw.point((px + pw, py), fill="#8B5A2B")
                        draw.point((px, py + ph), fill="#8B5A2B")
            if role == "giraffe_leg":
                fill(draw, sub(rect, 0.0, 0.88, 1.0, 1.0), "#2B211A", rng, 0)
            if role == "giraffe_tail" and face in ("north", "south"):
                fill(draw, rect, "#8B5A2B", rng, 0.02)
            if role == "giraffe_head" and face == "north":
                eye(draw, rect, 0.3, 0.38, 2, 2, "#17110D", "#F2E6C9")
                eye(draw, rect, 0.7, 0.38, 2, 2, "#17110D", "#F2E6C9")
            continue
        if role == "giraffe_mane":
            fill(draw, rect, "#5C3A1E", rng, 0.2)
            for i in range(max(2, h // 3)):
                py = y0 + rng.randrange(max(1, h))
                draw.line((x0, py, x1 - 1, py), fill="#3B2412")
            continue
        if role == "giraffe_snout":
            fill(draw, rect, "#EADCB8", rng, 0.05)
            if face == "north":
                draw.line((x0 + 1, y1 - 2, x1 - 2, y1 - 2), fill="#8B744D")
            continue
        if role == "giraffe_nose":
            fill(draw, rect, "#2B1E15", rng, 0)
            continue
        if role == "giraffe_ear":
            fill(draw, rect, "#D8B04A" if face != "down" else "#B68E35", rng, 0.08)
            if face == "north":
                fill(draw, sub(rect, 0.22, 0.2, 0.78, 0.8), "#C98F7A", rng, 0.03)
            continue
        if role == "giraffe_ossicone":
            fill(draw, rect, "#6B4428" if face != "up" else "#7B5330", rng, 0.08)
            if face in ("north", "south", "east", "west"):
                fill(draw, sub(rect, 0.0, 0.0, 1.0, 0.18), "#2B1E15", rng, 0)
            continue
        if role == "giraffe_tail_tip":
            fill(draw, rect, "#4A2D16", rng, 0.1)
            continue
        fill(draw, rect, "#D8B04A", rng, 0.1)

def paint_raccoon(c, draw, rng):
    role = c["role"]
    for face in FACES:
        rect = face_rect(c, face)
        x0, y0, x1, y1 = norm_rect(rect)
        w = x1 - x0
        h = y1 - y0
        base = "#8D8F8B"
        if role == "raccoon_body":
            if face == "up":
                base = "#9A9C97"
            elif face == "down":
                base = "#6A6C68"
            fill(draw, rect, base, rng, 0.14)
            if face == "north":
                fill(draw, sub(rect, 0.18, 0.45, 0.82, 0.95), "#B2B4AE", rng, 0.05)
            continue
        if role == "raccoon_head":
            base = "#8D8F8B" if face != "down" else "#6A6C68"
            fill(draw, rect, base, rng, 0.12)
            if face == "north":
                draw.rectangle((x0, y0 + int(h * 0.28), x1 - 1, y0 + int(h * 0.55)), fill="#262726")
                fill(draw, sub(rect, 0.18, 0.55, 0.82, 1.0), "#E8E4DA", rng, 0.03)
                eye(draw, rect, 0.3, 0.4, 2, 2, "#C9A24A", "#FFFFFF")
                eye(draw, rect, 0.7, 0.4, 2, 2, "#C9A24A", "#FFFFFF")
                draw.line((x0 + 1, y0 + int(h * 0.2), x0 + int(w * 0.42), y0 + int(h * 0.24)), fill="#E8E4DA")
                draw.line((x1 - 1, y0 + int(h * 0.2), x0 + int(w * 0.58), y0 + int(h * 0.24)), fill="#E8E4DA")
            continue
        if role == "raccoon_cheek":
            fill(draw, rect, "#B8B2A5", rng, 0.08)
            if face == "north":
                fill(draw, sub(rect, 0.0, 0.0, 1.0, 0.4), "#262726", rng, 0)
            continue
        if role == "raccoon_snout":
            fill(draw, rect, "#E8E4DA", rng, 0.04)
            if face == "north":
                draw.line((x0 + 1, y1 - 3, x0 + int(w * 0.5), y1 - 1), fill="#4A4A46")
                draw.line((x1 - 2, y1 - 3, x0 + int(w * 0.5), y1 - 1), fill="#4A4A46")
            continue
        if role == "raccoon_nose":
            fill(draw, rect, "#211F1D", rng, 0)
            continue
        if role == "raccoon_ear":
            fill(draw, rect, "#7D807B" if face != "down" else "#5A5C58", rng, 0.08)
            if face == "north":
                fill(draw, sub(rect, 0.2, 0.2, 0.8, 0.8), "#C98F7A", rng, 0.03)
            continue
        if role == "raccoon_leg":
            fill(draw, rect, "#4A4B47" if face != "down" else "#353632", rng, 0.1)
            continue
        if role == "raccoon_paw":
            fill(draw, rect, "#2B2C2B", rng, 0.05)
            continue
        if role in ("raccoon_tail", "raccoon_tail_tip"):
            fill(draw, rect, "#C9C3B5", rng, 0.08)
            if face in ("east", "west", "up", "down"):
                draw.rectangle((x0, y0, x0 + max(2, int(w * 0.45)), y1 - 1), fill="#2B2B28")
            elif face in ("north", "south"):
                draw.rectangle((x0, y0, x1 - 1, max(y0 + 2, y0 + h // 2)), fill="#2B2B28")
            if role == "raccoon_tail_tip":
                fill(draw, rect, "#2B2B28", rng, 0.04)
            continue
        fill(draw, rect, base, rng, 0.1)

def build_textures():
    TEXTURES.mkdir(parents=True, exist_ok=True)
    for mob in MOBS:
        if "import" in mob:
            continue
        tex_size = mob.get("texture_size", TEX_SIZE)
        atlas_h = pack_cubes(mob["cubes"], size=tex_size)
        img = Image.new("RGBA", (tex_size, tex_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        rng = random.Random(f"neosmoremobs-{mob['id']}")
        painter = {
            "bear": paint_bear,
            "blackbear": paint_bear,
            "tiger": paint_tiger,
            "lion": paint_tiger,
            "lioness": paint_tiger,
            "giraffe": paint_giraffe,
            "raccoon": paint_raccoon,
            "monkey": paint_monkey,
            "penguin": paint_penguin,
            "snake": paint_snake,
            "crocodile": paint_crocodile,
            "shark": paint_shark,
            "deer": paint_deer,
        }[mob["id"]]
        for cube in mob["cubes"]:
            cube["mob"] = mob["id"]
            painter(cube, draw, rng)
        path = TEXTURES / f"{mob['id']}.png"
        img.save(path)
        mob["texture_path"] = str(path)
        mob["atlas_height"] = atlas_h

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

def build_icon():
    size = 512
    img = Image.new("RGBA", (size, size), "#14221E")
    d = ImageDraw.Draw(img)
    for i in range(size):
        t = i / size
        d.line((0, i, size, i), fill=("#1C332B" if (i // 24) % 2 == 0 else "#193028"))
    d.rounded_rectangle((22, 22, size - 22, size - 22), radius=52, outline="#E8A94C", width=6)
    d.text((256, 66), "NEO'S", font=font(58, True), fill="#F4D08A", anchor="ma")
    d.text((256, 126), "MORE MOBS", font=font(56, True), fill="#FFF4D6", anchor="ma")
    d.line((82, 214, 430, 214), fill="#4F7B62", width=4)
    faces = [
        ("bear", "#8A5D3B", "#3B271B"),
        ("snake", "#5F9340", "#2E4A21"),
        ("monkey", "#8A5A34", "#D9B184"),
        ("tiger", "#E7862C", "#2B2019"),
        ("penguin", "#F2EEE4", "#202A35"),
    ]
    x = 92
    for index, (kind, a, b) in enumerate(faces):
        cy = 318
        if kind == "bear":
            d.ellipse((x - 42, cy - 30, x + 42, cy + 42), fill=a)
            d.ellipse((x - 46, cy - 50, x - 18, cy - 24), fill=a)
            d.ellipse((x + 18, cy - 50, x + 46, cy - 24), fill=a)
            d.ellipse((x - 22, cy - 12, x - 12, cy - 2), fill=b)
            d.ellipse((x + 12, cy - 12, x + 22, cy - 2), fill=b)
            d.ellipse((x - 12, cy + 10, x + 12, cy + 26), fill="#C49B70")
            d.ellipse((x - 5, cy + 12, x + 5, cy + 20), fill=b)
        elif kind == "snake":
            d.arc((x - 52, cy - 50, x + 10, cy + 12), 180, 355, fill=a, width=18)
            d.arc((x - 20, cy - 26, x + 44, cy + 38), 0, 180, fill=a, width=18)
            d.ellipse((x - 62, cy - 64, x - 20, cy - 22), fill=a)
            d.ellipse((x - 55, cy - 57, x - 45, cy - 47), fill=b)
        elif kind == "monkey":
            d.ellipse((x - 42, cy - 36, x + 42, cy + 48), fill=a)
            d.ellipse((x - 54, cy - 22, x - 30, cy + 4), fill=a)
            d.ellipse((x + 30, cy - 22, x + 54, cy + 4), fill=a)
            d.ellipse((x - 27, cy - 15, x + 27, cy + 34), fill=b)
            d.ellipse((x - 17, cy - 7, x - 7, cy + 3), fill=b)
            d.ellipse((x + 7, cy - 7, x + 17, cy + 3), fill=b)
            d.arc((x - 14, cy + 10, x + 14, cy + 38), 0, 180, fill=b, width=3)
        elif kind == "tiger":
            d.ellipse((x - 45, cy - 38, x + 45, cy + 48), fill=a)
            d.ellipse((x - 52, cy - 56, x - 24, cy - 28), fill=a)
            d.ellipse((x + 24, cy - 56, x + 52, cy - 28), fill=a)
            d.ellipse((x - 26, cy - 6, x + 26, cy + 36), fill="#F2E4C8")
            d.ellipse((x - 18, cy - 4, x - 8, cy + 6), fill=b)
            d.ellipse((x + 8, cy - 4, x + 18, cy + 6), fill=b)
            for px in (-30, -15, 0, 15, 30):
                d.line((x + px, cy - 34, x + px + 9, cy - 14), fill=b, width=4)
            d.polygon([(x - 7, cy + 16), (x + 7, cy + 16), (x, cy + 25)], fill="#B86A62")
            d.line((x, cy + 25, x, cy + 30), fill=b)
        else:
            d.ellipse((x - 42, cy - 42, x + 42, cy + 48), fill=b)
            d.ellipse((x - 32, cy - 30, x + 32, cy + 42), fill="#F2EEE4")
            d.ellipse((x - 20, cy - 18, x - 10, cy - 8), fill=b)
            d.ellipse((x + 10, cy - 18, x + 20, cy - 8), fill=b)
            d.polygon([(x - 6, cy + 6), (x + 6, cy + 6), (x, cy + 18)], fill="#E8942D")
        x += 82
    d.text((256, 438), "22 FULLY ANIMATED ANIMALS", font=font(22, True), fill="#C9D9C7", anchor="ma")
    path = ROOT / "pack_icon.png"
    img.resize((256, 256), Image.LANCZOS).save(path)
    return path

def make_bb_ops(mob):
    tex_size = mob.get("texture_size", TEX_SIZE)
    ops = [{"op": "set_model_properties", "name": mob["name"], "model_identifier": mob["geometry"], "resolution": {"width": tex_size, "height": tex_size}}]
    for bone in mob["bones"]:
        op = {"op": "add_group", "name": bone["name"], "origin": bone["origin"]}
        if bone["parent"]:
            op["parent"] = bone["parent"]
        ops.append(op)
    for cube in mob["cubes"]:
        ops.append({
            "op": "add_cube",
            "name": cube["name"],
            "from": cube["from"],
            "to": cube["to"],
            "box_uv": True,
            "uv_offset": cube["uv_offset"],
            "parent": cube["bone"],
        })
    return ops

def animation_ops(mob):
    ops = []
    for name, data in mob["clips"].items():
        anim_name = f"animation.neosmoremobs.{mob['id']}.{name}"
        ops.append({"op": "add_animation", "name": anim_name, "length": data["length"], "loop": "loop" if data["loop"] else "once"})
        for bone, channels in data["bones"].items():
            for channel, keys in channels.items():
                for time, value in keys.items():
                    ops.append({
                        "op": "set_keyframe",
                        "animation": anim_name,
                        "bone": bone,
                        "channel": channel,
                        "time": float(time),
                        "value": value,
                        "interpolation": "linear",
                    })
    return ops

def run_bb(tool, payload, timeout=900):
    command = [str(BUN), "run", "headless/call.ts", "--root", ROOT_STR, tool, json.dumps(payload, separators=(",", ":"))]
    result = subprocess.run(command, cwd=str(BB), capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"{tool} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    text = result.stdout.strip()
    if not text:
        raise RuntimeError(f"{tool} returned no output\nSTDERR:\n{result.stderr}")
    try:
        value, _ = json.JSONDecoder().raw_decode(text)
        return value
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{tool} returned non-JSON output\nSTDOUT:\n{text}\nSTDERR:\n{result.stderr}") from error

def run_bb_raw(tool, payload, timeout=900):
    command = [str(BUN), "run", "headless/call.ts", "--root", ROOT_STR, tool, json.dumps(payload, separators=(",", ":"))]
    result = subprocess.run(command, cwd=str(BB), capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"{tool} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.stdout.strip()

def build_blockbench_models():
    MODELS.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    for mob in MOBS:
        if "import" in mob:
            continue
        mob_id = mob["id"]
        model_rel = f"work/models/{mob_id}.bbmodel"
        model_path = ROOT / model_rel
        if model_path.exists():
            model_path.unlink()
        tex_size = mob.get("texture_size", TEX_SIZE)
        created = run_bb("bbmodel_create", {
            "file": model_rel,
            "format": "bedrock",
            "resolution": {"width": tex_size, "height": tex_size},
            "overwrite": True,
        })
        revision = created["revision"]
        edited = run_bb("bbmodel_edit", {
            "file": model_rel,
            "expected_revision": revision,
            "operations": make_bb_ops(mob),
        })
        revision = edited["revision"]
        textured = run_bb("bbmodel_add_texture", {
            "file": model_rel,
            "expected_revision": revision,
            "image": f"work/textures/{mob_id}.png",
            "name": f"{mob_id}_texture",
            "assign_to": [c["name"] for c in mob["cubes"]],
        })
        revision = textured["revision"]
        all_ops = animation_ops(mob)
        for index in range(0, len(all_ops), 350):
            batch = all_ops[index:index + 350]
            result = run_bb("bbmodel_edit", {
                "file": model_rel,
                "expected_revision": revision,
                "operations": batch,
            })
            revision = result["revision"]
        validation = run_bb("bbmodel_validate", {"file": model_rel})
        (MODELS / f"{mob_id}.validation.json").write_text(json.dumps(validation, indent=2))
        anim_validation = run_bb("bbmodel_validate_animations", {"file": model_rel})
        (MODELS / f"{mob_id}.animation_validation.json").write_text(json.dumps(anim_validation, indent=2))
        sheet_text = run_bb_raw("bbmodel_contact_sheet", {
            "file": model_rel,
            "views": ["front", "right", "back", "left", "three-quarter"],
            "size": 384,
            "orthographic": True,
            "lighting": "flat",
        })
        (MODELS / f"{mob_id}.sheet.txt").write_text(sheet_text)
        for line in sheet_text.splitlines():
            if ": " not in line:
                continue
            label, image_path = line.split(": ", 1)
            source = Path(image_path)
            if label in ("front", "right", "back", "left", "three-quarter") and source.exists():
                shutil.copyfile(source, RENDERS / f"{mob_id}_{label}.png")
        preview_times = {
            "idle": 1.0,
            "walk": 0.3,
            "run": 0.2,
            "attack": 0.3,
        }
        for clip, time in preview_times.items():
            if clip in mob["clips"]:
                out = f"work/renders/{mob_id}_{clip}.png"
                target = ROOT / out
                if target.exists():
                    target.unlink()
                run_bb("bbmodel_render", {
                    "file": model_rel,
                    "view": "three-quarter",
                    "width": 512,
                    "height": 512,
                    "lighting": "outdoor",
                    "clip": f"animation.neosmoremobs.{mob_id}.{clip}",
                    "time": time,
                    "output": out,
                    "overwrite": True,
                })
        out_geo = f"NeosMoreMobs_RP/models/entity/{mob_id}.geo.json"
        geo_path = ROOT / out_geo
        if geo_path.exists():
            geo_path.unlink()
        run_bb("bbmodel_export_bedrock_geometry", {
            "file": model_rel,
            "output": out_geo,
            "identifier": mob["geometry"],
            "visible_bounds": True,
            "overwrite": True,
        })

def item_entry(name, minimum, maximum, weight):
    return {
        "type": "item",
        "name": name,
        "weight": weight,
        "functions": [
            {"function": "set_count", "count": {"min": minimum, "max": maximum}},
            {"function": "looting_enchant", "count": {"min": 0, "max": 1}},
        ],
    }

def write_loot(mob):
    data = {"pools": [{"rolls": 1, "entries": [item_entry(*entry) for entry in mob["loot"]]}]}
    path = BP / "loot_tables" / "entities" / f"{mob['id']}.json"
    path.write_text(json.dumps(data, indent=2))

def family_filter(value):
    return {"test": "is_family", "subject": "other", "value": value}

def write_bp(mob):
    aquatic = mob["id"] in ("shark", "whale", "jelly")
    components = {
        "minecraft:is_hidden_when_invisible": {},
        "minecraft:type_family": {"family": mob["families"]},
        "minecraft:breathable": {"breathes_air": False, "breathes_water": True, "total_supply": 15, "suffocate_time": 0} if aquatic else {"total_supply": 15, "suffocate_time": 0},
        "minecraft:nameable": {},
        "minecraft:health": {"value": mob["health"], "max": mob["health"]},
        "minecraft:hurt_on_condition": {
            "damage_conditions": [{
                "filters": {"test": "in_lava", "subject": "self", "operator": "==", "value": True},
                "cause": "lava",
                "damage_per_tick": 4,
            }]
        },
        "minecraft:collision_box": {"width": mob["collision"][0], "height": mob["collision"][1]},
        "minecraft:movement": {"value": mob["speed"]},
        "minecraft:follow_range": {"value": 32},
        "minecraft:despawn": {"despawn_from_distance": {}},
        "minecraft:pushable_by_entity": {},
        "minecraft:pushable_by_block": {},
        "minecraft:conditional_bandwidth_optimization": {},
        "minecraft:experience_reward": {"on_death": "query.last_hit_by_player ? Math.Random(1,3) : 0"},
        "minecraft:loot": {"table": f"loot_tables/entities/{mob['id']}.json"},
        "minecraft:behavior.random_look_around": {"priority": 7 if aquatic else 8},
    }
    if aquatic:
        components.update({
            "minecraft:navigation.generic": {
                "is_amphibious": False,
                "can_path_over_water": False,
                "can_swim": True,
                "can_walk": False,
                "can_breach": False,
                "can_sink": False,
            },
            "minecraft:underwater_movement": {"value": 0.2},
            "minecraft:movement.sway": {},
            "minecraft:physics": {"has_gravity": False},
            "minecraft:behavior.random_swim": {"priority": 5, "interval": 0, "xz_dist": 20},
        })
    else:
        components.update({
            "minecraft:navigation.walk": {
                "can_path_over_water": True,
                "avoid_water": mob["id"] not in ("penguin", "bear", "blackbear", "crocodile", "platypus"),
                "avoid_damage_blocks": True,
            },
            "minecraft:movement.basic": {},
            "minecraft:jump.static": {},
            "minecraft:behavior.float": {"priority": 0},
            "minecraft:physics": {},
            "minecraft:behavior.random_stroll": {"priority": 6, "speed_multiplier": 0.7},
            "minecraft:behavior.look_at_player": {"priority": 7, "look_distance": 8.0, "probability": 0.02},
        })
    if mob["id"] == "platypus":
        components["minecraft:water_movement"] = {"drag_factor": 0.9}
        components["minecraft:behavior.panic"] = {"priority": 1, "speed_multiplier": 1.35}
    if mob["id"] == "penguin":
        components["minecraft:water_movement"] = {"drag_factor": 0.9}
        components["minecraft:behavior.panic"] = {"priority": 1, "speed_multiplier": 1.35}
        components["minecraft:behavior.tempt"] = {
            "priority": 4,
            "speed_multiplier": 0.8,
            "within_radius": 12,
            "items": ["fish", "salmon"],
        }
    elif mob["id"] == "monkey":
        components["minecraft:can_climb"] = {}
        components["minecraft:behavior.panic"] = {"priority": 1, "speed_multiplier": 1.4}
        components["minecraft:behavior.tempt"] = {
            "priority": 4,
            "speed_multiplier": 0.9,
            "within_radius": 12,
            "items": ["apple", "sweet_berries", "melon_slice"],
        }
    elif mob["id"] == "kangaroo":
        components["minecraft:behavior.panic"] = {"priority": 1, "speed_multiplier": 1.35}
        components["minecraft:behavior.tempt"] = {"priority": 4, "speed_multiplier": 0.9, "within_radius": 12, "items": ["apple", "wheat"]}
    elif mob["id"] == "emu":
        components["minecraft:behavior.panic"] = {"priority": 1, "speed_multiplier": 1.4}
        components["minecraft:behavior.tempt"] = {"priority": 4, "speed_multiplier": 1.0, "within_radius": 12, "items": ["wheat_seeds", "melon_seeds", "pumpkin_seeds"]}
    elif mob["id"] == "deer":
        components["minecraft:behavior.panic"] = {"priority": 1, "speed_multiplier": 1.4}
        components["minecraft:behavior.tempt"] = {
            "priority": 4,
            "speed_multiplier": 0.9,
            "within_radius": 12,
            "items": ["apple", "wheat"],
        }
        components["minecraft:behavior.avoid_mob_type"] = {
            "priority": 2,
            "entity_types": [{
                "filters": {"any_of": [family_filter("player"), family_filter("wolf"), family_filter("fox")]},
                "max_dist": 8,
                "walk_speed_multiplier": 1.1,
                "sprint_speed_multiplier": 1.35,
            }],
        }
    elif mob["id"] in ("bear", "blackbear"):
        components["minecraft:leashable"] = {}
        components["minecraft:balloonable"] = {"mass": 0.9}
    if mob["id"] in ("blackbear", "spider"):
        components["minecraft:can_climb"] = {}
    if mob["id"] == "lioness":
        components["minecraft:behavior.follow_mob"] = {
            "priority": 5,
            "filters": {"test": "is_family", "subject": "other", "value": "lion"},
            "preferred_actor_type": "neosmoremobs:lion",
            "search_range": 24,
            "stop_distance": 4,
            "speed_multiplier": 1.0,
        }
    if mob["id"] in ("bear", "blackbear", "monkey", "penguin", "deer"):
        components["minecraft:leashable"] = {}
        components["minecraft:balloonable"] = {"mass": 0.6 if mob["id"] in ("monkey", "penguin", "deer") else 0.9}
    if mob["damage"] > 0:
        components["minecraft:attack"] = {"damage": mob["damage"]}
        if mob["id"] in ("snake", "scorpion"):
            components["minecraft:attack"]["effect_name"] = "poison"
            components["minecraft:attack"]["effect_duration"] = 5 if mob["id"] == "snake" else 4
        components["minecraft:behavior.hurt_by_target"] = {"priority": 2}
        components["minecraft:behavior.delayed_attack"] = {
            "priority": 3,
            "attack_once": False,
            "track_target": True,
            "require_complete_path": False,
            "random_stop_interval": 0,
            "reach_multiplier": 1.5,
            "speed_multiplier": 1.0,
            "attack_duration": 0.8,
            "hit_delay_pct": 0.5,
        }
    if mob["id"] in ("tiger", "lion", "lioness"):
        components["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 4,
            "must_see": True,
            "reselect_targets": True,
            "within_radius": 20.0,
            "entity_types": [
                {"filters": {"any_of": [family_filter("player"), family_filter("sheep"), family_filter("cow"), family_filter("pig"), family_filter("chicken"), family_filter("rabbit")]}, "max_dist": 20},
            ],
        }
    elif mob["id"] in ("bear", "blackbear"):
        components["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 4,
            "must_see": True,
            "reselect_targets": True,
            "entity_types": [
                {"filters": {"any_of": [family_filter("rabbit"), family_filter("fox"), family_filter("chicken")]}, "max_dist": 14},
            ],
        }
    elif mob["id"] == "snake":
        components["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 4,
            "must_see": True,
            "reselect_targets": True,
            "entity_types": [
                {"filters": {"any_of": [family_filter("rabbit"), family_filter("chicken"), family_filter("frog")]}, "max_dist": 10},
            ],
        }
    elif mob["id"] == "scorpion":
        components["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 4,
            "must_see": True,
            "reselect_targets": True,
            "within_radius": 16.0,
            "entity_types": [
                {"filters": {"any_of": [family_filter("player"), family_filter("sheep"), family_filter("cow"), family_filter("pig"), family_filter("chicken"), family_filter("rabbit")]}, "max_dist": 16},
            ],
        }
    elif mob["id"] == "spider":
        components["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 4,
            "must_see": True,
            "reselect_targets": True,
            "within_radius": 16.0,
            "entity_types": [
                {"filters": {"any_of": [family_filter("player"), family_filter("sheep"), family_filter("cow"), family_filter("pig"), family_filter("chicken"), family_filter("rabbit")]}, "max_dist": 16},
            ],
        }
    elif mob["id"] == "crocodile":
        components["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 4,
            "must_see": True,
            "reselect_targets": True,
            "within_radius": 16.0,
            "entity_types": [
                {"filters": {"any_of": [family_filter("player"), family_filter("sheep"), family_filter("cow"), family_filter("pig"), family_filter("chicken"), family_filter("rabbit")]}, "max_dist": 16},
            ],
        }
    elif mob["id"] == "shark":
        components["minecraft:behavior.nearest_attackable_target"] = {
            "priority": 4,
            "must_see": True,
            "reselect_targets": True,
            "within_radius": 24.0,
            "entity_types": [
                {"filters": {"any_of": [family_filter("player"), family_filter("dolphin"), family_filter("fish"), family_filter("turtle")]}, "max_dist": 24},
            ],
        }
    entity_data = {
        "description": {
            "identifier": f"neosmoremobs:{mob['id']}",
            "spawn_category": "water_creature" if aquatic else mob.get("spawn_category", "creature"),
            "is_spawnable": True,
            "is_summonable": True,
        },
        "components": components,
    }
    if mob["id"] == "lion":
        pride_groups = {}
        randomize = []
        for count in range(10, 16):
            group = f"neosmoremobs:pride_{count}"
            pride_groups[group] = {
                "minecraft:spawn_entity": {
                    "entities": {
                        "min_wait_time": 0,
                        "max_wait_time": 0,
                        "num_to_spawn": count,
                        "single_use": True,
                        "spawn_entity": "neosmoremobs:lioness",
                        "spawn_event": "minecraft:entity_spawned",
                    }
                }
            }
            randomize.append({"weight": 1, "add": {"component_groups": [group]}})
        entity_data["component_groups"] = pride_groups
        entity_data["events"] = {"minecraft:entity_spawned": {"randomize": randomize}}
    data = {"format_version": "1.26.10", "minecraft:entity": entity_data}
    (BP / "entities" / f"{mob['id']}.json").write_text(json.dumps(data, indent=2))

def write_spawn_rule(mob):
    if mob.get("no_spawn_rule"):
        stale = BP / "spawn_rules" / f"{mob['id']}.json"
        if stale.exists():
            stale.unlink()
        return
    spawn = mob["spawn"]
    tags = spawn.get("tags")
    if tags is None:
        tags = [spawn["tag"]]
    underwater = spawn.get("underwater", False)
    conditions = []
    for tag in tags:
        condition = {}
        if underwater:
            condition["minecraft:spawns_on_surface"] = {}
            condition["minecraft:spawns_underwater"] = {}
            condition["minecraft:distance_filter"] = {"min": 12, "max": 48}
        else:
            condition["minecraft:spawns_on_surface"] = {}
            condition["minecraft:brightness_filter"] = spawn.get("brightness", {"min": 7, "max": 15, "adjust_for_weather": False})
        condition["minecraft:weight"] = {"default": spawn["weight"]}
        if underwater:
            condition["minecraft:height_filter"] = {"min": 0, "max": 64}
        condition["minecraft:herd"] = {"min_size": spawn["herd"][0], "max_size": spawn["herd"][1]}
        filters = [{"test": "has_biome_tag", "operator": "==", "value": tag}]
        for excluded in spawn.get("exclude", []):
            filters.append({"test": "has_biome_tag", "operator": "!=", "value": excluded})
        condition["minecraft:biome_filter"] = filters[0] if len(filters) == 1 else filters
        conditions.append(condition)
    data = {
        "format_version": "1.8.0",
        "minecraft:spawn_rules": {
            "description": {"identifier": f"neosmoremobs:{mob['id']}", "population_control": spawn.get("population_control", "water_animal" if underwater else "animal")},
            "conditions": conditions,
        },
    }
    (BP / "spawn_rules" / f"{mob['id']}.json").write_text(json.dumps(data, indent=2))

def write_client(mob):
    animations = {
        "idle": f"animation.neosmoremobs.{mob['id']}.idle",
        "walk": f"animation.neosmoremobs.{mob['id']}.walk",
        "run": f"animation.neosmoremobs.{mob['id']}.run",
        "look_at_target": "animation.common.look_at_target",
    }
    controllers = [{"move": "controller.animation.neosmoremobs.locomotion_swim" if mob["id"] == "penguin" else "controller.animation.neosmoremobs.locomotion"}]
    if mob["id"] == "penguin":
        animations["swim"] = f"animation.neosmoremobs.{mob['id']}.swim"
    elif mob["damage"] > 0:
        animations["attack"] = f"animation.neosmoremobs.{mob['id']}.attack"
        controllers.append({"attack": "controller.animation.neosmoremobs.attack"})
    if mob["id"] == "raccoon":
        animations["steal"] = "animation.neosmoremobs.raccoon.steal"
    data = {
        "format_version": "1.10.0",
        "minecraft:client_entity": {
            "description": {
                "identifier": f"neosmoremobs:{mob['id']}",
                "materials": {"default": "entity_alphatest"},
                "textures": {"default": mob["texture"]},
                "geometry": {"default": mob["geometry"]},
                "animations": animations,
                "scripts": {"animate": ["look_at_target"], "scale": str(mob["scale"])},
                "animation_controllers": controllers,
                "render_controllers": [f"controller.render.neosmoremobs.{mob['id']}"],
                "spawn_egg": {"base_color": mob["egg"][0], "overlay_color": mob["egg"][1]},
            }
        },
    }
    (RP / "entity" / f"{mob['id']}.entity.json").write_text(json.dumps(data, indent=2))

def write_animations(mob):
    animations = {}
    for name, data in mob["clips"].items():
        anim = {"animation_length": data["length"]}
        if data["loop"]:
            anim["loop"] = True
        anim["bones"] = {}
        for bone, channels in data["bones"].items():
            anim["bones"][bone] = {}
            for channel, keys in channels.items():
                anim["bones"][bone][channel] = {str(float(t)): v for t, v in keys.items()}
        animations[f"animation.neosmoremobs.{mob['id']}.{name}"] = anim
    data = {"format_version": "1.10.0", "animations": animations}
    (RP / "animations" / f"{mob['id']}.animation.json").write_text(json.dumps(data, indent=2))

def write_render_controllers():
    for mob in MOBS:
        data = {
            "format_version": "1.8.0",
            "render_controllers": {
                f"controller.render.neosmoremobs.{mob['id']}": {
                    "geometry": "Geometry.default",
                    "materials": [{"*": "Material.default"}],
                    "textures": ["Texture.default"],
                }
            },
        }
        (RP / "render_controllers" / f"{mob['id']}.render_controllers.json").write_text(json.dumps(data, indent=2))

def write_animation_controllers():
    data = {
        "format_version": "1.10.0",
        "animation_controllers": {
            "controller.animation.neosmoremobs.locomotion": {
                "initial_state": "idle",
                "states": {
                    "idle": {
                        "blend_transition": 0.3,
                        "animations": ["idle"],
                        "transitions": [{"walk": "query.modified_move_speed > 0.05"}],
                    },
                    "walk": {
                        "blend_transition": 0.25,
                        "animations": ["walk"],
                        "transitions": [
                            {"run": "query.modified_move_speed > 0.55"},
                            {"idle": "query.modified_move_speed <= 0.05"},
                        ],
                    },
                    "run": {
                        "blend_transition": 0.25,
                        "animations": ["run"],
                        "transitions": [{"walk": "query.modified_move_speed <= 0.55"}],
                    },
                },
            },
            "controller.animation.neosmoremobs.locomotion_swim": {
                "initial_state": "idle",
                "states": {
                    "idle": {
                        "blend_transition": 0.3,
                        "animations": ["idle"],
                        "transitions": [
                            {"swim": "query.is_in_water"},
                            {"walk": "query.modified_move_speed > 0.05"},
                        ],
                    },
                    "walk": {
                        "blend_transition": 0.25,
                        "animations": ["walk"],
                        "transitions": [
                            {"swim": "query.is_in_water"},
                            {"run": "query.modified_move_speed > 0.55"},
                            {"idle": "query.modified_move_speed <= 0.05"},
                        ],
                    },
                    "run": {
                        "blend_transition": 0.25,
                        "animations": ["run"],
                        "transitions": [{"walk": "query.modified_move_speed <= 0.55"}],
                    },
                    "swim": {
                        "blend_transition": 0.3,
                        "animations": ["swim"],
                        "transitions": [{"idle": "query.is_in_water == 0"}],
                    },
                },
            },
            "controller.animation.neosmoremobs.attack": {
                "initial_state": "default",
                "states": {
                    "default": {
                        "transitions": [{"attack": "query.is_delayed_attacking == 1"}],
                    },
                    "attack": {
                        "blend_transition": 0.08,
                        "animations": ["attack"],
                        "transitions": [{"default": "query.is_delayed_attacking == 0"}],
                    },
                },
            },
        },
    }
    (RP / "animation_controllers" / "neosmoremobs.animation_controllers.json").write_text(json.dumps(data, indent=2))

def ns_uuid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"neosmoremobs:{name}"))

def write_manifests(icon_path):
    bp_header = ns_uuid("bp_header")
    bp_module = ns_uuid("bp_module")
    rp_header = ns_uuid("rp_header")
    rp_module = ns_uuid("rp_module")
    bp_script = ns_uuid("bp_script_module")
    bp_manifest = {
        "format_version": 2,
        "header": {
            "name": "Neo's More Mobs BP",
            "description": "Twenty-two custom animated mobs, including a lion pride, Australian animals, and an item-stealing raccoon.",
            "uuid": bp_header,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 10],
        },
        "modules": [
            {"type": "data", "uuid": bp_module, "version": [1, 0, 0]},
            {"type": "script", "language": "javascript", "uuid": bp_script, "entry": "scripts/raccoon_theft.js", "version": [1, 0, 0]},
        ],
        "dependencies": [
            {"uuid": rp_header, "version": [1, 0, 0]},
            {"module_name": "@minecraft/server", "version": "2.0.0"},
        ],
        "metadata": {"authors": ["Neo"], "credits": ["Minecraft GrizzlyBear by ContinuedOak, CC BY-NC 4.0", "Elephant from alexs mobs by mrhurr2859, CC BY 4.0", "bison from alex's mobs by mrhurr2859, CC BY 4.0", "The scorpion girl by Bada, CC BY 4.0", "Blockbench Whale (free) by Treeminator, CC BY 4.0", "Minecraft Deer by Catnim, CC BY 4.0", "blue comb jelly from Alexs mobs by mrhurr2859, CC BY 4.0", "Minecraft Australia Edition Models by Whateverdata55, CC BY 4.0"]},
    }
    rp_manifest = {
        "format_version": 2,
        "header": {
            "name": "Neo's More Mobs RP",
            "description": "Models, textures and animations for all twenty-two Neo's More Mobs animals.",
            "uuid": rp_header,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 10],
        },
        "modules": [{"type": "resources", "uuid": rp_module, "version": [1, 0, 0]}],
        "metadata": {"authors": ["Neo"], "credits": ["Minecraft GrizzlyBear by ContinuedOak, CC BY-NC 4.0", "Elephant from alexs mobs by mrhurr2859, CC BY 4.0", "bison from alex's mobs by mrhurr2859, CC BY 4.0", "The scorpion girl by Bada, CC BY 4.0", "Blockbench Whale (free) by Treeminator, CC BY 4.0", "Minecraft Deer by Catnim, CC BY 4.0", "blue comb jelly from Alexs mobs by mrhurr2859, CC BY 4.0", "Minecraft Australia Edition Models by Whateverdata55, CC BY 4.0"]},
    }
    (BP / "manifest.json").write_text(json.dumps(bp_manifest, indent=2))
    (RP / "manifest.json").write_text(json.dumps(rp_manifest, indent=2))
    shutil.copyfile(icon_path, BP / "pack_icon.png")
    shutil.copyfile(icon_path, RP / "pack_icon.png")

def write_lang():
    lines = [
        "pack.name=Neo's More Mobs",
        "pack.description=Five fully animated animals for Bedrock.",
    ]
    for mob in MOBS:
        lines.append(f"entity.neosmoremobs:{mob['id']}.name={mob['name']}")
        lines.append(f"item.spawn_egg.entity.neosmoremobs:{mob['id']}.name={mob['name']} Spawn Egg")
    (RP / "texts" / "en_US.lang").write_text("\n".join(lines) + "\n")
    (RP / "texts" / "languages.json").write_text(json.dumps(["en_US"], indent=2))

def write_texture_copies():
    target = RP / "textures" / "entity" / "neosmoremobs"
    target.mkdir(parents=True, exist_ok=True)
    for mob in MOBS:
        if "import" in mob:
            continue
        shutil.copyfile(TEXTURES / f"{mob['id']}.png", target / f"{mob['id']}.png")

def write_addon_json():
    for mob in MOBS:
        write_bp(mob)
        write_spawn_rule(mob)
        write_loot(mob)
        write_client(mob)
        write_animations(mob)
    write_render_controllers()
    write_animation_controllers()
    write_texture_copies()
    write_lang()

def write_license():
    source = WORK / "LICENSE.txt"
    if not source.exists():
        return
    shutil.copyfile(source, ROOT / "LICENSE.txt")
    shutil.copyfile(source, BP / "LICENSE.txt")
    shutil.copyfile(source, RP / "LICENSE.txt")

def package_addon():
    output = ROOT / "NeosMoreMobs.mcaddon"
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for pack in (BP, RP):
            for path in pack.rglob("*"):
                if path.is_file():
                    zf.write(path, str(path.relative_to(ROOT)))
        license_path = ROOT / "LICENSE.txt"
        if license_path.exists():
            zf.write(license_path, "LICENSE.txt")
    return output

def summary():
    print(json.dumps({
        "root": str(ROOT),
        "mobs": [m["id"] for m in MOBS],
        "bp": str(BP),
        "rp": str(RP),
        "models": [str(MODELS / f"{m['id']}.bbmodel") for m in MOBS],
    }, indent=2))

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    for directory in [
        MODELS, TEXTURES, RENDERS,
        BP / "entities", BP / "spawn_rules", BP / "loot_tables" / "entities",
        RP / "entity", RP / "models" / "entity", RP / "animations",
        RP / "animation_controllers", RP / "render_controllers",
        RP / "textures" / "entity" / "neosmoremobs", RP / "texts",
    ]:
        directory.mkdir(parents=True, exist_ok=True)
    build_textures()
    icon = build_icon()
    write_addon_json()
    write_manifests(icon)
    write_license()
    if "--blockbench" in sys.argv:
        build_blockbench_models()
        subprocess.run([sys.executable, str(WORK / "build_imported.py")], check=True)
    if "--pack" in sys.argv:
        out = package_addon()
        print(f"packaged {out}")
    summary()

if __name__ == "__main__":
    main()
