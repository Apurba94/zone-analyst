import React from 'react';
import { View, Text, Pressable, ScrollView, StyleSheet } from 'react-native';
import { usePalette, FONT } from '../src/theme';
import { Screen, H1, Card, Slider, Row, Note, Segmented } from '../src/components/ui';
import {
  WEAPONS, DEFAULT_INPUTS, budget, sensitivityGrid, pairAnalysis, fightMath,
  ARMOUR_LEVELS, HIT_RATES, type FightInputs, type Weapon,
} from '../src/combat';

export default function Combat() {
  const p = usePalette();
  const [i, setI] = React.useState<FightInputs>(DEFAULT_INPUTS);
  const [test, setTest] = React.useState('M416');
  const [tab, setTab] = React.useState<'budget' | 'pairs' | 'db'>('budget');

  const w = WEAPONS.find((x) => x.name === test) ?? WEAPONS[0];
  const b = budget(w, i);
  const grid = sensitivityGrid(w, i);
  const pairs = pairAnalysis(i, test);
  const magCap = b?.magCapacity ?? 0;

  const set = (k: keyof FightInputs) => (v: number) => setI((s) => ({ ...s, [k]: v }));

  return (
    <Screen>
      <H1 sub="Whether a clutch is mechanically possible before skill enters the picture.">
        Combat math
      </H1>

      <Card title="Fight assumptions">
        <Slider label="Enemies to knock" value={i.enemies} min={1} max={4} step={1} onChange={set('enemies')} />
        <Slider label="Armour damage reduction" value={i.armour} min={0.2} max={0.6} step={0.05} onChange={set('armour')} format={(v) => `${(v * 100).toFixed(0)}%`} />
        <Slider label="Hit rate (accuracy)" value={i.hitRate} min={0.15} max={0.6} step={0.05} onChange={set('hitRate')} format={(v) => `${(v * 100).toFixed(0)}%`} />
        <Slider label="Hit location multiplier" value={i.mult} min={0.7} max={1.5} step={0.05} onChange={set('mult')} format={(v) => v.toFixed(2)} />
        <Slider label="Weapon swap time (s)" value={i.swap} min={0.3} max={1.5} step={0.05} onChange={set('swap')} format={(v) => v.toFixed(2)} />
        <Note>
          Armour reduction and swap time are unverified placeholders. Swap time is the one to measure
          first — the whole double-gun case scales with it and nobody publishes it.
        </Note>
      </Card>

      <Card title="Weapon under test">
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={{ flexDirection: 'row', gap: 6 }}>
            {WEAPONS.filter((x) => x.dmg !== null).slice(0, 14).map((x) => (
              <Pressable
                key={x.name}
                onPress={() => setTest(x.name)}
                style={[
                  s.chip,
                  { borderColor: p.rule, backgroundColor: x.name === test ? p.ink : p.paper },
                ]}
              >
                <Text style={[FONT.small, { color: x.name === test ? p.paper : p.inkSoft }]}>{x.name}</Text>
              </Pressable>
            ))}
          </View>
        </ScrollView>
      </Card>

      <Segmented
        value={tab}
        onChange={setTab}
        options={[
          { key: 'budget', label: '1v4 budget' },
          { key: 'pairs', label: 'Double gun' },
          { key: 'db', label: 'Database' },
        ]}
      />
      <View style={{ height: 14 }} />

      {tab === 'budget' && b ? (
        <>
          <Card title={`${w.name} — ammunition budget`}>
            <Row label="Hits to knock one" value={String(b.hitsOne)} />
            <Row label="Hits for the whole squad" value={String(b.hitsAll)} />
            <Row label="Rounds you must FIRE" value={String(b.roundsNeeded)} />
            <Row label="Rounds in an extended mag" value={b.magCapacity === null ? '—' : String(b.magCapacity)} />
            <Row
              label="Margin"
              value={b.margin === null ? '—' : `${b.margin > 0 ? '+' : ''}${b.margin}`}
              tone={b.tone}
            />
            <Text style={[FONT.small, { color: b.tone === 'bad' ? p.caution : b.tone === 'ok' ? p.good : p.warn, marginTop: 10, lineHeight: 19 }]}>
              {b.verdict}
            </Text>
          </Card>

          <Card title="Rounds to fire, by hit rate and armour">
            <View style={[s.gridRow, { borderBottomColor: p.rule, borderBottomWidth: 1, paddingBottom: 5 }]}>
              <Text style={[FONT.small, { color: p.inkSoft, width: 62 }]}>hit rate</Text>
              {ARMOUR_LEVELS.map((a) => (
                <Text key={a.label} style={[FONT.small, { color: p.inkSoft, flex: 1, textAlign: 'center' }]}>
                  {a.label}
                </Text>
              ))}
            </View>
            {HIT_RATES.map((hr, r) => (
              <View key={hr} style={[s.gridRow, { borderBottomColor: p.rule }]}>
                <Text style={[FONT.num, { color: p.ink, width: 62 }]}>{(hr * 100).toFixed(0)}%</Text>
                {grid[r].map((v, c) => {
                  const over = v !== null && magCap > 0 && v > magCap;
                  return (
                    <Text
                      key={c}
                      style={[
                        FONT.num,
                        {
                          flex: 1, textAlign: 'center',
                          color: over ? p.caution : p.good,
                          fontWeight: over ? '700' : '600',
                        },
                      ]}
                    >
                      {v === null ? '—' : v}
                    </Text>
                  );
                })}
              </View>
            ))}
            <Note tone="bad">
              Red means one magazine cannot finish the fight. Against Level 3 armour there is usually
              no hit rate on this grid that works — and Level 3 is what you face in the late circles,
              which is exactly where clutches happen.
            </Note>
          </Card>
        </>
      ) : null}

      {tab === 'pairs' ? (
        <Card title="Double-gun loadouts, ranked">
          {pairs.map((r) => (
            <View key={`${r.pair.a}/${r.pair.b}`} style={[s.pair, { borderBottomColor: p.rule }]}>
              <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: 8 }}>
                <Text style={[FONT.h3, { color: p.ink, flex: 1 }]}>
                  {r.pair.a} + {r.pair.b}
                </Text>
                <Text
                  style={[
                    FONT.num,
                    { color: (r.margin ?? 0) > 8 ? p.good : (r.margin ?? 0) > 0 ? p.warn : p.caution, fontWeight: '700' },
                  ]}
                >
                  {r.margin === null ? '—' : `${r.margin > 0 ? '+' : ''}${r.margin}`}
                </Text>
              </View>
              <Text style={[FONT.small, { color: p.inkSoft, marginTop: 2 }]}>
                {r.pair.label} · {r.bothUsable ? 'both usable at clutch range' : 'second gun dead inside 30 m'}
                {r.total !== null ? ` · ${r.total} usable rounds` : ''}
                {r.swapSaves !== null ? ` · swap saves ${r.swapSaves}s` : ''}
              </Text>
              <Text style={[FONT.small, { color: p.inkSoft, marginTop: 3 }]}>{r.pair.note}</Text>
            </View>
          ))}
          <Note>
            Margin is usable rounds minus rounds needed. Rounds on a gun you cannot shoot at fifteen
            metres are not rounds, which is why the AR plus DMR and AR plus sniper pairings land at
            zero — the same as holding one gun, because that is effectively what you are doing.
          </Note>
        </Card>
      ) : null}

      {tab === 'db' ? (
        <Card title="Weapon database">
          <Note tone="warn">
            PUBG Mobile publishes no stat table. Every figure is a community private-lobby estimate,
            the sources contradict each other, and most reload times could not be sourced at all.
          </Note>
          <View style={{ height: 10 }} />
          {WEAPONS.map((x) => (
            <WeaponRow key={x.name} w={x} inputs={i} />
          ))}
        </Card>
      ) : null}
    </Screen>
  );
}

function WeaponRow({ w, inputs }: { w: Weapon; inputs: FightInputs }) {
  const p = usePalette();
  const row = fightMath(w, inputs);
  const confColor = w.conf === 'UNMEASURED' ? p.caution : w.conf === 'Medium' ? p.good : p.warn;
  return (
    <View style={[s.dbRow, { borderBottomColor: p.rule }]}>
      <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: 8 }}>
        <Text style={[FONT.h3, { color: p.ink, flex: 1 }]}>{w.name}</Text>
        <Text style={[FONT.small, { color: p.inkSoft }]}>{w.cls} · {w.ammo}</Text>
        <Text style={[FONT.small, { color: confColor, fontWeight: '600' }]}>{w.conf}</Text>
      </View>
      <Text style={[FONT.small, { color: p.inkSoft, marginTop: 3 }]}>
        dmg {w.dmg ?? '—'}
        {w.dmgAlt !== null ? ` (alt ${w.dmgAlt})` : ''} · mag {w.mag ?? '—'}
        {w.ext ? `/${w.ext}` : ''} · reload {w.reload ?? '—'}s
        {row.hitsToKnock !== null ? ` · ${row.hitsToKnock} hits to knock` : ''}
      </Text>
      <Text style={[FONT.small, { color: p.inkSoft, marginTop: 2, fontStyle: 'italic' }]}>{w.note}</Text>
    </View>
  );
}

const s = StyleSheet.create({
  chip: { borderWidth: 1, paddingHorizontal: 11, paddingVertical: 6 },
  gridRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6, borderBottomWidth: 1 },
  pair: { paddingVertical: 10, borderBottomWidth: 1 },
  dbRow: { paddingVertical: 9, borderBottomWidth: 1 },
});
