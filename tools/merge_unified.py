#!/usr/bin/env python3
"""Merge Neo's More Mobs into the Alex's Mobs Neo Port as one addon.

Keeps only the original mobs that Alex's Mobs does not already provide and
removes every duplicate animal (and every colliding file name).
"""
import json
import os
import shutil
import uuid
import zipfile
from pathlib import Path

ROOT = Path("/workspace/Neo's more mobs")
PORT = ROOT / "AlexsMobsNeoPort"
EXTRAS_BP = ROOT / "NeosMoreMobs_BP"
EXTRAS_RP = ROOT / "NeosMoreMobs_RP"
OUT = ROOT / "NeosMoreMobsUnified"
BP = OUT / "NeosMoreMobsUnified_BP"
RP = OUT / "NeosMoreMobsUnified_RP"

# Extras that have no Alex's Mobs counterpart.
KEEP = {"blackbear", "deer", "penguin", "scorpion", "giraffe", "spider", "lion", "lioness"}

# Extras that duplicate a ported Alex's Mobs animal (dropped).
DROP = {"bear", "bison", "tiger", "monkey", "snake", "crocodile", "shark",
        "jelly", "elephant", "whale", "platypus", "kangaroo", "emu", "raccoon"}


def ns(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"neosmoremobsunified:{name}"))


def normalize_clients(rp):
    """Bedrock 1.26 rejects the legacy `animation_controllers` child in client
    entities; reference controllers through `animations` + `scripts.animate`
    (the form the working Void Dealer / Forgotten Soul use)."""
    changed = 0
    for path in (rp / "entity").glob("*.entity.json"):
        data = json.loads(path.read_text())
        desc = data.get("minecraft:client_entity", {}).get("description")
        if not desc or "animation_controllers" not in desc:
            continue
        ctrls = desc.pop("animation_controllers")
        anims = desc.setdefault("animations", {})
        scripts = desc.setdefault("scripts", {})
        animate = scripts.get("animate", [])
        if isinstance(animate, str):
            animate = [animate]
        elif not isinstance(animate, list):
            animate = []
        for entry in ctrls:
            if not isinstance(entry, dict):
                continue
            for key, ctrl in entry.items():
                existing = next((k for k, v in anims.items() if v == ctrl), None)
                if existing:
                    use = existing
                else:
                    use = key
                    if use in anims:
                        use = key + "_controller"
                    i = 2
                    while use in anims:
                        use = f"{key}_{i}"
                        i += 1
                    anims[use] = ctrl
                already = use in animate or any(isinstance(a, dict) and use in a for a in animate)
                if not already:
                    animate.append(use)
        scripts["animate"] = animate
        path.write_text(json.dumps(data, indent=2))
        changed += 1
    print(f"normalized {changed} client entities (controller wiring)")


def copy_tree(src, dst):
    for path in src.rglob("*"):
        if path.is_file():
            target = dst / path.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    copy_tree(PORT / "AlexsMobsNeoPort_BP", BP)
    copy_tree(PORT / "AlexsMobsNeoPort_RP", RP)

    for mob in sorted(KEEP):
        required = [
            (EXTRAS_BP / "entities" / f"{mob}.json", BP / "entities" / f"{mob}.json"),
            (EXTRAS_RP / "entity" / f"{mob}.entity.json", RP / "entity" / f"{mob}.entity.json"),
            (EXTRAS_RP / "render_controllers" / f"{mob}.render_controllers.json", RP / "render_controllers" / f"{mob}.render_controllers.json"),
            (EXTRAS_RP / "textures" / "entity" / "neosmoremobs" / f"{mob}.png", RP / "textures" / "entity" / "neosmoremobs" / f"{mob}.png"),
        ]
        required += [
            (EXTRAS_RP / "models" / "entity" / f"{mob}.geo.json", RP / "models" / "entity" / f"{mob}.geo.json"),
            (EXTRAS_RP / "animations" / f"{mob}.animation.json", RP / "animations" / f"{mob}.animation.json"),
        ]
        optional = [
            (EXTRAS_BP / "spawn_rules" / f"{mob}.json", BP / "spawn_rules" / f"{mob}.json"),
            (EXTRAS_BP / "loot_tables" / "entities" / f"{mob}.json", BP / "loot_tables" / "entities" / f"{mob}.json"),
        ]
        for src, dst in required:
            if not src.exists():
                raise FileNotFoundError(src)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        for src, dst in optional:
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)

    shutil.copyfile(EXTRAS_RP / "animation_controllers" / "neosmoremobs.animation_controllers.json",
                    RP / "animation_controllers" / "neosmoremobs.animation_controllers.json")

    # Raccoon theft now applies to the ported Alex's Mobs raccoon.
    script = (EXTRAS_BP / "scripts" / "raccoon_theft.js").read_text()
    script = script.replace("neosmoremobs:raccoon", "alexsmobs:raccoon")
    script = "\n".join(line for line in script.splitlines()
                       if "animation.neosmoremobs.raccoon.steal" not in line) + "\n"
    (BP / "scripts").mkdir(parents=True, exist_ok=True)
    (BP / "scripts" / "raccoon_theft.js").write_text(script)

    # Graveyard + Forgotten Soul assets (structure, feature, spawn rule, RP).
    stage = ROOT / "work" / "graveyard_assets"
    copy_tree(stage / "BP", BP)
    copy_tree(stage / "RP", RP)

    # Miner Zombie + Void Dealer assets.
    more = ROOT / "work" / "more_mobs_assets"
    copy_tree(more / "BP", BP)
    copy_tree(more / "RP", RP)

    normalize_clients(RP)

    # Language: port names + kept extras names/eggs.
    port_lang = (PORT / "AlexsMobsNeoPort_RP" / "texts" / "en_US.lang").read_text().splitlines()
    extras_lang = {}
    for line in (EXTRAS_RP / "texts" / "en_US.lang").read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            extras_lang[k] = v
    lines = list(port_lang)
    for mob in sorted(KEEP):
        key = f"entity.neosmoremobs:{mob}.name"
        egg = f"item.spawn_egg.entity.neosmoremobs:{mob}.name"
        if key in extras_lang:
            lines.append(f"{key}={extras_lang[key]}")
            lines.append(f"{egg}={extras_lang.get(egg, extras_lang[key] + ' Spawn Egg')}")
    lines.extend((stage / "lang.txt").read_text().splitlines())
    lines.extend((more / "lang.txt").read_text().splitlines())
    (RP / "texts" / "en_US.lang").write_text("\n".join(lines) + "\n")

    # Combined license.
    license_parts = [
        "Neo's More Mobs + Alex's Mobs (Bedrock port)\n============================================\n",
        "This package contains work ported from Alex's Mobs 1.22.9 by AlexModGuy and\n"
        "contributors (LGPL-3.0) and original/third-party models listed below.\n",
        "--- Alex's Mobs / Citadel: LGPL-3.0 ---\n",
        (PORT / "LICENSE.txt").read_text(),
        "\n--- Neo's More Mobs third-party model licenses ---\n",
        (ROOT / "LICENSE.txt").read_text(),
    ]
    (OUT / "LICENSE.txt").write_text("\n".join(license_parts))
    for target in (BP / "LICENSE.txt", RP / "LICENSE.txt"):
        shutil.copyfile(OUT / "LICENSE.txt", target)

    # Manifests.
    bp_header, bp_data, bp_script = ns("bp_header"), ns("bp_data"), ns("bp_script")
    rp_header, rp_res = ns("rp_header"), ns("rp_res")
    mob_count = len(list((BP / "entities").glob("*.json")))
    (BP / "manifest.json").write_text(json.dumps({
        "format_version": 2,
        "header": {
            "name": "Neo's More Mobs + Alex's Mobs",
            "description": f"{mob_count} mobs in one pack: the Alex's Mobs 1.22.9 Bedrock port plus Neo's original mobs. Duplicates removed. Includes graveyard structures where Forgotten Souls spawn, Miner Zombies and the Void Dealer trader.",
            "uuid": bp_header,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 10],
        },
        "modules": [
            {"type": "data", "uuid": bp_data, "version": [1, 0, 0]},
            {"type": "script", "language": "javascript", "uuid": bp_script,
             "entry": "scripts/main.js", "version": [1, 0, 0]},
        ],
        "dependencies": [
            {"uuid": rp_header, "version": [1, 0, 0]},
            {"module_name": "@minecraft/server", "version": "2.0.0"},
            {"module_name": "@minecraft/server-ui", "version": "2.0.0"},
        ],
        "metadata": {
            "authors": ["Neo"],
            "credits": [
                "Alex's Mobs by AlexModGuy and contributors, LGPL-3.0",
                "Citadel by AlexModGuy and contributors",
                "Minecraft GrizzlyBear by ContinuedOak, CC BY-NC 4.0",
                "Elephant from alex's mobs by mrhurr2859, CC BY 4.0",
                "bison from alex's mobs by mrhurr2859, CC BY 4.0",
                "The scorpion girl by Bada, CC BY 4.0",
                "Blockbench Whale (free) by Treeminator, CC BY 4.0",
                "Minecraft Deer by Catnim, CC BY 4.0",
                "blue comb jelly from Alexs mobs by mrhurr2859, CC BY 4.0",
                "Minecraft Australia Edition Models by Whateverdata55, CC BY 4.0",
            ],
        },
    }, indent=2))
    (RP / "manifest.json").write_text(json.dumps({
        "format_version": 2,
        "header": {
            "name": "Neo's More Mobs + Alex's Mobs RP",
            "description": f"Models, textures and animations for {mob_count} mobs.",
            "uuid": rp_header,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 10],
        },
        "modules": [{"type": "resources", "uuid": rp_res, "version": [1, 0, 0]}],
        "metadata": {
            "authors": ["Neo"],
            "credits": ["Alex's Mobs by AlexModGuy and contributors, LGPL-3.0",
                        "Citadel by AlexModGuy and contributors"],
        },
    }, indent=2))

    # Icon.
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new("RGBA", (256, 256), "#17201b")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    draw.rounded_rectangle((12, 12, 244, 244), radius=26, outline="#D8A64A", width=4)
    draw.text((128, 66), "NEO'S MORE", font=font, fill="#F2CF7A", anchor="ma")
    draw.text((128, 96), "MOBS", font=font, fill="#F2CF7A", anchor="ma")
    draw.text((128, 134), "ALEX'S MOBS PORT", font=small, fill="#DCE8D8", anchor="ma")
    draw.text((128, 186), f"{mob_count} MOBS", font=font, fill="#FFFFFF", anchor="ma")
    icon = OUT / "pack_icon.png"
    image.save(icon)
    shutil.copyfile(icon, BP / "pack_icon.png")
    shutil.copyfile(icon, RP / "pack_icon.png")

    output = ROOT / "NeosMoreMobs_AlexsMobsPort.mcaddon"
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for pack in (BP, RP):
            for path in pack.rglob("*"):
                if path.is_file():
                    zf.write(path, str(path.relative_to(OUT)))
        zf.write(OUT / "LICENSE.txt", "LICENSE.txt")
    print(output, mob_count, "mobs")


if __name__ == "__main__":
    main()
