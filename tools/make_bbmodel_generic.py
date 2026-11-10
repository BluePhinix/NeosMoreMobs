#!/usr/bin/env python3
"""Convert a unified-pack mob (box or per-face UV, numeric clips) to .bbmodel for QA."""
import base64
import json
import os
import shutil
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RP = "/workspace/Neo's more mobs/NeosMoreMobsUnified/NeosMoreMobsUnified_RP"

BOX_FACES = ("north", "east", "south", "west", "up", "down")


def box_faces(u, v, sx, sy, sz):
    return {
        "north": [u + sz, v + sz, u + sz + sx, v + sz + sy],
        "east": [u, v + sz, u + sz, v + sz + sy],
        "south": [u + 2 * sz + sx, v + sz, u + 2 * sz + 2 * sx, v + sz + sy],
        "west": [u + sz + sx, v + sz, u + 2 * sz + sx, v + sz + sy],
        "up": [u + sz, v, u + sz + sx, v + sz],
        "down": [u + sz + sx, v, u + 2 * sx + sz, v + sz],
    }


def find_texture(rp, mob):
    for rel in (f"textures/entity/neosmoremobs/{mob}.png",
                f"textures/entity/alexsmobs/{mob}.png",
                f"textures/entity/{mob}.png"):
        p = os.path.join(rp, rel)
        if os.path.exists(p):
            return p
    for root, _dirs, files in os.walk(os.path.join(rp, "textures")):
        if f"{mob}.png" in files:
            return os.path.join(root, f"{mob}.png")
    raise FileNotFoundError(mob)


def build(rp, mob, out_dir, clips=None):
    geo_doc = json.load(open(os.path.join(rp, "models", "entity", f"{mob}.geo.json")))
    geo = geo_doc["minecraft:geometry"][0]
    desc = geo["description"]
    tw, th = desc["texture_width"], desc["texture_height"]

    elements, groups, child_elements, child_groups, roots = [], {}, {}, {}, []
    for bone in geo["bones"]:
        uuids = []
        for i, c in enumerate(bone.get("cubes", [])):
            frm = c["origin"]
            to = [frm[j] + c["size"][j] for j in range(3)]
            sx, sy, sz = [to[j] - frm[j] for j in range(3)]
            uv = c["uv"]
            if isinstance(uv, dict):
                faces = {}
                for face in BOX_FACES:
                    entry = uv.get(face)
                    if not entry:
                        continue
                    x, y = entry["uv"]
                    w, h = entry["uv_size"]
                    faces[face] = {"uv": [x, y, x + w, y + h], "texture": 0}
            else:
                faces = {f: {"uv": rect, "texture": 0}
                         for f, rect in box_faces(uv[0], uv[1], sx, sy, sz).items()}
            el = {
                "name": f"{bone['name']}_{i}", "from": frm, "to": to,
                "origin": c.get("pivot", bone.get("pivot", [0, 0, 0])),
                "uv_offset": uv if isinstance(uv, list) else [0, 0],
                "faces": faces, "type": "cube", "uuid": str(uuid.uuid4()),
            }
            if c.get("rotation"):
                el["rotation"] = c["rotation"]
            if c.get("mirror"):
                el["mirror_uv"] = True
            if c.get("inflate"):
                el["inflate"] = c["inflate"]
            elements.append(el)
            uuids.append(el["uuid"])
        grp = {"name": bone["name"], "origin": bone.get("pivot", [0, 0, 0]),
               "uuid": str(uuid.uuid4())}
        if bone.get("rotation"):
            grp["rotation"] = bone["rotation"]
        groups[bone["name"]] = grp
        child_elements[bone["name"]] = uuids

    for bone in geo["bones"]:
        parent = bone.get("parent")
        if parent and parent in groups:
            child_groups.setdefault(parent, []).append(bone["name"])
        else:
            roots.append(bone["name"])

    def node(name):
        return {"uuid": groups[name]["uuid"],
                "children": [node(c) for c in child_groups.get(name, [])] + child_elements.get(name, [])}
    outliner = [node(r) for r in roots]

    anim_path = os.path.join(rp, "animations", f"{mob}.animation.json")
    animations = []
    if os.path.exists(anim_path):
        anims = json.load(open(anim_path))["animations"]
        for key, clip in anims.items():
            name = key.rsplit(".", 1)[-1]
            if clips and name not in clips:
                continue
            length = clip.get("animation_length") or 1.0
            animators = {}
            for bone, channels in clip.get("bones", {}).items():
                if bone not in groups:
                    continue
                kfs = []
                for channel in ("rotation", "position"):
                    if channel not in channels:
                        continue
                    value = channels[channel]
                    if isinstance(value, list):
                        value = {0.0: value, float(length): value}
                    for t, vec in sorted(value.items(), key=lambda kv: float(kv[0])):
                        if not (isinstance(vec, list) and len(vec) == 3
                                and all(isinstance(v, (int, float)) for v in vec)):
                            continue
                        kfs.append({
                            "uuid": str(uuid.uuid4()), "channel": channel,
                            "time": float(t), "interpolation": "linear",
                            "data_points": [{"x": vec[0], "y": vec[1], "z": vec[2]}],
                        })
                if kfs:
                    animators[groups[bone]["uuid"]] = {"name": bone, "type": "bone", "keyframes": kfs}
            animations.append({
                "name": name, "loop": "loop" if clip.get("loop", True) else "once",
                "length": length, "snapping": 20, "animators": animators,
                "uuid": str(uuid.uuid4()),
            })
    elif mob in ("void_dealer", "miner_zombie"):
        # QA approximation of the enderman humanoid move clip used by the move controller.
        length = 1.0
        kfs_by_bone = {}
        steps = 24
        for i in range(steps + 1):
            t = length * i / steps
            import math
            tcos = 50.0 * math.cos(t * math.tau)
            vals = {"leftarm": [tcos, 0, 0], "leftleg": [tcos * -1.4, -0.1, -0.1],
                    "rightarm": [-tcos, 0, 0], "rightleg": [tcos * 1.4, 0.1, 0.1]}
            for bname, vec in vals.items():
                actual = next((g for g in groups if g.lower() == bname), None)
                if not actual:
                    continue
                kfs_by_bone.setdefault(actual, []).append({
                    "uuid": str(uuid.uuid4()), "channel": "rotation", "time": round(t, 4),
                    "interpolation": "linear",
                    "data_points": [{"x": vec[0], "y": vec[1], "z": vec[2]}],
                })
        animations.append({
            "name": "walk", "loop": "loop", "length": length, "snapping": 20,
            "animators": {groups[b]["uuid"]: {"name": b, "type": "bone", "keyframes": kf}
                          for b, kf in kfs_by_bone.items()},
            "uuid": str(uuid.uuid4()),
        })

    tex_path = find_texture(rp, mob)
    b64 = base64.b64encode(open(tex_path, "rb").read()).decode()
    model = {
        "meta": {"format_version": "4.10", "model_format": "bedrock", "box_uv": True},
        "name": mob, "resolution": {"width": tw, "height": th},
        "elements": elements, "groups": list(groups.values()), "outliner": outliner,
        "textures": [{
            "path": "", "name": f"{mob}.png", "folder": "", "namespace": "", "id": "0",
            "width": tw, "height": th, "uv_width": tw, "uv_height": th, "particle": False,
            "render_mode": "default", "visible": True, "internal": True, "mode": "bitmap",
            "saved": False, "source": "data:image/png;base64," + b64, "uuid": str(uuid.uuid4()),
        }],
        "animations": animations,
    }
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, f"{mob}.bbmodel")
    open(dst, "w").write(json.dumps(model))
    shutil.copyfile(tex_path, os.path.join(out_dir, f"{mob}.png"))
    return dst


if __name__ == "__main__":
    rp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RP
    mob = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "qa", "frames_models")
    clips = sys.argv[4:] or None
    print(build(rp, mob, out, clips))
