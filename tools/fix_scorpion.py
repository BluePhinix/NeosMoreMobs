#!/usr/bin/env python3
"""Re-rig the scorpion so legs are chained pairs and the stinger is one solid tail."""
import json

GEO = "/workspace/Neo's more mobs/NeosMoreMobs_RP/models/entity/scorpion.geo.json"
ANIM = "/workspace/Neo's more mobs/NeosMoreMobs_RP/animations/scorpion.animation.json"

TAIL_BONES = ("bone3", "bone4", "bone5", "bone6", "bone7", "bone8")


def main():
    doc = json.load(open(GEO))
    g = doc["minecraft:geometry"][0]
    baked = {b["name"]: b for b in g["bones"]}
    root = baked["root"]

    # ---- rigid tail: every stinger segment becomes part of hcost
    hcost = baked["hcost"]
    tail_cubes = list(hcost.get("cubes", []))
    for name in TAIL_BONES:
        tail_cubes.extend(baked[name].get("cubes", []))
    hcost["cubes"] = tail_cubes

    kept = ["root", "body", "bone", "bone2", "hcost", "head", "headwear",
            "left_arm", "right_arm"]
    bones = [baked[n] for n in kept if n in baked]

    # ---- split each side's three legs into upper + lower chained bones
    def split_side(side, upper_name, lower_name, upper_pivot_x, lower_pivot_x):
        upper = baked[upper_name]["cubes"]
        lower = baked[lower_name]["cubes"]
        zs = (5, 13, 20)
        for i, z in enumerate(zs):
            up = [c for c in upper if round(c.get("pivot", [0, 0, 0])[2]) == z]
            lo = [c for c in lower if round(c.get("pivot", [0, 0, 0])[2]) == z]
            if not up and not lo:
                continue
            up_name = f"{side}Leg{i + 1}"
            lo_name = f"{side}Leg{i + 1}Low"
            bones.append({
                "name": up_name, "parent": "root",
                "pivot": [upper_pivot_x, 10.296846, z], "cubes": up,
            })
            bones.append({
                "name": lo_name, "parent": up_name,
                "pivot": [lower_pivot_x, 5.75, z], "cubes": lo,
            })

    split_side("left", "left_leg", "left_leg2", 10, 16.788691)
    split_side("right", "right_leg", "right_leg2", -10, -16.5)

    g["bones"] = bones
    json.dump(doc, open(GEO, "w"), indent=1)
    print("scorpion geometry re-rigged:", [b["name"] for b in bones])

    # ---- animations: drop old leg/tail channels, drive the new chains
    adoc = json.load(open(ANIM))
    anims = adoc["animations"]
    remap = {
        "walk": (18, 10, 1.0),
        "run": (26, 14, 0.7),
    }
    phases = {
        "leftLeg1": 1, "leftLeg2": -1, "leftLeg3": 1,
        "rightLeg1": -1, "rightLeg2": 1, "rightLeg3": -1,
    }
    for state, (up_amp, low_amp, length) in remap.items():
        clip = anims[f"animation.neosmoremobs.scorpion.{state}"]
        bones_out = clip["bones"]
        for old in ("left_leg", "right_leg", "left_leg2", "right_leg2",
                    *TAIL_BONES):
            bones_out.pop(old, None)
        for leg, sign in phases.items():
            up = up_amp * sign
            low = -low_amp * sign
            bones_out[leg] = {"rotation": {"0.0": [up, 0, 0], str(length / 2): [-up, 0, 0], str(length): [up, 0, 0]}}
            bones_out[leg + "Low"] = {"rotation": {"0.0": [low, 0, 0], str(length / 2): [-low, 0, 0], str(length): [low, 0, 0]}}
        clip["bones"] = bones_out

    for key in anims:
        for b in anims[key]["bones"]:
            pass
    for key, clip in anims.items():
        for old in TAIL_BONES:
            clip["bones"].pop(old, None)
    json.dump(adoc, open(ANIM, "w"), indent=1)
    print("scorpion animations re-targeted")


if __name__ == "__main__":
    main()
