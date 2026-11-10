#!/usr/bin/env python3
"""Render 10 fps animation GIFs for the original (non-port) mobs."""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = "/workspace/Neo's more mobs"
MODELS = os.path.join(ROOT, "work/qa/frames_models")
FRAMES = os.path.join(ROOT, "work/qa/anim_frames")
OUT = os.path.join(ROOT, "work/qa/anim_gifs")
RENDER = os.path.join(ROOT, "work/render_frames.mjs")
SUN = "/workspace/project/sun"
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)


def frame_count(length):
    loops = max(1, round(10.0 / length))
    return min(140, max(20, round(loops * length * 10)))


def render(mob, clip, length):
    out = os.path.join(FRAMES, f"{mob}_{clip}")
    count = frame_count(length)
    subprocess.run(
        ["node", RENDER, os.path.join(MODELS, f"{mob}.bbmodel"), clip, out,
         str(count), "10", "256", "35", "18"],
        cwd=SUN, check=True, stdout=subprocess.DEVNULL,
    )
    return out, count


def frames(folder):
    return [Image.open(os.path.join(folder, f)).convert("RGB")
            for f in sorted(os.listdir(folder)) if f.endswith(".png")]


def save_gif(images, path):
    images[0].save(path, save_all=True, append_images=images[1:],
                   duration=100, loop=0, optimize=True)


def label(images, text):
    out = []
    for im in images:
        d = ImageDraw.Draw(im)
        d.rectangle((3, 3, 3 + 8 * len(text), 26), fill=(10, 8, 16))
        d.text((6, 4), text, font=FONT, fill=(255, 220, 80))
        out.append(im)
    return out


def main(mobs):
    os.makedirs(OUT, exist_ok=True)
    for mob in mobs:
        doc = json.load(open(os.path.join(MODELS, f"{mob}.bbmodel")))
        clips = {a["name"]: a["length"] for a in doc["animations"]}
        rendered = {}
        for clip in ("idle", "walk"):
            if clip not in clips:
                continue
            folder, count = render(mob, clip, clips[clip])
            rendered[clip] = frames(folder)
            save_gif(rendered[clip], os.path.join(OUT, f"{mob}_{clip}.gif"))
            print(f"{mob} {clip}: {count} frames")
        if "idle" in rendered and "walk" in rendered:
            combined = (label(rendered["idle"][:40], "IDLE")
                        + label(rendered["walk"][:60], "WALK"))
            save_gif(combined, os.path.join(OUT, f"{mob}_idle_then_walk.gif"))
            print(f"{mob} combined gif")
    print("done", ", ".join(mobs))


if __name__ == "__main__":
    main(sys.argv[1:])
