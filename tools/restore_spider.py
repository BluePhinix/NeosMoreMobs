#!/usr/bin/env python3
"""Restore the provided Australia spider model from its bbmodel and fix its gait."""
import copy
import json
import shutil
import uuid

ROOT = "/workspace/Neo's more mobs"
BB = f"{ROOT}/work/models/spider.bbmodel"
GEO = f"{ROOT}/NeosMoreMobs_RP/models/entity/spider.geo.json"
ANIM = f"{ROOT}/NeosMoreMobs_RP/animations/spider.animation.json"
TEX_SRC = f"{ROOT}/work/textures/spider.png"
TEX_DST = f"{ROOT}/NeosMoreMobs_RP/textures/entity/neosmoremobs/spider.png"
CLIENT = f"{ROOT}/NeosMoreMobs_RP/entity/spider.entity.json"
QA = f"{ROOT}/work/qa/frames_models/spider.bbmodel"


def keyframes_for(bone, length, amp_y, amp_z):
    return [
        {"uuid": str(uuid.uuid4()), "channel": "rotation", "time": 0.0,
         "interpolation": "linear", "data_points": [{"x": 0, "y": amp_y, "z": amp_z}]},
        {"uuid": str(uuid.uuid4()), "channel": "rotation", "time": round(length / 2, 4),
         "interpolation": "linear", "data_points": [{"x": 0, "y": -amp_y, "z": -amp_z}]},
        {"uuid": str(uuid.uuid4()), "channel": "rotation", "time": length,
         "interpolation": "linear", "data_points": [{"x": 0, "y": amp_y, "z": amp_z}]},
    ]


def main():
    bb = json.load(open(BB))
    geo = json.load(open(GEO))["minecraft:geometry"][0]
    bones = {b["name"]: b for b in geo["bones"]}

    # upper legs grouped by side, ordered front-to-back
    uppers = {name: b for name, b in bones.items() if name in
              ("leg5", "leg6", "leg7", "leg8", "leg9", "leg10", "leg11", "leg12")}
    sides = {"left": [], "right": []}
    for name, b in uppers.items():
        side = "left" if b.get("parent") == "left" else "right"
        sides[side].append((b["pivot"][2], name))
    for s in sides:
        sides[s].sort()
    phase = {}
    for side, items in sides.items():
        for i, (_z, name) in enumerate(items):
            p = 1 if i % 2 == 0 else -1
            if side == "right":
                p = -p
            zsign = 1 if side == "left" else -1
            phase[name] = (p, zsign)

    def gait(length, amp_y, amp_z):
        return {name: {"rotation": {
            "0.0": [0, amp_y * p, amp_z * p * zs],
            str(round(length / 2, 4)): [0, -amp_y * p, -amp_z * p * zs],
            str(length): [0, amp_y * p, amp_z * p * zs],
        }} for name, (p, zs) in phase.items()}

    # Bedrock animation JSON from the bbmodel clips, with fixed walk/run legs
    out = {"format_version": "1.8.0", "animations": {}}
    qa = copy.deepcopy(bb)
    qa_anims = {a["name"]: a for a in qa["animations"]}
    for anim in bb["animations"]:
        short = anim["name"].rsplit(".", 1)[-1]
        length = anim.get("length", 1.0)
        bones_out = {}
        for _uid, animator in anim.get("animators", {}).items():
            bone = animator.get("name")
            chans = {}
            for kf in animator.get("keyframes", []):
                ch = kf.get("channel")
                if ch not in ("rotation", "position"):
                    continue
                dp = kf["data_points"][0]
                chans.setdefault(ch, {})[str(round(kf["time"], 4))] = [dp["x"], dp["y"], dp["z"]]
            if chans:
                bones_out[bone] = chans
        if short in ("walk", "run"):
            amp_y, amp_z = (14, 5) if short == "walk" else (20, 7)
            for name in phase:
                bones_out[name] = {"rotation": {
                    "0.0": [0, amp_y * phase[name][0], amp_z * phase[name][0] * phase[name][1]],
                    str(round(length / 2, 4)): [0, -amp_y * phase[name][0], -amp_z * phase[name][0] * phase[name][1]],
                    str(length): [0, amp_y * phase[name][0], amp_z * phase[name][0] * phase[name][1]],
                }}
            # rewrite the QA bbmodel animator keyframes as well
            qanim = qa_anims[anim["name"]]
            for uid, group in ((g["uuid"], g) for g in qa["groups"]):
                if group["name"] in phase:
                    qanim["animators"][uid] = {
                        "name": group["name"], "type": "bone",
                        "keyframes": keyframes_for(group["name"], length,
                                                   amp_y * phase[group["name"]][0],
                                                   amp_z * phase[group["name"]][0] * phase[group["name"]][1]),
                    }
        out["animations"][f"animation.neosmoremobs.spider.{short}"] = {
            "loop": True, "animation_length": length, "bones": bones_out,
        }

    json.dump(out, open(ANIM, "w"), indent=1)
    json.dump(qa, open(QA, "w"))
    shutil.copyfile(TEX_SRC, TEX_DST)

    client = {
        "format_version": "1.10.0",
        "minecraft:client_entity": {"description": {
            "identifier": "neosmoremobs:spider",
            "materials": {"default": "entity_alphatest"},
            "textures": {"default": "textures/entity/neosmoremobs/spider"},
            "geometry": {"default": "geometry.neosmoremobs.spider"},
            "animations": {
                "idle": "animation.neosmoremobs.spider.idle",
                "walk": "animation.neosmoremobs.spider.walk",
                "run": "animation.neosmoremobs.spider.run",
                "attack": "animation.neosmoremobs.spider.attack",
                "look_at_target": "animation.common.look_at_target",
                "locomotion": "controller.animation.neosmoremobs.locomotion",
                "attack_controller": "controller.animation.neosmoremobs.attack",
            },
            "scripts": {"animate": ["look_at_target", "locomotion", "attack_controller"]},
            "render_controllers": ["controller.render.neosmoremobs.spider"],
            "spawn_egg": {"base_color": "#3B2C23", "overlay_color": "#8A6B3F"},
        }}
    }
    open(CLIENT, "w").write(json.dumps(client, indent=1))
    print("spider restored; QA bbmodel updated")


if __name__ == "__main__":
    main()
