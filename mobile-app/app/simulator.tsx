import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import Svg, { Path, Circle as SvgCircle, Line, G } from 'react-native-svg';
import { usePalette, FONT } from '../src/theme';
import { Screen, H1, Card, Slider, Segmented, Row, Note } from '../src/components/ui';
import {
  makeMatch, lerpCircle, guaranteedSafeRadius, matchTransitions, runBattery, verdict,
  type Circle, type ZoneModel, type Transition,
} from '../src/zone';

const SIZE = 340;

export default function Simulator() {
  const p = usePalette();

  const [model, setModel] = React.useState<ZoneModel>('disc');
  const [ratio, setRatio] = React.useState(0.62);
  const [waitS, setWaitS] = React.useState(40);
  const [shrinkS, setShrinkS] = React.useState(70);
  const [dps, setDps] = React.useState(4);
  const [speed, setSpeed] = React.useState(0.05); // map widths per minute
  const [rate, setRate] = React.useState(4);

  const [match, setMatch] = React.useState<Circle[]>(() => makeMatch(0.58, 0.62, 8, 'disc', 0));
  const [phase, setPhase] = React.useState(0);
  const [mode, setMode] = React.useState<'wait' | 'shrink'>('wait');
  const [t, setT] = React.useState(0);
  const [playing, setPlaying] = React.useState(false);
  const [hp, setHp] = React.useState(100);
  const [team, setTeam] = React.useState({ x: 0.78, y: 0.24 });
  const [data, setData] = React.useState<Transition[]>([]);

  const reset = React.useCallback(
    (m: ZoneModel = model, r: number = ratio) => {
      setMatch(makeMatch(0.58, r, 8, m, 0));
      setPhase(0);
      setMode('wait');
      setT(0);
      setHp(100);
    },
    [model, ratio]
  );

  // --- simulation loop -----------------------------------------------------
  const st = React.useRef({ phase, mode, t, hp, team, playing, match });
  st.current = { phase, mode, t, hp, team, playing, match };

  React.useEffect(() => {
    if (!playing) return;
    let last = Date.now();
    const id = setInterval(() => {
      const now = Date.now();
      const dt = ((now - last) / 1000) * rate;
      last = now;
      const c = st.current;
      const dur = c.mode === 'wait' ? waitS : shrinkS;
      let nt = c.t + dt;

      const z = blue(c.match, c.phase, c.mode, c.t, shrinkS);
      if (Math.hypot(c.team.x - z.x, c.team.y - z.y) > z.r) {
        setHp((h) => Math.max(0, h - dps * dt));
      }

      if (nt >= dur) {
        nt = 0;
        if (c.mode === 'wait') setMode('shrink');
        else {
          const next = c.phase + 1;
          if (next >= c.match.length - 1) {
            setData((d) => [...d, ...matchTransitions(c.match)]);
            setMatch(makeMatch(0.58, ratio, 8, model, 0));
            setPhase(0);
            setHp(100);
          } else {
            setPhase(next);
          }
          setMode('wait');
        }
      }
      setT(nt);
    }, 40);
    return () => clearInterval(id);
  }, [playing, rate, waitS, shrinkS, dps, ratio, model]);

  const z = blue(match, phase, mode, t, shrinkS);
  const next = match[phase + 1];
  const cur = match[phase];
  const outside = Math.hypot(team.x - z.x, team.y - z.y) > z.r;
  const rho = next && model !== 'free' ? guaranteedSafeRadius(cur.r, next.r) : 0;

  const caught = timeUntilCaught(match, phase, mode, t, waitS, shrinkS, team);
  const need = next
    ? Math.max(0, Math.hypot(team.x - next.x, team.y - next.y) - next.r) / (speed / 60)
    : 0;
  const slack = caught - need;

  const bat = runBattery(data);
  const v = verdict(bat);
  const dur = mode === 'wait' ? waitS : shrinkS;

  const px = (n: number) => n * SIZE;

  return (
    <Screen>
      <H1 sub="Watch the zone close, drag your team into its path, and see whether they get out. Every match feeds the battery below.">
        Zone simulator
      </H1>

      <Card>
        <View style={s.status}>
          <Text style={[FONT.h2, { color: p.ink }]}>Phase {phase + 1}</Text>
          <Text style={[FONT.small, { color: p.inkSoft, flex: 1 }]}>
            {!next ? 'final circle' : mode === 'wait' ? 'holding — next circle shown' : 'closing'}
          </Text>
          <Text style={[FONT.h2, { color: p.ink }]}>{Math.max(0, Math.ceil(dur - t))}s</Text>
        </View>

        <View style={[s.hpBar, { backgroundColor: p.rule }]}>
          <View style={[s.hpFill, { width: `${hp}%`, backgroundColor: hp < 100 ? p.caution : p.good }]} />
        </View>

        <View
          style={{ alignSelf: 'center', marginTop: 10 }}
          onStartShouldSetResponder={() => true}
          onMoveShouldSetResponder={() => true}
          onResponderGrant={(e) =>
            setTeam({
              x: clamp(e.nativeEvent.locationX / SIZE),
              y: clamp(e.nativeEvent.locationY / SIZE),
            })
          }
          onResponderMove={(e) =>
            setTeam({
              x: clamp(e.nativeEvent.locationX / SIZE),
              y: clamp(e.nativeEvent.locationY / SIZE),
            })
          }
        >
          <Svg width={SIZE} height={SIZE} style={{ backgroundColor: p.paper2 }}>
            <G opacity={0.5}>
              {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                <G key={i}>
                  <Line x1={(SIZE * i) / 8} y1={0} x2={(SIZE * i) / 8} y2={SIZE} stroke={p.rule} strokeWidth={1} />
                  <Line x1={0} y1={(SIZE * i) / 8} x2={SIZE} y2={(SIZE * i) / 8} stroke={p.rule} strokeWidth={1} />
                </G>
              ))}
            </G>

            {/* Everything outside the blue boundary is lethal: even-odd fill. */}
            <Path d={outsideDiscPath(px(z.x), px(z.y), px(z.r), SIZE)} fill={p.danger} fillRule="evenodd" />

            {next ? (
              <SvgCircle
                cx={px(next.x)} cy={px(next.y)} r={px(next.r)}
                stroke={p.ink} strokeWidth={2} strokeDasharray="7,5" fill="none" opacity={0.75}
              />
            ) : null}

            {rho > 0 ? (
              <SvgCircle
                cx={px(cur.x)} cy={px(cur.y)} r={px(rho)}
                stroke={p.ink} strokeWidth={1.5} strokeDasharray="1,3" fill="none" opacity={0.65}
              />
            ) : null}

            <SvgCircle cx={px(z.x)} cy={px(z.y)} r={px(z.r)} stroke={p.sea} strokeWidth={3} fill="none" />

            <SvgCircle cx={px(team.x)} cy={px(team.y)} r={7} stroke={p.caution} strokeWidth={3} fill="none" />
            {outside ? (
              <SvgCircle cx={px(team.x)} cy={px(team.y)} r={13} stroke={p.caution} strokeWidth={2} fill="none" opacity={0.35} />
            ) : null}
          </Svg>
        </View>

        <View style={[s.legend, { borderTopColor: p.rule }]}>
          <Text style={[FONT.small, { color: p.inkSoft }]}>
            blue = zone · dashed = next circle · dotted = guaranteed safe · magenta = your team
          </Text>
        </View>

        <View style={[s.transport, { borderTopColor: p.rule }]}>
          <Pressable style={[s.tBtn, { backgroundColor: p.ink }]} onPress={() => setPlaying((x) => !x)}>
            <Text style={[FONT.small, { color: p.paper, fontWeight: '600' }]}>{playing ? 'Pause' : 'Play'}</Text>
          </Pressable>
          <Pressable
            style={[s.tBtn, { backgroundColor: p.paper, borderLeftWidth: 1, borderLeftColor: p.rule }]}
            onPress={() => (mode === 'wait' ? setMode('shrink') : (setPhase((x) => Math.min(x + 1, match.length - 2)), setMode('wait')), setT(0))}
          >
            <Text style={[FONT.small, { color: p.ink }]}>Skip phase</Text>
          </Pressable>
          <Pressable
            style={[s.tBtn, { backgroundColor: p.paper, borderLeftWidth: 1, borderLeftColor: p.rule }]}
            onPress={() => reset()}
          >
            <Text style={[FONT.small, { color: p.ink }]}>New match</Text>
          </Pressable>
        </View>
      </Card>

      <Card title="Can they make it?">
        {!next ? (
          <Text style={[FONT.h2, { color: p.ink }]}>Final circle.</Text>
        ) : caught === 0 ? (
          <>
            <Text style={[FONT.h2, { color: p.caution }]}>Taking damage — {hp.toFixed(0)} HP left.</Text>
            <Note>{need.toFixed(0)}s of travel to reach the next circle at this speed.</Note>
          </>
        ) : caught === Infinity ? (
          <>
            <Text style={[FONT.h2, { color: p.good }]}>Safe through this phase.</Text>
            <Note>Already inside the next circle — no rotation needed.</Note>
          </>
        ) : (
          <>
            <Text style={[FONT.h2, { color: slack > 20 ? p.good : slack > 0 ? p.warn : p.caution }]}>
              {slack > 20
                ? `Makes it, ${slack.toFixed(0)}s to spare.`
                : slack > 0
                ? `Tight — ${slack.toFixed(0)}s to spare.`
                : `Short by ${(-slack).toFixed(0)}s.`}
            </Text>
            <Note>
              Caught in {caught.toFixed(0)}s; needs {need.toFixed(0)}s to reach safety.
            </Note>
          </>
        )}
      </Card>

      <Card title="Zone rule">
        <Segmented
          value={model}
          onChange={(m) => {
            setModel(m);
            reset(m);
          }}
          options={[
            { key: 'disc', label: 'Disc' },
            { key: 'spiral', label: 'Spiral' },
            { key: 'half', label: 'Half' },
            { key: 'free', label: 'Null' },
          ]}
        />
        <View style={{ height: 12 }} />
        <Slider label="Next radius ÷ current" value={ratio} min={0.3} max={0.85} step={0.01}
          onChange={(v) => { setRatio(v); reset(model, v); }} format={(v) => v.toFixed(2)} />
        <Note>
          Above 0.50 there is a disc of ground that cannot be caught outside. Below it, no ground is
          guaranteed and centre play stops being free.
        </Note>
      </Card>

      <Card title="Timing and damage">
        <Slider label="Wait before shrink (s)" value={waitS} min={5} max={180} step={5} onChange={setWaitS} />
        <Slider label="Shrink duration (s)" value={shrinkS} min={10} max={300} step={5} onChange={setShrinkS} />
        <Slider label="Damage outside (HP/s)" value={dps} min={0.2} max={20} step={0.2} onChange={setDps} format={(v) => v.toFixed(1)} />
        <Slider label="Travel speed (map widths/min)" value={speed} min={0.01} max={0.5} step={0.005} onChange={setSpeed} format={(v) => v.toFixed(3)} />
        <Slider label="Playback (× real time)" value={rate} min={1} max={40} step={1} onChange={setRate} />
        <Note>None of these four are measured values. Set them from your own custom-room timings.</Note>
      </Card>

      <Card title="Accumulated data">
        <View style={{ flexDirection: 'row', gap: 8, marginBottom: 10 }}>
          <Pressable
            style={[s.act, { borderColor: p.rule }]}
            onPress={() => {
              const add: Transition[] = [];
              for (let i = 0; i < 25; i++) add.push(...matchTransitions(makeMatch(0.58, ratio, 8, model, 0)));
              setData((d) => [...d, ...add]);
            }}
          >
            <Text style={[FONT.small, { color: p.ink }]}>Run 25 matches</Text>
          </Pressable>
          <Pressable style={[s.act, { borderColor: p.rule }]} onPress={() => setData([])}>
            <Text style={[FONT.small, { color: p.ink }]}>Clear</Text>
          </Pressable>
        </View>

        <Row label="Transitions" value={String(data.length)} />
        {bat ? (
          <>
            <Row label="Containment violations" value={`${(bat.violFrac * 100).toFixed(0)}%`} />
            <Row label="Mean s (0.5 if uniform)" value={bat.meanS.toFixed(3)} />
            <Row label="Radial KS p" value={bat.ksP === null ? '—' : bat.ksP.toExponential(2)} />
            <Row label="Bearing Kuiper p" value={bat.kuiperP === null ? '—' : bat.kuiperP.toExponential(2)} />
            <Row label="Coupling resultant" value={bat.coupRes.toFixed(3)} />
          </>
        ) : null}

        <Text style={[FONT.h3, { color: p.ink, marginTop: 12 }]}>{v.title}</Text>
        <Note>{v.detail}</Note>
      </Card>
    </Screen>
  );
}

// --- helpers ---------------------------------------------------------------

const clamp = (v: number) => Math.min(Math.max(v, 0), 1);

function blue(match: Circle[], phase: number, mode: 'wait' | 'shrink', t: number, shrinkS: number): Circle {
  const a = match[phase];
  const b = match[phase + 1];
  if (!b || mode === 'wait') return { ...a };
  return lerpCircle(a, b, t / shrinkS);
}

/** A rect with a disc punched out, for the even-odd danger fill. */
function outsideDiscPath(cx: number, cy: number, r: number, size: number): string {
  const rr = Math.max(r, 0.01);
  return (
    `M0,0 H${size} V${size} H0 Z ` +
    `M${cx - rr},${cy} a${rr},${rr} 0 1,0 ${2 * rr},0 a${rr},${rr} 0 1,0 ${-2 * rr},0 Z`
  );
}

/** Seconds until the closing boundary passes the team's current position. */
function timeUntilCaught(
  match: Circle[], phase: number, mode: 'wait' | 'shrink', t: number,
  waitS: number, shrinkS: number, team: { x: number; y: number }
): number {
  const a = match[phase];
  const b = match[phase + 1];
  if (!b) return Infinity;
  const z = blue(match, phase, mode, t, shrinkS);
  if (Math.hypot(team.x - z.x, team.y - z.y) > z.r) return 0;
  const u0 = mode === 'shrink' ? Math.min(t / shrinkS, 1) : 0;
  const waitLeft = mode === 'wait' ? waitS - t : 0;
  for (let i = 1; i <= 240; i++) {
    const u = u0 + (1 - u0) * (i / 240);
    const c = lerpCircle(a, b, u);
    if (Math.hypot(team.x - c.x, team.y - c.y) > c.r) return waitLeft + (u - u0) * shrinkS;
  }
  return Infinity;
}

const s = StyleSheet.create({
  status: { flexDirection: 'row', alignItems: 'baseline', gap: 10, padding: 13 },
  hpBar: { height: 5, overflow: 'hidden' },
  hpFill: { height: 5 },
  legend: { borderTopWidth: 1, padding: 10, marginTop: 10 },
  transport: { flexDirection: 'row', borderTopWidth: 1 },
  tBtn: { flex: 1, paddingVertical: 11, alignItems: 'center' },
  act: { flex: 1, borderWidth: 1, paddingVertical: 8, alignItems: 'center' },
});
