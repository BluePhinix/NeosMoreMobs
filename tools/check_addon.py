from pathlib import Path
import json
import zipfile

ROOT = Path("/workspace/Neo's more mobs")
BP = ROOT / "NeosMoreMobs_BP"
RP = ROOT / "NeosMoreMobs_RP"
IDS = ["bear", "tiger", "monkey", "penguin", "snake", "blackbear", "crocodile", "shark", "deer", "lion", "elephant", "bison", "lioness", "scorpion", "whale", "jelly", "giraffe", "raccoon", "platypus", "kangaroo", "emu", "spider"]
errors = []

def load(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        errors.append(f"invalid json {path}: {exc}")
        return {}

bp_manifest = load(BP / "manifest.json")
rp_manifest = load(RP / "manifest.json")
uuids = [bp_manifest["header"]["uuid"], bp_manifest["modules"][0]["uuid"], rp_manifest["header"]["uuid"], rp_manifest["modules"][0]["uuid"]]
if len(set(uuids)) != 4:
    errors.append("manifest uuids are not unique")
bp_dependencies = bp_manifest.get("dependencies", [])
if {"uuid": rp_manifest["header"]["uuid"], "version": [1, 0, 0]} not in bp_dependencies:
    errors.append("bp -> rp dependency does not match rp header uuid")
if {"module_name": "@minecraft/server", "version": "2.0.0"} not in bp_dependencies:
    errors.append("bp is missing the @minecraft/server script dependency")
if not any(module.get("type") == "script" and module.get("entry") == "scripts/raccoon_theft.js" for module in bp_manifest.get("modules", [])):
    errors.append("bp is missing the raccoon script module")

controllers = load(RP / "animation_controllers" / "neosmoremobs.animation_controllers.json")
available_controllers = controllers.get("animation_controllers", {})
lang = (RP / "texts" / "en_US.lang").read_text()

for mob_id in IDS:
    bp = load(BP / "entities" / f"{mob_id}.json")
    rp = load(RP / "entity" / f"{mob_id}.entity.json")
    geo = load(RP / "models" / "entity" / f"{mob_id}.geo.json")
    anim = load(RP / "animations" / f"{mob_id}.animation.json")
    loot = load(BP / "loot_tables" / "entities" / f"{mob_id}.json")
    spawn = {} if mob_id == "lioness" else load(BP / "spawn_rules" / f"{mob_id}.json")
    rc = load(RP / "render_controllers" / f"{mob_id}.render_controllers.json")
    identifier = f"neosmoremobs:{mob_id}"
    if bp.get("minecraft:entity", {}).get("description", {}).get("identifier") != identifier:
        errors.append(f"{mob_id}: bp identifier mismatch")
    if rp.get("minecraft:client_entity", {}).get("description", {}).get("identifier") != identifier:
        errors.append(f"{mob_id}: rp identifier mismatch")
    desc = rp.get("minecraft:client_entity", {}).get("description", {})
    tex = desc.get("textures", {}).get("default", "")
    if not (RP / f"{tex}.png").exists():
        errors.append(f"{mob_id}: missing texture {tex}")
    geo_id = desc.get("geometry", {}).get("default")
    geo_ids = [g.get("description", {}).get("identifier") for g in geo.get("minecraft:geometry", [])]
    if geo_id not in geo_ids:
        errors.append(f"{mob_id}: geometry identifier {geo_id} not in geo")
    geo_bones = {b["name"] for g in geo.get("minecraft:geometry", []) for b in g.get("bones", [])}
    anims = anim.get("animations", {})
    for key, name in desc.get("animations", {}).items():
        if name.startswith("animation.neosmoremobs.") and name not in anims:
            errors.append(f"{mob_id}: missing animation {name}")
    for name, data in anims.items():
        for bone in data.get("bones", {}):
            if bone not in geo_bones:
                errors.append(f"{mob_id}: animation {name} targets missing bone {bone}")
    for controller in desc.get("animation_controllers", []):
        for key, name in controller.items():
            if name not in available_controllers:
                errors.append(f"{mob_id}: missing controller {name}")
    for name in desc.get("render_controllers", []):
        if name not in rc.get("render_controllers", {}):
            errors.append(f"{mob_id}: missing render controller {name}")
    if not loot.get("pools"):
        errors.append(f"{mob_id}: empty loot table")
    if mob_id == "lioness":
        if (BP / "spawn_rules" / f"{mob_id}.json").exists():
            errors.append("lioness should not have a natural spawn rule")
    else:
        if spawn.get("minecraft:spawn_rules", {}).get("description", {}).get("identifier") != identifier:
            errors.append(f"{mob_id}: spawn rule identifier mismatch")
    if f"entity.{identifier}.name=" not in lang:
        errors.append(f"{mob_id}: missing entity lang key")
    if f"item.spawn_egg.entity.{identifier}.name=" not in lang:
        errors.append(f"{mob_id}: missing spawn egg lang key")
    if "spawn_egg" not in desc:
        errors.append(f"{mob_id}: missing spawn egg definition")

lion_entity = load(BP / "entities" / "lion.json")["minecraft:entity"]
pride_groups = lion_entity.get("component_groups", {})
for count in range(10, 16):
    group = pride_groups.get(f"neosmoremobs:pride_{count}", {})
    spawner = group.get("minecraft:spawn_entity", {}).get("entities", {})
    if spawner.get("num_to_spawn") != count or spawner.get("spawn_entity") != "neosmoremobs:lioness":
        errors.append(f"lion pride group {count} is incorrect")
randomize = lion_entity.get("events", {}).get("minecraft:entity_spawned", {}).get("randomize", [])
if len(randomize) != 6:
    errors.append("lion pride spawn event should have six random outcomes")
lioness_entity = load(BP / "entities" / "lioness.json")["minecraft:entity"]["components"]
if "minecraft:behavior.follow_mob" not in lioness_entity:
    errors.append("lioness is missing follow_mob")

for passive in ("monkey", "deer"):
    passive_bp = load(BP / "entities" / f"{passive}.json")["minecraft:entity"]["components"]
    for component in ("minecraft:attack", "minecraft:behavior.delayed_attack", "minecraft:behavior.hurt_by_target", "minecraft:behavior.nearest_attackable_target"):
        if component in passive_bp:
            errors.append(f"{passive} still has {component}")
    passive_rp = load(RP / "entity" / f"{passive}.entity.json")["minecraft:client_entity"]["description"]
    if "attack" in passive_rp.get("animations", {}):
        errors.append(f"{passive} still has attack animation")
    if any("attack" in c for c in passive_rp.get("animation_controllers", [])):
        errors.append(f"{passive} still has attack controller")

lion_spawn = load(BP / "spawn_rules" / "lion.json")
deer_spawn = load(BP / "spawn_rules" / "deer.json")
if "savanna" not in json.dumps(lion_spawn):
    errors.append("lion spawn rule is missing savanna")
for tag in ("forest", "meadow"):
    if tag not in json.dumps(deer_spawn):
        errors.append(f"deer spawn rule is missing {tag}")

package = ROOT / "NeosMoreMobs.mcaddon"
if not package.exists():
    errors.append("mcaddon package missing")
else:
    with zipfile.ZipFile(package) as zf:
        names = set(zf.namelist())
        if "NeosMoreMobs_BP/scripts/raccoon_theft.js" not in names:
            errors.append("package is missing the raccoon theft script")
        for required in ("NeosMoreMobs_BP/manifest.json", "NeosMoreMobs_RP/manifest.json", "NeosMoreMobs_BP/pack_icon.png", "NeosMoreMobs_RP/pack_icon.png"):
            if required not in names:
                errors.append(f"package missing {required}")
        if "work/build.py" in names or "work/validator/package.json" in names:
            errors.append("package contains work files")
        if "LICENSE.txt" not in names or "NeosMoreMobs_BP/LICENSE.txt" not in names or "NeosMoreMobs_RP/LICENSE.txt" not in names:
            errors.append("package is missing LICENSE.txt")
        else:
            license_text = zf.read("LICENSE.txt").decode("utf-8")
            for credit in ("ContinuedOak", "mrhurr2859", "Bada", "Treeminator", "Catnim", "Whateverdata55", "CC BY-NC 4.0", "CC BY 4.0"):
                if credit not in license_text:
                    errors.append(f"LICENSE.txt is missing {credit}")

if errors:
    print("FAIL")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)
print("PASS: identifiers, textures, geometry, animations, controllers, loot, spawn rules, lang, passive monkey, and package all verified")
