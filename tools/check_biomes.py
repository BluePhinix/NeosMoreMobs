#!/usr/bin/env python3
import json, re, zipfile
from pathlib import Path

ROOT = Path("/workspace/Neo's more mobs")
OUT = ROOT / "NeosMoreBiomes"
BP, RP = OUT / "NeosMoreBiomes_BP", OUT / "NeosMoreBiomes_RP"
SAMPLES = Path("/workspace/bedrock-samples-v1.26.40.05-full (1)")
errors = []

NOISE = {"default","default_mutated","lowlands","highlands","mountains","extreme",
         "less_extreme","taiga","swamp","ocean","deep_ocean","river","beach","stone_beach","mushroom"}
CATS = {"medium","cold","warm","frozen","lukewarm"}
SURF = {"minecraft:overworld","minecraft:mesa","minecraft:swamp","minecraft:frozen_ocean",
        "minecraft:capped","minecraft:the_end","minecraft:noise_gradient"}
MUSIC = set()
for p in (SAMPLES / "resource_pack" / "biomes").glob("*.client_biome.json"):
    d = json.loads(p.read_text())["minecraft:client_biome"]["components"]
    m = d.get("minecraft:biome_music", {}).get("music_definition")
    if m:
        MUSIC.add(m)
FOGS = {p.name.replace("_fog_setting.json", "") for p in (SAMPLES / "resource_pack" / "fogs").glob("*_fog_setting.json")}
TAGS = set()
for p in (SAMPLES / "behavior_pack" / "biomes").glob("*.biome.json"):
    d = json.loads(p.read_text())["minecraft:biome"]["components"]
    for t in d.get("minecraft:tags", {}).get("tags", []):
        TAGS.add(t)

def load(p):
    try:
        return json.loads(p.read_text())
    except Exception as e:
        errors.append(f"invalid {p.name}: {e}")
        return {}

bp_ids = {}
for p in (BP / "biomes").glob("*.biome.json"):
    d = load(p)
    b = d.get("minecraft:biome", {})
    ident = b.get("description", {}).get("identifier", "")
    if not ident.startswith("neosmorebiomes:"):
        errors.append(f"{p.name}: bad identifier {ident}")
    if ident in bp_ids:
        errors.append(f"{p.name}: duplicate {ident}")
    bp_ids[ident] = p
    c = b.get("components", {})
    for req in ("minecraft:climate","minecraft:overworld_height","minecraft:surface_builder","minecraft:tags"):
        if req not in c:
            errors.append(f"{p.name}: missing {req}")
    height = c.get("minecraft:overworld_height", {}).get("noise_type")
    if height not in NOISE:
        errors.append(f"{p.name}: bad noise {height}")
    surf = c.get("minecraft:surface_builder", {}).get("builder", {})
    if surf.get("type") not in SURF:
        errors.append(f"{p.name}: bad surface type {surf.get('type')}")
    for k in ("foundation_material","mid_material","top_material","sea_material"):
        if not surf.get(k):
            errors.append(f"{p.name}: surface missing {k}")
    if surf.get("type") == "minecraft:mesa":
        for k in ("clay_material","hard_clay_material","bryce_pillars","has_forest"):
            if k not in surf:
                errors.append(f"{p.name}: mesa missing {k}")
    if surf.get("type") == "minecraft:swamp" and "max_puddle_depth_below_sea_level" not in surf:
        errors.append(f"{p.name}: swamp missing puddle depth")
    gen = c.get("minecraft:overworld_generation_rules", {})
    cats = gen.get("generate_for_climates")
    if not cats:
        errors.append(f"{p.name}: no generate_for_climates")
    for cat, weight in cats or []:
        if cat not in CATS:
            errors.append(f"{p.name}: bad climate category {cat}")
        if not isinstance(weight, int) or weight <= 0:
            errors.append(f"{p.name}: bad weight {weight}")
    tags = c.get("minecraft:tags", {}).get("tags", [])
    if "overworld" not in tags:
        errors.append(f"{p.name}: missing overworld tag")
    for t in tags:
        if t.startswith("neo_"):
            continue
        if t not in TAGS:
            errors.append(f"{p.name}: unknown vanilla tag {t}")

rp_ids = {}
for p in (RP / "biomes").glob("*.client_biome.json"):
    d = load(p)
    c = d.get("minecraft:client_biome", {})
    ident = c.get("description", {}).get("identifier", "")
    rp_ids[ident] = p
    comp = c.get("components", {})
    fog = comp.get("minecraft:fog_appearance", {}).get("fog_identifier", "")
    if fog.replace("minecraft:fog_", "") not in FOGS:
        errors.append(f"{p.name}: bad fog {fog}")
    music = comp.get("minecraft:biome_music", {}).get("music_definition")
    if music and music not in MUSIC:
        errors.append(f"{p.name}: bad music {music}")
    water = comp.get("minecraft:water_appearance", {}).get("surface_color", "")
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", water):
        errors.append(f"{p.name}: bad water color {water}")
    if ident not in bp_ids:
        errors.append(f"{p.name}: no matching behavior biome")

if set(bp_ids) != set(rp_ids):
    errors.append(f"biome id sets differ: {len(bp_ids)} bp vs {len(rp_ids)} rp")
if len(bp_ids) != 30:
    errors.append(f"expected 30 biomes, got {len(bp_ids)}")

features = {}
for p in (BP / "features").glob("*.json"):
    d = load(p)
    key = next((k for k in d if k.startswith("minecraft:")), None)
    ident = d.get(key, {}).get("description", {}).get("identifier", "")
    features[ident] = p
    if ident.split(":")[-1] != p.stem:
        errors.append(f"{p.name}: identifier/file mismatch {ident}")
rules = {}
for p in (BP / "feature_rules").glob("*.json"):
    d = load(p)
    r = d.get("minecraft:feature_rules", {})
    ident = r.get("description", {}).get("identifier", "")
    rules[ident] = p
    feat = r.get("description", {}).get("places_feature")
    if feat not in features:
        errors.append(f"{p.name}: places unknown feature {feat}")
    tag = r.get("conditions", {}).get("minecraft:biome_filter", {}).get("value")
    if tag and not any(tag in json.loads(x.read_text())["minecraft:biome"]["components"]["minecraft:tags"]["tags"] for x in bp_ids.values()):
        errors.append(f"{p.name}: biome tag {tag} not used by any biome")

bp_manifest = load(BP / "manifest.json")
rp_uuid = load(RP / "manifest.json")["header"]["uuid"]
deps = {d.get("uuid") for d in bp_manifest.get("dependencies", []) if d.get("uuid")}
for need in ("08ea1f24-e2b2-5799-b4ae-aea7a21d4456", "111d4c0b-65a9-5663-b0fd-6af67f38a8db", rp_uuid):
    if need not in deps:
        errors.append(f"missing dependency {need}")

pkg = ROOT / "NeosMoreBiomes.mcaddon"
if not pkg.exists():
    errors.append("missing mcaddon")
else:
    with zipfile.ZipFile(pkg) as z:
        names = z.namelist()
        n_bp = len([n for n in names if n.startswith("NeosMoreBiomes_BP/biomes/")])
        n_rp = len([n for n in names if n.startswith("NeosMoreBiomes_RP/biomes/")])
        if n_bp != 30 or n_rp != 30:
            errors.append(f"package biomes bp={n_bp} rp={n_rp}")
        for req in ("NeosMoreBiomes_BP/manifest.json", "NeosMoreBiomes_RP/manifest.json"):
            if req not in names:
                errors.append(f"package missing {req}")

if errors:
    print("FAIL", len(errors))
    for e in errors[:80]:
        print(" -", e)
    raise SystemExit(1)
print(f"PASS: {len(bp_ids)} biomes, {len(features)} features, {len(rules)} feature rules; references valid")
