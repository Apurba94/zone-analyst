/**
 * Combat mathematics — the workbook, as a module.
 *
 * DATA HEALTH WARNING, carried through to the UI on purpose:
 * PUBG Mobile publishes no weapon statistics. The game exposes a power bar and
 * nothing else. Every figure below came from community private-lobby testing,
 * the sources contradict each other (two PUBG Mobile sources put the M416 at 41
 * and 43 base damage), and reload times could not be sourced for PUBG Mobile
 * for most weapons. Rows carry their own confidence grade, and `null` means a
 * genuine gap rather than a zero.
 *
 * Nothing here depends on those numbers being right. Every conclusion is a
 * function of the database, so measured values replace these and the answers
 * update.
 */

export type WeaponClass = 'AR' | 'DMR' | 'SR' | 'SMG' | 'LMG' | 'SG' | 'PIS';
export type Confidence = 'Medium' | 'Low' | 'UNMEASURED';

export type Weapon = {
  name: string;
  cls: WeaponClass;
  ammo: string;
  dmg: number | null;
  dmgAlt: number | null;
  mag: number | null;
  ext: number | null;
  reload: number | null;
  rof: number | null;
  /** Usable in a clutch, i.e. inside roughly 30 m. */
  closeUsable: boolean;
  src: string;
  conf: Confidence;
  note: string;
};

export const WEAPONS: Weapon[] = [
  { name: 'M416', cls: 'AR', ammo: '5.56', dmg: 43, dmgAlt: 41, mag: 30, ext: 40, reload: 2.1, rof: 0.085, closeUsable: true, src: 'zilliongamer; Liquipedia PUBGM', conf: 'Medium', note: 'Two PUBGM sources disagree on damage (43 vs 41).' },
  { name: 'SCAR-L', cls: 'AR', ammo: '5.56', dmg: 43, dmgAlt: 41, mag: 30, ext: 40, reload: 2.2, rof: 0.096, closeUsable: true, src: 'zilliongamer; Liquipedia PUBGM', conf: 'Medium', note: 'Lower recoil, slightly slower to kill.' },
  { name: 'G36C', cls: 'AR', ammo: '5.56', dmg: 43, dmgAlt: 41, mag: 30, ext: 40, reload: 3.8, rof: 0.086, closeUsable: true, src: 'zilliongamer; Liquipedia PUBGM', conf: 'Medium', note: 'Worst reload in the class. Never be caught empty.' },
  { name: 'QBZ95', cls: 'AR', ammo: '5.56', dmg: 43, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.092, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Sanhok. Reload not sourced.' },
  { name: 'AUG A3', cls: 'AR', ammo: '5.56', dmg: 43, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.0827, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Crate weapon. Reload not sourced.' },
  { name: 'M16A4', cls: 'AR', ammo: '5.56', dmg: 43, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.075, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Burst only. Reload not sourced.' },
  { name: 'AKM', cls: 'AR', ammo: '7.62', dmg: 49, dmgAlt: null, mag: 30, ext: 40, reload: 2.9, rof: 0.1, closeUsable: true, src: 'zilliongamer; Liquipedia PUBG(PC)', conf: 'Low', note: 'Reload is from the PC wiki, not PUBGM. Verify.' },
  { name: 'Beryl M762', cls: 'AR', ammo: '7.62', dmg: 47, dmgAlt: null, mag: 30, ext: 40, reload: 2.9, rof: 0.086, closeUsable: true, src: 'zilliongamer; Liquipedia PUBG(PC)', conf: 'Low', note: 'Reload is from the PC wiki, not PUBGM. Verify.' },
  { name: 'Mk47 Mutant', cls: 'AR', ammo: '7.62', dmg: 49, dmgAlt: null, mag: 20, ext: 30, reload: 3.36, rof: 0.1, closeUsable: true, src: 'zilliongamer; Liquipedia PUBG(PC)', conf: 'Low', note: 'Burst/single only. Reload from PC wiki.' },
  { name: 'Groza', cls: 'AR', ammo: '7.62', dmg: 49, dmgAlt: null, mag: 30, ext: null, reload: null, rof: 0.08, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Crate. No extended mag. Reload not sourced.' },

  { name: 'Mini14', cls: 'DMR', ammo: '5.56', dmg: 53, dmgAlt: null, mag: 20, ext: 30, reload: null, rof: 0.1, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Flattest DMR. Reload not sourced.' },
  { name: 'QBU', cls: 'DMR', ammo: '5.56', dmg: 53, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.1, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Sanhok. Reload not sourced.' },
  { name: 'SKS', cls: 'DMR', ammo: '7.62', dmg: 56, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.1, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Reload not sourced.' },
  { name: 'SLR', cls: 'DMR', ammo: '7.62', dmg: 58, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.1, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Hits harder than the Mini14, more kick.' },
  { name: 'Mk14 EBR', cls: 'DMR', ammo: '7.62', dmg: 61, dmgAlt: null, mag: 10, ext: 20, reload: 3.683, rof: 0.09, closeUsable: false, src: 'zilliongamer; Sportskeeda PUBGM', conf: 'Medium', note: 'Crate. Reload corroborated by a PUBGM source.' },
  { name: 'VSS', cls: 'DMR', ammo: '9mm', dmg: 40, dmgAlt: null, mag: 10, ext: 20, reload: null, rof: 0.086, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Integral suppressor. Reload not sourced.' },

  { name: 'Kar98k', cls: 'SR', ammo: '7.62', dmg: 74, dmgAlt: null, mag: 5, ext: null, reload: null, rof: 1.9, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Bolt action. Reload not sourced.' },
  { name: 'M24', cls: 'SR', ammo: '7.62', dmg: 79, dmgAlt: null, mag: 5, ext: 7, reload: null, rof: 1.9, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Bolt action. Reload not sourced.' },
  { name: 'AWM', cls: 'SR', ammo: '.300', dmg: 105, dmgAlt: null, mag: 5, ext: 7, reload: null, rof: 1.85, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'Crate. Reload not sourced.' },
  { name: 'Win94', cls: 'SR', ammo: '.45', dmg: 66, dmgAlt: null, mag: 8, ext: null, reload: null, rof: 0.6, closeUsable: false, src: 'zilliongamer', conf: 'Low', note: 'No scope slot. Reload not sourced.' },

  { name: 'UMP45', cls: 'SMG', ammo: '.45', dmg: 39, dmgAlt: null, mag: 25, ext: 35, reload: null, rof: 0.092, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'The balanced SMG. Reload not sourced.' },
  { name: 'Vector', cls: 'SMG', ammo: '.45', dmg: 35, dmgAlt: null, mag: 19, ext: 33, reload: null, rof: 0.055, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Base mag disputed (13 vs 19). Verify both.' },
  { name: 'Micro Uzi', cls: 'SMG', ammo: '9mm', dmg: 26, dmgAlt: null, mag: 25, ext: 35, reload: null, rof: 0.048, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Fastest fire rate in the game.' },
  { name: 'Thompson', cls: 'SMG', ammo: '.45', dmg: 39, dmgAlt: null, mag: 30, ext: 50, reload: null, rof: 0.086, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'No muzzle slot. Reload not sourced.' },
  { name: 'PP-19 Bizon', cls: 'SMG', ammo: '9mm', dmg: 36, dmgAlt: null, mag: 53, ext: null, reload: null, rof: 0.086, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Huge base mag, no extended.' },
  { name: 'MP5K', cls: 'SMG', ammo: '9mm', dmg: null, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: 0.067, closeUsable: true, src: 'not sourced', conf: 'UNMEASURED', note: 'Vikendi. No PUBGM damage figure sourced.' },
  { name: 'JS9', cls: 'SMG', ammo: '9mm', dmg: null, dmgAlt: null, mag: 30, ext: 40, reload: null, rof: null, closeUsable: true, src: 'not sourced', conf: 'UNMEASURED', note: 'Rondo-exclusive. No PUBGM figures sourced.' },

  { name: 'DP-28', cls: 'LMG', ammo: '7.62', dmg: 49, dmgAlt: null, mag: 47, ext: null, reload: null, rof: 0.109, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Largest usable second magazine. Loud.' },
  { name: 'M249', cls: 'LMG', ammo: '5.56', dmg: 47, dmgAlt: null, mag: 100, ext: null, reload: null, rof: 0.075, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Crate. Reload not sourced.' },

  { name: 'S12K', cls: 'SG', ammo: '12ga', dmg: 195, dmgAlt: null, mag: 5, ext: 8, reload: null, rof: 0.25, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Damage is TOTAL pellet damage, not per pellet.' },
  { name: 'S1897', cls: 'SG', ammo: '12ga', dmg: 206, dmgAlt: null, mag: 5, ext: 7, reload: null, rof: 0.75, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Damage is TOTAL pellet damage, not per pellet.' },
  { name: 'S686', cls: 'SG', ammo: '12ga', dmg: 216, dmgAlt: null, mag: 2, ext: null, reload: null, rof: 0.2, closeUsable: true, src: 'zilliongamer', conf: 'Low', note: 'Damage is TOTAL pellet damage, not per pellet.' },
];

export type FightInputs = {
  /** Knock threshold. In squads a downed player is out of the fight at 0 HP. */
  hp: number;
  /** Fraction of damage removed by the vest. Unverified — measure it. */
  armour: number;
  /** 1.0 = torso. Real fights are mostly torso. */
  mult: number;
  /** Fraction of fired rounds that connect. Pull it from your own replays. */
  hitRate: number;
  /** Seconds to swap weapons. The double-gun case scales with this number. */
  swap: number;
  enemies: number;
};

export const DEFAULT_INPUTS: FightInputs = {
  hp: 100,
  armour: 0.4,
  mult: 1.0,
  hitRate: 0.4,
  swap: 0.65,
  enemies: 4,
};

export type FightRow = {
  w: Weapon;
  effective: number | null;
  hitsToKnock: number | null;
  roundsToFire: number | null;
  extMag: number | null;
  knocksPerMag: number | null;
};

/**
 * Round up with a tolerance, matching spreadsheet CEILING semantics.
 *
 * Dividing by a hit rate such as 0.35 can land a hair above an exact integer in
 * floating point (40.00000000000001), and a bare Math.ceil would then demand a
 * round that never needs firing. The workbook and this module must agree.
 */
const ceil = (x: number) => Math.ceil(x - 1e-9);

export function fightMath(w: Weapon, i: FightInputs): FightRow {
  if (w.dmg === null) return { w, effective: null, hitsToKnock: null, roundsToFire: null, extMag: w.ext ?? w.mag, knocksPerMag: null };
  const effective = w.dmg * i.mult * (1 - i.armour);
  const hitsToKnock = ceil(i.hp / effective);
  const roundsToFire = ceil(hitsToKnock / i.hitRate);
  const extMag = w.ext ?? w.mag;
  const knocksPerMag = extMag !== null ? (extMag * i.hitRate) / hitsToKnock : null;
  return { w, effective, hitsToKnock, roundsToFire, extMag, knocksPerMag };
}

export type Budget = {
  hitsOne: number;
  hitsAll: number;
  roundsNeeded: number;
  magCapacity: number | null;
  margin: number | null;
  verdict: string;
  tone: 'bad' | 'warn' | 'ok';
};

export function budget(w: Weapon, i: FightInputs): Budget | null {
  const row = fightMath(w, i);
  if (row.hitsToKnock === null || row.roundsToFire === null) return null;
  const hitsAll = row.hitsToKnock * i.enemies;
  const roundsNeeded = ceil(hitsAll / i.hitRate);
  const magCapacity = row.extMag;
  const margin = magCapacity !== null ? magCapacity - roundsNeeded : null;

  let verdict: string;
  let tone: Budget['tone'];
  if (margin === null) {
    verdict = 'No magazine size on record for this weapon.';
    tone = 'warn';
  } else if (margin < 0) {
    verdict = `Short by ${Math.abs(margin)} rounds. One gun cannot finish this fight — you will be reloading in front of three people.`;
    tone = 'bad';
  } else if (margin <= 8) {
    verdict = `Covered by ${margin} rounds. That is not a margin. One missed burst, one enemy who heals, or Level 3 armour and you are short.`;
    tone = 'warn';
  } else {
    verdict = `Covered with ${margin} rounds to spare under these assumptions. Check the grid before believing it.`;
    tone = 'ok';
  }
  return { hitsOne: row.hitsToKnock, hitsAll, roundsNeeded, magCapacity, margin, verdict, tone };
}

export const ARMOUR_LEVELS = [
  { label: 'Lv1', v: 0.3 },
  { label: 'Lv2', v: 0.4 },
  { label: 'Lv3', v: 0.55 },
];
export const HIT_RATES = [0.2, 0.25, 0.3, 0.35, 0.4, 0.5];

/**
 * Rounds that must be fired, across hit rate and enemy armour.
 *
 * This grid is the real answer, not the single headline number. Against Level 3
 * armour one gun does not cover a 1v4 at any hit rate here — and Level 3 is
 * what you face in the late circles, which is exactly where clutches happen.
 */
export function sensitivityGrid(w: Weapon, i: FightInputs): (number | null)[][] {
  if (w.dmg === null) return HIT_RATES.map(() => ARMOUR_LEVELS.map(() => null));
  return HIT_RATES.map((hr) =>
    ARMOUR_LEVELS.map((a) => {
      const eff = w.dmg! * i.mult * (1 - a.v);
      const hits = ceil(i.hp / eff);
      return ceil((hits * i.enemies) / hr);
    })
  );
}

export type Pair = { a: string; b: string; label: string; note: string };

export const PAIRS: Pair[] = [
  { a: 'M416', b: 'Beryl M762', label: 'AR + AR', note: 'Most controllable rifle with the highest close output.' },
  { a: 'M416', b: 'AKM', label: 'AR + AR', note: 'Same logic, higher per-bullet damage on the second gun.' },
  { a: 'M416', b: 'Groza', label: 'AR + AR', note: 'Best case if the crate lands. No extended mag on the Groza.' },
  { a: 'M416', b: 'UMP45', label: 'AR + SMG', note: 'Lighter on ammo weight, very controllable indoors.' },
  { a: 'M416', b: 'Vector', label: 'AR + SMG', note: 'Highest close burst, smallest magazine. Verify the base mag.' },
  { a: 'M416', b: 'DP-28', label: 'AR + LMG', note: 'Largest margin on the sheet. Slow swap, and very loud.' },
  { a: 'M416', b: 'Mini14', label: 'AR + DMR', note: 'The standard team loadout. Weak inside 30 m.' },
  { a: 'M416', b: 'SLR', label: 'AR + DMR', note: 'Team loadout. Ten rounds of usable clutch ammunition.' },
  { a: 'M416', b: 'Kar98k', label: 'AR + SR', note: 'The sniper contributes almost nothing in a clutch.' },
  { a: 'Beryl M762', b: 'UMP45', label: 'AR + SMG', note: 'Aggressive entry build.' },
];

export type PairResult = {
  pair: Pair;
  bothUsable: boolean;
  roundsA: number | null;
  roundsB: number | null;
  total: number | null;
  needed: number;
  margin: number | null;
  swapSaves: number | null;
};

const byName = (n: string) => WEAPONS.find((w) => w.name === n);

export function pairAnalysis(i: FightInputs, testWeapon = 'M416'): PairResult[] {
  const base = byName(testWeapon) ?? WEAPONS[0];
  const b = budget(base, i);
  const needed = b?.roundsNeeded ?? 0;

  return PAIRS.map((pair) => {
    const wa = byName(pair.a);
    const wb = byName(pair.b);
    const roundsA = wa ? wa.ext ?? wa.mag : null;
    const roundsB = wb ? wb.ext ?? wb.mag : null;
    const bothUsable = !!wa?.closeUsable && !!wb?.closeUsable;
    // Rounds on a gun you cannot shoot at 15 metres are not rounds.
    const total = roundsA === null ? null : roundsA + (bothUsable && roundsB !== null ? roundsB : 0);
    return {
      pair,
      bothUsable,
      roundsA,
      roundsB,
      total,
      needed,
      margin: total === null ? null : total - needed,
      swapSaves: wa?.reload != null ? +(wa.reload - i.swap).toFixed(2) : null,
    };
  }).sort((x, y) => (y.margin ?? -1e9) - (x.margin ?? -1e9));
}
