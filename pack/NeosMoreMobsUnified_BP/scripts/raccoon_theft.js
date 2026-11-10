import { world, system, ItemStack } from "@minecraft/server";

const holdState = new Map();
const cooldowns = new Map();
const HOLD_TICKS = 80;
const COOLDOWN_TICKS = 200;
const STEAL_RADIUS = 3.2;

function containerFor(player) {
  return player.getComponent("minecraft:inventory")?.container;
}

function resetHold(player) {
  const container = containerFor(player);
  if (!container) return;
  const item = container.getItem(player.selectedSlotIndex);
  holdState.set(player.id, {
    itemId: item?.typeId ?? "",
    slot: player.selectedSlotIndex,
    since: system.currentTick,
  });
}

world.afterEvents.itemStartUse.subscribe(({ source }) => resetHold(source));
world.afterEvents.itemUse.subscribe(({ source }) => resetHold(source));
world.afterEvents.playerLeave.subscribe(({ playerId }) => holdState.delete(playerId));

world.afterEvents.entityDie.subscribe(({ deadEntity }) => {
  if (deadEntity.typeId !== "alexsmobs:raccoon") return;
  const raw = deadEntity.getDynamicProperty("neosmoremobs:stolen");
  if (typeof raw !== "string") return;
  try {
    for (const entry of JSON.parse(raw)) {
      deadEntity.dimension.spawnItem(new ItemStack(entry.id, entry.amount), deadEntity.location);
    }
  } catch {}
  deadEntity.setDynamicProperty("neosmoremobs:stolen", undefined);
});

system.runInterval(() => {
  const now = system.currentTick;
  for (const player of world.getPlayers()) {
    const container = containerFor(player);
    if (!container) continue;
    const slot = player.selectedSlotIndex;
    const item = container.getItem(slot);
    if (!item) {
      holdState.delete(player.id);
      continue;
    }
    const state = holdState.get(player.id);
    if (!state || state.itemId !== item.typeId || state.slot !== slot) {
      holdState.set(player.id, { itemId: item.typeId, slot, since: now });
      continue;
    }
    if (now - state.since < HOLD_TICKS) continue;
    const raccoons = player.dimension.getEntities({
      type: "alexsmobs:raccoon",
      location: player.location,
      maxDistance: STEAL_RADIUS,
    });
    for (const raccoon of raccoons) {
      if (now - (cooldowns.get(raccoon.id) ?? -COOLDOWN_TICKS) < COOLDOWN_TICKS) continue;
      const stolenItem = item.clone();
      const remaining = item.amount - 1;
      if (remaining <= 0) container.setItem(slot);
      else {
        const stack = item.clone();
        stack.amount = remaining;
        container.setItem(slot, stack);
      }
      let stored = [];
      try {
        const raw = raccoon.getDynamicProperty("neosmoremobs:stolen");
        if (typeof raw === "string") stored = JSON.parse(raw);
      } catch {}
      stored.push({ id: stolenItem.typeId, amount: 1 });
      raccoon.setDynamicProperty("neosmoremobs:stolen", JSON.stringify(stored));
      cooldowns.set(raccoon.id, now);
      holdState.delete(player.id);
      player.onScreenDisplay.setActionBar(`A raccoon stole your ${stolenItem.typeId.replace("minecraft:", "").replaceAll("_", " ")}!`);
      player.dimension.playSound("random.pop", raccoon.location, { volume: 0.7, pitch: 1.25 });
      try {
      } catch {}
      break;
    }
  }
}, 20);
