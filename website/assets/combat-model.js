/* GENERATED from mobile-app/src/combat.ts — do not edit by hand. Rebuild: npx esbuild mobile-app/src/combat.ts --bundle --format=iife --global-name=ZoneCombat --target=es2019 --outfile=website/assets/combat-model.js */
"use strict";
var ZoneCombat = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // ../../../../../../home/claude/zone-analyst/mobile-app/src/combat.ts
  var combat_exports = {};
  __export(combat_exports, {
    ARMOUR_LEVELS: () => ARMOUR_LEVELS,
    DEFAULT_INPUTS: () => DEFAULT_INPUTS,
    HIT_RATES: () => HIT_RATES,
    PAIRS: () => PAIRS,
    WEAPONS: () => WEAPONS,
    budget: () => budget,
    fightMath: () => fightMath,
    pairAnalysis: () => pairAnalysis,
    sensitivityGrid: () => sensitivityGrid
  });
  var WEAPONS = [
    { name: "M416", cls: "AR", ammo: "5.56", dmg: 43, dmgAlt: 41, mag: 30, ext: 40, reload: 2.1, rof: 0.085, closeUsable: true, src: "zilliongamer; Liquipedia PUBGM", conf: "Medium", note: "Two PUBGM sources disagree on damage (43 vs 41)." },
    { name: "SCAR-L", cls: "AR", ammo: "5.56", dmg: 43, dmgAlt: 41, mag: 30, ext: 40, reload: 2.2, rof: 0.096, closeUsable: true, src: "zilliongamer; Liquipedia PUBGM", conf: "Medium", note: "Lower recoil, slightly slower to kill." },
    { name: "G36C", cls: "AR", ammo: "5.56", dmg: 43, dmgAlt: 41, mag: 30, ext: 40, reload: 3.8, rof: 0.086, closeUsable: true, src: "zilliongamer; Liquipedia PUBGM", conf: "Medium", note: "Worst reload in the class. Never be caught empty." },
    { name: "QBZ95", cls: "AR", ammo: "5.56", dmg: 43, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.092, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Sanhok. Reload not sourced." },
    { name: "AUG A3", cls: "AR", ammo: "5.56", dmg: 43, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.0827, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Crate weapon. Reload not sourced." },
    { name: "M16A4", cls: "AR", ammo: "5.56", dmg: 43, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.075, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Burst only. Reload not sourced." },
    { name: "AKM", cls: "AR", ammo: "7.62", dmg: 49, dmgAlt: null, mag: 30, ext: 40, reload: 2.9, rof: 0.1, closeUsable: true, src: "zilliongamer; Liquipedia PUBG(PC)", conf: "Low", note: "Reload is from the PC wiki, not PUBGM. Verify." },
    { name: "Beryl M762", cls: "AR", ammo: "7.62", dmg: 47, dmgAlt: null, mag: 30, ext: 40, reload: 2.9, rof: 0.086, closeUsable: true, src: "zilliongamer; Liquipedia PUBG(PC)", conf: "Low", note: "Reload is from the PC wiki, not PUBGM. Verify." },
    { name: "Mk47 Mutant", cls: "AR", ammo: "7.62", dmg: 49, dmgAlt: null, mag: 20, ext: 30, reload: 3.36, rof: 0.1, closeUsable: true, src: "zilliongamer; Liquipedia PUBG(PC)", conf: "Low", note: "Burst/single only. Reload from PC wiki." },
    { name: "Groza", cls: "AR", ammo: "7.62", dmg: 49, dmgAlt: null, mag: 30, ext: null, reload: null, rof: 0.08, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Crate. No extended mag. Reload not sourced." },
    { name: "Mini14", cls: "DMR", ammo: "5.56", dmg: 53, dmgAlt: null, mag: 20, ext: 30, reload: null, rof: 0.1, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Flattest DMR. Reload not sourced." },
    { name: "QBU", cls: "DMR", ammo: "5.56", dmg: 53, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.1, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Sanhok. Reload not sourced." },
    { name: "SKS", cls: "DMR", ammo: "7.62", dmg: 56, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.1, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Reload not sourced." },
    { name: "SLR", cls: "DMR", ammo: "7.62", dmg: 58, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.1, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Hits harder than the Mini14, more kick." },
    { name: "Mk14 EBR", cls: "DMR", ammo: "7.62", dmg: 61, dmgAlt: null, mag: 10, ext: 20, reload: 3.683, rof: 0.09, closeUsable: false, src: "zilliongamer; Sportskeeda PUBGM", conf: "Medium", note: "Crate. Reload corroborated by a PUBGM source." },
    { name: "VSS", cls: "DMR", ammo: "9mm", dmg: 40, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.086, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Integral suppressor. Reload not sourced." },
    { name: "Kar98k", cls: "SR", ammo: "7.62", dmg: 74, dmgAlt: null, mag: 5, ext: null, reload: null, rof: 1.9, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Bolt action. Reload not sourced." },
    { name: "M24", cls: "SR", ammo: "7.62", dmg: 79, dmgAlt: null, mag: 5, ext: 7, reload: null, rof: 1.9, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Bolt action. Reload not sourced." },
    { name: "AWM", cls: "SR", ammo: ".300", dmg: 105, dmgAlt: null, mag: 5, ext: 7, reload: null, rof: 1.85, closeUsable: false, src: "zilliongamer", conf: "Low", note: "Crate. Reload not sourced." },
    { name: "Win94", cls: "SR", ammo: ".45", dmg: 66, dmgAlt: null, mag: 8, ext: null, reload: null, rof: 0.6, closeUsable: false, src: "zilliongamer", conf: "Low", note: "No scope slot. Reload not sourced." },
    { name: "UMP45", cls: "SMG", ammo: ".45", dmg: 39, dmgAlt: null, mag: 25, ext: 35, reload: null, rof: 0.092, closeUsable: true, src: "zilliongamer", conf: "Low", note: "The balanced SMG. Reload not sourced." },
    { name: "Vector", cls: "SMG", ammo: ".45", dmg: 35, dmgAlt: null, mag: 19, ext: 33, reload: null, rof: 0.055, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Base mag disputed (13 vs 19). Verify both." },
    { name: "Micro Uzi", cls: "SMG", ammo: "9mm", dmg: 26, dmgAlt: null, mag: 25, ext: 35, reload: null, rof: 0.048, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Fastest fire rate in the game." },
    { name: "Thompson", cls: "SMG", ammo: ".45", dmg: 39, dmgAlt: null, mag: 30, ext: 50, reload: null, rof: 0.086, closeUsable: true, src: "zilliongamer", conf: "Low", note: "No muzzle slot. Reload not sourced." },
    { name: "PP-19 Bizon", cls: "SMG", ammo: "9mm", dmg: 36, dmgAlt: null, mag: 53, ext: null, reload: null, rof: 0.086, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Huge base mag, no extended." },
    { name: "MP5K", cls: "SMG", ammo: "9mm", dmg: null, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.067, closeUsable: true, src: "not sourced", conf: "UNMEASURED", note: "Vikendi. No PUBGM damage figure sourced." },
    { name: "JS9", cls: "SMG", ammo: "9mm", dmg: null, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: null, closeUsable: true, src: "not sourced", conf: "UNMEASURED", note: "Rondo-exclusive. No PUBGM figures sourced." },
    { name: "DP-28", cls: "LMG", ammo: "7.62", dmg: 49, dmgAlt: null, mag: 47, ext: null, reload: null, rof: 0.109, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Largest usable second magazine. Loud." },
    { name: "M249", cls: "LMG", ammo: "5.56", dmg: 47, dmgAlt: null, mag: 100, ext: null, reload: null, rof: 0.075, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Crate. Reload not sourced." },
    { name: "S12K", cls: "SG", ammo: "12ga", dmg: 195, dmgAlt: null, mag: 5, ext: 8, reload: null, rof: 0.25, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Damage is TOTAL pellet damage, not per pellet." },
    { name: "S1897", cls: "SG", ammo: "12ga", dmg: 206, dmgAlt: null, mag: 5, ext: 7, reload: null, rof: 0.75, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Damage is TOTAL pellet damage, not per pellet." },
    { name: "S686", cls: "SG", ammo: "12ga", dmg: 216, dmgAlt: null, mag: 2, ext: null, reload: null, rof: 0.2, closeUsable: true, src: "zilliongamer", conf: "Low", note: "Damage is TOTAL pellet damage, not per pellet." }
  ];
  var DEFAULT_INPUTS = {
    hp: 100,
    armour: 0.4,
    mult: 1,
    hitRate: 0.4,
    swap: 0.65,
    enemies: 4
  };
  var ceil = (x) => Math.ceil(x - 1e-9);
  function fightMath(w, i) {
    var _a, _b;
    if (w.dmg === null) return { w, effective: null, hitsToKnock: null, roundsToFire: null, extMag: (_a = w.ext) != null ? _a : w.mag, knocksPerMag: null };
    const effective = w.dmg * i.mult * (1 - i.armour);
    const hitsToKnock = ceil(i.hp / effective);
    const roundsToFire = ceil(hitsToKnock / i.hitRate);
    const extMag = (_b = w.ext) != null ? _b : w.mag;
    const knocksPerMag = extMag !== null ? extMag * i.hitRate / hitsToKnock : null;
    return { w, effective, hitsToKnock, roundsToFire, extMag, knocksPerMag };
  }
  function budget(w, i) {
    const row = fightMath(w, i);
    if (row.hitsToKnock === null || row.roundsToFire === null) return null;
    const hitsAll = row.hitsToKnock * i.enemies;
    const roundsNeeded = ceil(hitsAll / i.hitRate);
    const magCapacity = row.extMag;
    const margin = magCapacity !== null ? magCapacity - roundsNeeded : null;
    let verdict;
    let tone;
    if (margin === null) {
      verdict = "No magazine size on record for this weapon.";
      tone = "warn";
    } else if (margin < 0) {
      verdict = `Short by ${Math.abs(margin)} rounds. One gun cannot finish this fight \u2014 you will be reloading in front of three people.`;
      tone = "bad";
    } else if (margin <= 8) {
      verdict = `Covered by ${margin} rounds. That is not a margin. One missed burst, one enemy who heals, or Level 3 armour and you are short.`;
      tone = "warn";
    } else {
      verdict = `Covered with ${margin} rounds to spare under these assumptions. Check the grid before believing it.`;
      tone = "ok";
    }
    return { hitsOne: row.hitsToKnock, hitsAll, roundsNeeded, magCapacity, margin, verdict, tone };
  }
  var ARMOUR_LEVELS = [
    { label: "Lv1", v: 0.3 },
    { label: "Lv2", v: 0.4 },
    { label: "Lv3", v: 0.55 }
  ];
  var HIT_RATES = [0.2, 0.25, 0.3, 0.35, 0.4, 0.5];
  function sensitivityGrid(w, i) {
    if (w.dmg === null) return HIT_RATES.map(() => ARMOUR_LEVELS.map(() => null));
    return HIT_RATES.map(
      (hr) => ARMOUR_LEVELS.map((a) => {
        const eff = w.dmg * i.mult * (1 - a.v);
        const hits = ceil(i.hp / eff);
        return ceil(hits * i.enemies / hr);
      })
    );
  }
  var PAIRS = [
    { a: "M416", b: "Beryl M762", label: "AR + AR", note: "Most controllable rifle with the highest close output." },
    { a: "M416", b: "AKM", label: "AR + AR", note: "Same logic, higher per-bullet damage on the second gun." },
    { a: "M416", b: "Groza", label: "AR + AR", note: "Best case if the crate lands. No extended mag on the Groza." },
    { a: "M416", b: "UMP45", label: "AR + SMG", note: "Lighter on ammo weight, very controllable indoors." },
    { a: "M416", b: "Vector", label: "AR + SMG", note: "Highest close burst, smallest magazine. Verify the base mag." },
    { a: "M416", b: "DP-28", label: "AR + LMG", note: "Largest margin on the sheet. Slow swap, and very loud." },
    { a: "M416", b: "Mini14", label: "AR + DMR", note: "The standard team loadout. Weak inside 30 m." },
    { a: "M416", b: "SLR", label: "AR + DMR", note: "Team loadout. Ten rounds of usable clutch ammunition." },
    { a: "M416", b: "Kar98k", label: "AR + SR", note: "The sniper contributes almost nothing in a clutch." },
    { a: "Beryl M762", b: "UMP45", label: "AR + SMG", note: "Aggressive entry build." }
  ];
  var byName = (n) => WEAPONS.find((w) => w.name === n);
  function pairAnalysis(i, testWeapon = "M416") {
    var _a, _b;
    const base = (_a = byName(testWeapon)) != null ? _a : WEAPONS[0];
    const b = budget(base, i);
    const needed = (_b = b == null ? void 0 : b.roundsNeeded) != null ? _b : 0;
    return PAIRS.map((pair) => {
      var _a2, _b2;
      const wa = byName(pair.a);
      const wb = byName(pair.b);
      const roundsA = wa ? (_a2 = wa.ext) != null ? _a2 : wa.mag : null;
      const roundsB = wb ? (_b2 = wb.ext) != null ? _b2 : wb.mag : null;
      const bothUsable = !!(wa == null ? void 0 : wa.closeUsable) && !!(wb == null ? void 0 : wb.closeUsable);
      const total = roundsA === null ? null : roundsA + (bothUsable && roundsB !== null ? roundsB : 0);
      return {
        pair,
        bothUsable,
        roundsA,
        roundsB,
        total,
        needed,
        margin: total === null ? null : total - needed,
        swapSaves: (wa == null ? void 0 : wa.reload) != null ? +(wa.reload - i.swap).toFixed(2) : null
      };
    }).sort((x, y) => {
      var _a2, _b2;
      return ((_a2 = y.margin) != null ? _a2 : -1e9) - ((_b2 = x.margin) != null ? _b2 : -1e9);
    });
  }
  return __toCommonJS(combat_exports);
})();
