
import { world, system, ItemStack } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";

const OFFERS = [
  { label: "16 Obsidian", cost: 1, item: "minecraft:obsidian", count: 16 },
  { label: "4 Ender Pearls", cost: 1, item: "minecraft:ender_pearl", count: 4 },
  { label: "2 Eyes of Ender", cost: 2, item: "minecraft:ender_eye", count: 2 },
  { label: "1 Ender Chest", cost: 2, item: "minecraft:ender_chest", count: 1 },
  { label: "8 Chorus Fruit", cost: 2, item: "minecraft:chorus_fruit", count: 8 },
  { label: "1 Shulker Shell", cost: 3, item: "minecraft:shulker_shell", count: 1 },
  { label: "1 Netherite Ingot", cost: 5, item: "minecraft:netherite_ingot", count: 1 },
  { label: "1 Totem of Undying", cost: 5, item: "minecraft:totem_of_undying", count: 1 },
];

function containerOf(player) {
  return player.getComponent("minecraft:inventory")?.container;
}

function countItem(container, id) {
  let total = 0;
  for (let i = 0; i < container.size; i++) {
    const item = container.getItem(i);
    if (item?.typeId === id) total += item.amount;
  }
  return total;
}

function takeItem(container, id, amount) {
  let left = amount;
  for (let i = 0; i < container.size && left > 0; i++) {
    const item = container.getItem(i);
    if (item?.typeId !== id) continue;
    const used = Math.min(left, item.amount);
    left -= used;
    if (item.amount === used) container.setItem(i);
    else container.setItem(i, new ItemStack(id, item.amount - used));
  }
  return left === 0;
}

function giveItem(player, id, amount) {
  const container = containerOf(player);
  try {
    const left = container.addItem(new ItemStack(id, amount));
    if (left) player.dimension.spawnItem(left, player.location);
  } catch {
    player.dimension.spawnItem(new ItemStack(id, amount), player.location);
  }
}

function showShop(player, tries = 0) {
  const form = new ActionFormData()
    .title("Void Dealer")
    .body("The void trades. Bring diamonds.");
  for (const offer of OFFERS) {
    form.button(`${offer.label}\n§b${offer.cost} Diamond${offer.cost > 1 ? "s" : ""}`);
  }
  form.show(player).then((res) => {
    if (res.canceled || res.selection === undefined) return;
    const offer = OFFERS[res.selection];
    const container = containerOf(player);
    if (!container || countItem(container, "minecraft:diamond") < offer.cost) {
      player.onScreenDisplay.setActionBar("§cNot enough diamonds.");
      return;
    }
    takeItem(container, "minecraft:diamond", offer.cost);
    giveItem(player, offer.item, offer.count);
    player.onScreenDisplay.setActionBar(`§5Bought ${offer.label}`);
    player.playSound("random.orb", { pitch: 0.8 });
  }).catch(() => {
    if (tries < 2) system.runTimeout(() => showShop(player, tries + 1), 20);
  });
}

world.afterEvents.playerInteractWithEntity.subscribe(({ player, target }) => {
  if (target?.typeId === "neosmoremobs:void_dealer") showShop(player);
});
