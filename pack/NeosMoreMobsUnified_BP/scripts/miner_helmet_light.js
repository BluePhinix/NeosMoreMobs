
import { world, system } from "@minecraft/server";

const HELMET_ID = "neosmoremobs:miner_helmet";
const LIGHT_ID = "minecraft:light_block_15";
const SAVE_KEY = "neosmoremobs:miner_helmet_lights";
const PLAYER_INTERVAL = 5;
const MOB_EVERY = 2;
const MOB_RANGE = 40;

const lights = new Map();
let dirty = false;
let tick = 0;

function key3(loc) {
  return `${Math.floor(loc.x)},${Math.floor(loc.y)},${Math.floor(loc.z)}`;
}

function removeTracked(info) {
  try {
    const dim = world.getDimension(info.dimensionId);
    const loc = { x: info.x, y: info.y, z: info.z };
    const block = dim.getBlock(loc);
    if (block && typeof block.typeId === "string" && block.typeId.startsWith("minecraft:light_block")) {
      dim.setBlockType(loc, "minecraft:air");
    }
  } catch {
    /* chunk not loaded */
  }
}

function clearLight(key) {
  const prev = lights.get(key);
  if (!prev) return;
  removeTracked(prev);
  lights.delete(key);
  dirty = true;
}

function isDark(dimension, loc) {
  if (dimension.id !== "minecraft:overworld") return true;
  try {
    const hit = dimension.getBlockFromRay(
      { x: loc.x, y: loc.y + 1.62, z: loc.z },
      { x: 0, y: 1, z: 0 },
      { maxDistance: 320, includeLiquidBlocks: false, includePassableBlocks: false }
    );
    if (hit && hit.block && hit.block.typeId !== "minecraft:air") return true;
  } catch {
    /* unloaded chunk */
  }
  let time = 0;
  try { time = world.getTimeOfDay(); } catch {}
  return time >= 13000 && time <= 23000;
}

function placeLight(key, dimension, loc) {
  const candidates = [
    { x: Math.floor(loc.x), y: Math.floor(loc.y), z: Math.floor(loc.z) },
    { x: Math.floor(loc.x), y: Math.floor(loc.y) + 1, z: Math.floor(loc.z) },
  ];
  let target = undefined;
  for (const candidate of candidates) {
    try {
      const block = dimension.getBlock(candidate);
      if (block && block.typeId === "minecraft:air") { target = candidate; break; }
    } catch {
      return;
    }
  }
  if (!target) return;
  const prev = lights.get(key);
  if (prev && prev.dimensionId === dimension.id &&
      prev.x === target.x && prev.y === target.y && prev.z === target.z) {
    try {
      const block = dimension.getBlock(target);
      if (block && typeof block.typeId === "string" &&
          block.typeId.startsWith("minecraft:light_block")) return;
    } catch {
      return;
    }
  }
  try {
    dimension.setBlockType(target, LIGHT_ID);
  } catch {
    return;
  }
  if (prev) removeTracked(prev);
  lights.set(key, { dimensionId: dimension.id, x: target.x, y: target.y, z: target.z });
  dirty = true;
}

function persist() {
  try {
    world.setDynamicProperty(SAVE_KEY, JSON.stringify([...lights.values()]));
  } catch {}
}

function cleanupStale() {
  try {
    const raw = world.getDynamicProperty(SAVE_KEY);
    if (typeof raw === "string" && raw.length > 2) {
      for (const info of JSON.parse(raw)) removeTracked(info);
    }
    world.setDynamicProperty(SAVE_KEY, "[]");
  } catch {}
}

system.run(cleanupStale);

world.afterEvents.playerLeave.subscribe((event) => {
  try { clearLight("p:" + event.playerId); } catch {}
  persist();
});

system.runInterval(() => {
  tick++;
  const players = world.getPlayers();
  for (const player of players) {
    let wearing = false;
    try {
      const equippable = player.getComponent("minecraft:equippable");
      const helmet = equippable ? equippable.getEquipment("Head") : undefined;
      wearing = !!helmet && helmet.typeId === HELMET_ID;
    } catch {}
    if (wearing && isDark(player.dimension, player.location)) {
      placeLight("p:" + player.id, player.dimension, player.location);
    } else {
      clearLight("p:" + player.id);
    }
  }

  if (tick % MOB_EVERY === 0) {
    const seen = new Set();
    for (const player of players) {
      let mobs = [];
      try {
        mobs = player.dimension.getEntities({
          type: "neosmoremobs:miner_zombie",
          location: player.location,
          maxDistance: MOB_RANGE,
        });
      } catch {}
      for (const mob of mobs) {
        const key = "e:" + mob.id;
        if (seen.has(key)) continue;
        seen.add(key);
        try {
          if (isDark(mob.dimension, mob.location)) {
            placeLight(key, mob.dimension, mob.location);
          } else {
            clearLight(key);
          }
        } catch {}
      }
    }
    for (const key of [...lights.keys()]) {
      if (key.startsWith("e:") && !seen.has(key)) clearLight(key);
    }
  }

  if (dirty) { persist(); dirty = false; }
}, PLAYER_INTERVAL);
