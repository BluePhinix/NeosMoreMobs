#!/usr/bin/env python3
"""Re-rig the spider: one rigid bone per leg (inner+outer cubes), Y/Z step gait."""
import json

GEO = "/workspace/Neo's more mobs/NeosMoreMobs_RP/models/entity/spider.geo.json"
ANIM = "/workspace/Neo's more mobs/NeosMoreMobs_RP/animations/spider.animation.json"

UPPERS = ("leg5", "leg6", "leg7", "leg8", "leg9", "leg10", "leg11", "leg12")
LEFT = ("leg6", "leg8", "leg10", "leg12")


def main():
    doc = json.load(open(GEO))
    g = doc["minecraft:geometry"][0]
    baked = {b["name"]: b for b in g["bones"]}
    lowers = {}
    for b in g["bones"]:
        if b["name"].startswith("bone2") and b.get("parent") in UPPERS:
            lowers[b["parent"]] = b

    legs = {"left": [], "right": []}
    for up_name in UPPERS:
        up = baked[up_name]
        side = "left" if up_name in LEFT else "right"
        cubes = list(up.get("cubes", []))
        low = lowers.get(up_name)
        if low:
            cubes.extend(low.get("cubes", []))
        legs[side].append((up.get("pivot", [0, 0, 0])[2], cubes))
    for side in legs:
        legs[side].sort(key=lambda item: item[0])

    bones = [baked[n] for n in ("spider", "body4", "bone19", "head5", "head_sub_0", "neck2") if n in baked]
    named = {"left": [], "right": []}
    for side, items in legs.items():
        for i, (z, cubes) in enumerate(items):
            name = f"{side}Leg{i + 1}"
            named[side].append((z, name))
            bones.append({
                "name": name, "parent": "spider",
                "pivot": [4 if side == "left" else -4, 5, z],
                "cubes": cubes,
            })
    g["bones"] = bones
    json.dump(doc, open(GEO, "w"), indent=1)
    print("spider re-rigged:", [b["name"] for b in bones])

    adoc = json.load(open(ANIM))
    anims = adoc["animations"]
    old = set(UPPERS) | {b["name"] for b in lowers.values()} | {"left", "rightside"}

    def gait(amp_y, amp_z, length):
        out = {}
        for side, items in named.items():
            for i, (_z, bone) in enumerate(items):
                phase = 1 if i % 2 == 0 else -1
                if side == "right":
                    phase = -phase
                y = amp_y * phase
                z = amp_z * phase * (1 if side == "left" else -1)
                out[bone] = {"rotation": {
                    "0.0": [0, y, z],
                    str(length / 2): [0, -y, -z],
                    str(length): [0, y, z],
                }}
        return out

    for key, (amp_y, amp_z, length) in {
        "animation.neosmoremobs.spider.walk": (14, 5, 1.0),
        "animation.neosmoremobs.spider.run": (20, 7, 0.7),
    }.items():
        clip = anims[key]
        for o in old:
            clip["bones"].pop(o, None)
        clip["bones"].update(gait(amp_y, amp_z, length))
        clip["bones"].setdefault("spider", {"position": {
            "0.0": [0, 0, 0], "0.25": [0, 0.2, 0],
            "0.5": [0, 0, 0], "0.75": [0, 0.2, 0], "1.0": [0, 0, 0],
        }})

    for key in anims:
        if key in ("animation.neosmoremobs.spider.walk", "animation.neosmoremobs.spider.run"):
            continue
        for o in old:
            anims[key]["bones"].pop(o, None)
    json.dump(adoc, open(ANIM, "w"), indent=1)
    print("spider animations re-targeted")


if __name__ == "__main__":
    main()
