from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / "work" / "renders"

mobs = [
    ("bear", "GRIZZLY BEAR"),
    ("blackbear", "BLACK BEAR"),
    ("lion", "LION"),
    ("lioness", "LIONESS"),
    ("tiger", "BENGAL TIGER"),
    ("monkey", "CAPUCHIN MONKEY"),
    ("deer", "DEER"),
    ("penguin", "EMPEROR PENGUIN"),
    ("snake", "EMERALD SNAKE"),
    ("crocodile", "CROCODILE"),
    ("shark", "SHARK"),
    ("jelly", "BLUE COMB JELLY"),
    ("elephant", "ELEPHANT"),
    ("bison", "BISON"),
    ("whale", "WHALE"),
    ("scorpion", "SCORPION GIRL"),
    ("giraffe", "GIRAFFE"),
    ("raccoon", "RACCOON"),
    ("platypus", "PLATYPUS"),
    ("kangaroo", "KANGAROO"),
    ("emu", "EMU"),
    ("spider", "AUSTRALIAN SPIDER"),
]

cols = 6
rows = 3
panel = 300
gap_x = 16
gap_y = 42
margin_x = 20
top = 130
label_height = 42
width = margin_x * 2 + cols * panel + (cols - 1) * gap_x
height = top + rows * (panel + gap_y) + 40

image = Image.new("RGBA", (width, height), "#13221d")
draw = ImageDraw.Draw(image)
for y in range(height):
    draw.line((0, y, width, y), fill=("#13221d" if (y // 28) % 2 == 0 else "#172821"))

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title = ImageFont.truetype(font_path, 52)
subtitle = ImageFont.truetype(font_path, 24)
label = ImageFont.truetype(font_path, 19)

draw.text((width // 2, 34), "NEO'S MORE MOBS", font=title, fill="#F4D08A", anchor="ma")
draw.text((width // 2, 96), "22 ANIMATED ANIMALS", font=subtitle, fill="#C9D9C7", anchor="ma")

for index, (key, name) in enumerate(mobs):
    col = index % cols
    row = index // cols
    x = margin_x + col * (panel + gap_x)
    y = top + row * (panel + gap_y)
    source = RENDERS / f"{key}_walk.png"
    if not source.exists():
        source = RENDERS / f"{key}_three-quarter.png"
    if not source.exists():
        continue
    icon = Image.open(source).convert("RGBA").resize((panel, panel), Image.LANCZOS)
    image.alpha_composite(icon, (x, y))
    draw.text((x + panel // 2, y + panel + 16), name, font=label, fill="#DCE8D8", anchor="ma")

image.convert("RGB").save(ROOT / "Neo's More Mobs Preview.jpg", quality=92)
print(ROOT / "Neo's More Mobs Preview.jpg")
