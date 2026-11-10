#!/usr/bin/env python3
import json, os, re, sys, zipfile
from pathlib import Path

ROOT = Path("/workspace/Neo's more mobs")
OUT = ROOT / "NeosMoreMobsUnified"
BP, RP = OUT / "NeosMoreMobsUnified_BP", OUT / "NeosMoreMobsUnified_RP"
KEEP = {"blackbear", "deer", "penguin", "scorpion", "giraffe", "spider", "lion", "lioness"}
DROP = {"bear", "bison", "tiger", "monkey", "snake", "crocodile", "shark",
        "jelly", "elephant", "whale", "platypus", "kangaroo", "emu", "raccoon"}
errors = []

def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception as e:
        errors.append(f"invalid {p}: {e}")
        return {}

bp_ids, rp_ids = {}, {}
for p in (BP / "entities").glob("*.json"):
    d = load(p)
    ident = d.get("minecraft:entity", {}).get("description", {}).get("identifier")
    if not ident:
        errors.append(f"{p.name}: missing identifier")
    if ident in bp_ids:
        errors.append(f"duplicate entity id {ident}: {p.name} / {bp_ids[ident]}")
    bp_ids[ident] = p.name
for p in (RP / "entity").glob("*.entity.json"):
    d = load(p)
    ident = d.get("minecraft:client_entity", {}).get("description", {}).get("identifier")
    if not ident:
        errors.append(f"{p.name}: missing identifier")
    if ident in rp_ids:
        errors.append(f"duplicate client id {ident}")
    rp_ids[ident] = p.name

if set(bp_ids) != set(rp_ids):
    errors.append(f"bp/rp id sets differ: only-bp={sorted(set(bp_ids)-set(rp_ids))} only-rp={sorted(set(rp_ids)-set(bp_ids))}")

geo = {}
for p in (RP / "models" / "entity").glob("*.geo.json"):
    for g in load(p).get("minecraft:geometry", []):
        geo[g["description"]["identifier"]] = p.name
anims = {}
for p in (RP / "animations").glob("*.json"):
    for name in load(p).get("animations", {}):
        anims[name] = p.name
geo_bones = {}
for p in (RP / "models" / "entity").glob("*.geo.json"):
    for g in load(p).get("minecraft:geometry", []):
        geo_bones[g["description"]["identifier"]] = [b["name"] for b in g.get("bones", [])]
        for b in g.get("bones", []):
            if not re.fullmatch(r"[A-Za-z0-9_]+", b.get("name", "")):
                errors.append(f"{p.name}: invalid bone name {b.get('name')!r}")
            for c in b.get("cubes", []):
                if "from" in c or "to" in c:
                    errors.append(f"{p.name}:{b.get('name')} uses from/to instead of origin/size")
                if "origin" not in c or "size" not in c:
                    errors.append(f"{p.name}:{b.get('name')} missing origin/size")
                elif any(v < 0.009 for v in c["size"]):
                    errors.append(f"{p.name}:{b.get('name')} degenerate cube {c['size']}")
ctrls = {}
for p in (RP / "animation_controllers").glob("*.json"):
    ctrls.update(load(p).get("animation_controllers", {}))
rctrls = {}
for p in (RP / "render_controllers").glob("*.json"):
    rctrls.update(load(p).get("render_controllers", {}))
controllers_refd = set()
lang = (RP / "texts" / "en_US.lang").read_text()

for ident, fname in sorted(bp_ids.items()):
    stem = fname[:-5]
    client = load(RP / "entity" / f"{stem}.entity.json")["minecraft:client_entity"]["description"]
    tex = client.get("textures", {}).get("default", "")
    if not (RP / f"{tex}.png").exists():
        errors.append(f"{stem}: texture {tex} missing")
    mid = client.get("geometry", {}).get("default", "")
    if mid not in geo and not mid.startswith(("geometry.zombie.", "geometry.spider.")):
        errors.append(f"{stem}: geometry {mid} missing")
    for key, name in client.get("animations", {}).items():
        if not name:
            continue
        if name.startswith("controller."):
            builtin = name.startswith(("controller.animation.humanoid.", "controller.animation.zombie.", "controller.animation.enderman.", "controller.animation.spider."))
            if not builtin and name not in ctrls:
                errors.append(f"{stem}: animation controller {name} missing")
            continue
        builtin = name.startswith(("animation.common.", "animation.humanoid.", "animation.zombie.", "animation.enderman.", "animation.spider."))
        if not builtin and name not in anims:
            errors.append(f"{stem}: animation {name} missing")
    for entry in client.get("animation_controllers", []):
        for cname in entry.values():
            builtin = cname.startswith(("controller.animation.humanoid.", "controller.animation.zombie.", "controller.animation.enderman.", "controller.animation.spider."))
            if builtin:
                continue
            if cname not in ctrls:
                errors.append(f"{stem}: controller {cname} missing")
            else:
                controllers_refd.add(cname)
                for st in ctrls[cname].get("states", {}).values():
                    for a in st.get("animations", []):
                        if a not in client.get("animations", {}):
                            errors.append(f"{stem}: controller {cname} uses undefined '{a}'")
    if f"entity.{ident}.name=" not in lang:
        errors.append(f"{ident}: missing lang name")
    if "spawn_egg" not in client:
        errors.append(f"{ident}: missing spawn egg")
    if "animation_controllers" in client:
        errors.append(f"{ident}: legacy animation_controllers still present")
    for rc in client.get("render_controllers", []):
        rid = rc.get("controller") if isinstance(rc, dict) else rc
        if isinstance(rid, str) and rid not in rctrls and not rid.startswith("controller.render.zombie."):
            errors.append(f"{ident}: render controller {rid} missing")
    gid = client.get("geometry", {}).get("default")
    if gid in geo_bones:
        ap = RP / "animations" / f"{stem}.animation.json"
        if ap.exists():
            bones = set(geo_bones[gid])
            for clip, c in load(ap).get("animations", {}).items():
                for bname in c.get("bones", {}):
                    if bname not in bones:
                        errors.append(f"{stem}: {clip} animates missing bone {bname!r}")
    flat_animate = client.get("scripts", {}).get("animate", [])
    if isinstance(flat_animate, str):
        flat_animate = [flat_animate]
    for a in flat_animate:
        key = next(iter(a)) if isinstance(a, dict) else a
        target = client.get("animations", {}).get(key)
        if target is None:
            errors.append(f"{ident}: animate references undefined key {key}")
    bd = load(BP / "entities" / fname)["minecraft:entity"]
    loot = bd.get("components", {}).get("minecraft:loot", {}).get("table")
    if loot and not (BP / loot).exists():
        errors.append(f"{ident}: loot {loot} missing")

for c in controllers_refd:
    pass

# Duplicate-file checks: extras must not shadow a port file.
extras_stems = KEEP
for folder, suffix in (("models/entity", ".geo.json"), ("animations", ".animation.json"),
                       ("entity", ".entity.json"), ("render_controllers", ".render_controllers.json")):
    for stem in extras_stems:
        name = f"{stem}{suffix}"
        if (RP / folder / name).exists() and stem not in KEEP:
            errors.append(f"unexpected extras file {folder}/{name}")

# No dropped extras survive under the extras namespace (port files with the
# same file stem are the real Alex's Mobs versions and must stay).
for stem in DROP:
    if f"neosmoremobs:{stem}" in bp_ids:
        errors.append(f"dropped extras mob still registered: neosmoremobs:{stem}")
    if f"neosmoremobs:{stem}" in rp_ids:
        errors.append(f"dropped extras client still registered: neosmoremobs:{stem}")
if f"neosmoremobs:raccoon" in bp_ids or f"neosmoremobs:raccoon" in rp_ids:
    errors.append("extras raccoon still present")

# Script wiring.
bp_manifest = load(BP / "manifest.json")
mods = bp_manifest.get("modules", [])
if not any(m.get("type") == "script" for m in mods):
    errors.append("missing script module")
script = (BP / "scripts" / "raccoon_theft.js").read_text()
if "alexsmobs:raccoon" not in script:
    errors.append("raccoon script not retargeted")
if "neosmoremobs:raccoon" in script:
    errors.append("raccoon script still references removed extras raccoon")
rp_uuid = load(RP / "manifest.json")["header"]["uuid"]
deps = {d.get("uuid") for d in bp_manifest.get("dependencies", []) if d.get("uuid")}
if rp_uuid not in deps:
    errors.append("bp does not depend on its rp")

# Spawn rules reference existing entities and valid biome tags.
valid = {"animal","bamboo","beach","birch","caves","cherry_grove","cold","crimson_forest","deep",
         "desert","dripstone_caves","edge","extreme_hills","flower_forest","forest","frozen",
         "frozen_peaks","grove","ice_plains","jagged_peaks","jungle","lukewarm","lush_caves",
         "mangrove_swamp","meadow","mega","mesa","monster","mooshroom_island","mountain","mutated",
         "nether","ocean","plains","plateau","river","roofed","savanna","snowy_slopes",
         "soulsand_valley","stone","sunflower_plains","swamp","taiga","the_end","warm","warped_forest","overworld"}
for p in (BP / "spawn_rules").glob("*.json"):
    d = load(p).get("minecraft:spawn_rules", {})
    ident = d.get("description", {}).get("identifier")
    if ident not in bp_ids:
        errors.append(f"{p.name}: spawn rule for unknown {ident}")
    for cond in d.get("conditions", []):
        v = cond.get("minecraft:biome_filter", {}).get("value")
        if v and v not in valid:
            errors.append(f"{p.name}: invalid biome tag {v}")

count = len(bp_ids)
if count != 100:
    errors.append(f"expected 100 mobs, got {count}")

# Graveyard structure + Forgotten Soul wiring.
import sys as _sys
_sys.path.insert(0, str(ROOT / "work" / "structure_tools"))
from mcs_lib import read_structure
struct_path = BP / "structures" / "graveyard.mcstructure"
if not struct_path.exists():
    errors.append("missing graveyard.mcstructure")
else:
    st = read_structure(struct_path.read_bytes())
    names = [e["name"] for e in st["block_palette"]]
    if "minecraft:soul_soil" not in names:
        errors.append("graveyard has no soul_soil spawn surface")
    if "minecraft:chest" not in names:
        errors.append("graveyard has no loot chest")
    pos_data = st.get("block_position_data", {})
    tables = [v.get("block_entity_data", {}).get("LootTable") for v in pos_data.values()]
    for t in tables:
        if t and not (BP / t).exists():
            errors.append(f"structure chest loot missing {t}")
if not (BP / "features" / "graveyard.json").exists():
    errors.append("missing graveyard feature")
else:
    feat = load(BP / "features" / "graveyard.json")["minecraft:structure_template_feature"]
    if feat.get("structure_name") != "mystructure:graveyard":
        errors.append(f"graveyard feature structure_name {feat.get('structure_name')}")
    if feat["description"]["identifier"] != "neosmoremobs:graveyard":
        errors.append("graveyard feature identifier mismatch")
if not (BP / "feature_rules" / "graveyard_rule.json").exists():
    errors.append("missing graveyard feature rule")
else:
    rule = load(BP / "feature_rules" / "graveyard_rule.json")["minecraft:feature_rules"]
    if rule["description"]["places_feature"] != "neosmoremobs:graveyard":
        errors.append("graveyard rule places wrong feature")
    if "scatter_chance" not in rule.get("distribution", {}):
        errors.append("graveyard rule has no scatter_chance")
soul = load(BP / "spawn_rules" / "forgotten_soul.json")["minecraft:spawn_rules"]
conds = soul.get("conditions", [{}])[0]
blk = conds.get("minecraft:spawns_on_block_filter")
def _is_soil(x):
    return x == "minecraft:soul_soil" or (isinstance(x, dict) and x.get("name") == "minecraft:soul_soil")
if not (blk == "minecraft:soul_soil" or (isinstance(blk, list) and any(_is_soil(x) for x in blk))):
    errors.append(f"forgotten soul spawn rule not tied to graveyard soil ({blk!r})")
if conds.get("minecraft:biome_filter", {}).get("value") != "overworld":
    errors.append("forgotten soul spawn rule not restricted to overworld")
# Miner Zombie / Void Dealer wiring.
for mid in ("miner_zombie", "void_dealer"):
    if f"neosmoremobs:{mid}" not in bp_ids:
        errors.append(f"missing {mid}")
    if not (BP / "spawn_rules" / f"{mid}.json").exists():
        errors.append(f"missing {mid} spawn rule")
    if not (BP / "loot_tables" / "entities" / f"{mid}.json").exists():
        errors.append(f"missing {mid} loot")
b = load(BP / "manifest.json")
if not any(m.get("entry") == "scripts/main.js" for m in b.get("modules", [])):
    errors.append("script entry is not scripts/main.js")
if not any(d.get("module_name") == "@minecraft/server-ui" for d in b.get("dependencies", [])):
    errors.append("missing @minecraft/server-ui dependency")
for f in ("main.js", "raccoon_theft.js", "void_dealer_trade.js"):
    if not (BP / "scripts" / f).exists():
        errors.append(f"missing script {f}")
if "neosmoremobs:void_dealer" not in (BP / "scripts" / "void_dealer_trade.js").read_text():
    errors.append("trade script does not target the Void Dealer")
vd = load(BP / "spawn_rules" / "void_dealer.json")["minecraft:spawn_rules"]["conditions"]
tags = [c.get("minecraft:biome_filter", {}).get("value") for c in vd]
if len(vd) != 2 or set(tags) != {"overworld", "the_end"}:
    errors.append(f"void dealer spawn biomes wrong: {tags}")
mz = load(BP / "spawn_rules" / "miner_zombie.json")["minecraft:spawn_rules"]["conditions"]
if not any("minecraft:spawns_underground" in c for c in mz):
    errors.append("miner zombie does not spawn underground")
pkg = ROOT / "NeosMoreMobs_AlexsMobsPort.mcaddon"
if not pkg.exists():
    errors.append("missing mcaddon")
else:
    with zipfile.ZipFile(pkg) as z:
        names = set(z.namelist())
        for req in ("NeosMoreMobsUnified_BP/manifest.json", "NeosMoreMobsUnified_RP/manifest.json", "LICENSE.txt"):
            if req not in names:
                errors.append(f"package missing {req}")
        bp_entities = [n for n in names if n.startswith("NeosMoreMobsUnified_BP/entities/")]
        if len(bp_entities) != count:
            errors.append(f"package entity count {len(bp_entities)} != {count}")

if errors:
    print("FAIL", len(errors))
    for e in errors[:80]:
        print(" -", e)
    sys.exit(1)
print(f"PASS: unified pack has {count} unique mobs ({count - 89} originals + 89 port), graveyard, Forgotten Soul, Miner Zombie and Void Dealer wired; references valid")
