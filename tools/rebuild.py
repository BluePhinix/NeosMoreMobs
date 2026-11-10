from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import build
import build_imported

ids = sys.argv[1:]
if not ids:
    raise SystemExit("usage: python3 work/rebuild.py <mob-id> [...]")

for mob_id in ids:
    mob = build.MOB_BY_ID[mob_id]
    print(f"rebuilding {mob_id}", flush=True)
    if "import" in mob:
        build_imported.build_model(mob)
    else:
        build.pack_cubes(mob["cubes"], size=mob.get("texture_size", build.TEX_SIZE))
        build.MOBS = [mob]
        build.build_blockbench_models()
print("done")
