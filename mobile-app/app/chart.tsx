import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Svg, { Circle as SvgCircle, Line, G, Path, Text as SvgText } from 'react-native-svg';
import { usePalette, FONT } from '../src/theme';
import { Screen, H1, Card, Slider, Segmented, Row, Note } from '../src/components/ui';
import {
  radiusSchedule, centreQuantiles, survivalCurve, guaranteedSafeRadius,
  type ZoneModel,
} from '../src/zone';

const SIZE = 340;
const LEVELS = [0.5, 0.75, 0.9, 0.95];

export default function Chart() {
  const p = usePalette();
  const [model, setModel] = React.useState<ZoneModel>('disc');
  const [rNow, setRNow] = React.useState(0.19);
  const [ratio, setRatio] = React.useState(0.55);
  const [steps, setSteps] = React.useState(1);
  const [view, setView] = React.useState<'density' | 'survival'>('density');

  const radii = React.useMemo(
    () => radiusSchedule(rNow, ratio, steps + 1).slice(1),
    [rNow, ratio, steps]
  );

  // Both fields are isotropic about the current centre, so each collapses to a
  // one-dimensional curve. That is why this renders as rings rather than as a
  // 17,000-rectangle heatmap.
  const quantiles = React.useMemo(
    () => centreQuantiles(rNow, radii, model, LEVELS, 3000),
    [rNow, radii, model]
  );
  const surv = React.useMemo(
    () => survivalCurve(rNow, radii, model, 40, 2000),
    [rNow, radii, model]
  );

  const rFinal = radii[radii.length - 1];
  const rho = model === 'free' ? 0 : guaranteedSafeRadius(rNow, rFinal);
  const cx = SIZE / 2;
  const cy = SIZE / 2;
  const scale = SIZE / (Math.max(rNow, quantiles[3]) * 2.6);
  const px = (v: number) => v * scale;

  const bands = [p.sea, p.sea, p.sea, p.sea];
  const opac = [0.42, 0.3, 0.2, 0.12];

  // Survival rings: distances where the curve crosses these probabilities.
  const survRings = [0.9, 0.6, 0.3].map((target) => {
    let d = 0;
    for (let i = 0; i < surv.p.length; i++) {
      if (surv.p[i] >= target) d = surv.d[i];
    }
    return { target, d };
  });

  const atCentre = surv.p[0];

  return (
    <Screen>
      <H1 sub="Where the next centre can reach, and where a team can stand and stay inside. These are different questions and the second one is what positioning depends on.">
        Probability chart
      </H1>

      <Card>
        <Segmented
          value={view}
          onChange={setView}
          options={[
            { key: 'density', label: 'Centre density' },
            { key: 'survival', label: 'Survival' },
          ]}
        />

        <View style={{ alignSelf: 'center', marginTop: 12 }}>
          <Svg width={SIZE} height={SIZE} style={{ backgroundColor: p.paper2 }}>
            <G opacity={0.45}>
              {[1, 2, 3].map((i) => (
                <G key={i}>
                  <Line x1={(SIZE * i) / 4} y1={0} x2={(SIZE * i) / 4} y2={SIZE} stroke={p.rule} strokeWidth={1} />
                  <Line x1={0} y1={(SIZE * i) / 4} x2={SIZE} y2={(SIZE * i) / 4} stroke={p.rule} strokeWidth={1} />
                </G>
              ))}
            </G>

            {view === 'density'
              ? [...LEVELS].reverse().map((lv, i) => {
                  const idx = LEVELS.indexOf(lv);
                  return (
                    <SvgCircle
                      key={lv}
                      cx={cx} cy={cy} r={px(quantiles[idx])}
                      fill={bands[i]} opacity={opac[LEVELS.length - 1 - idx]}
                      stroke={p.ink} strokeWidth={0.75} strokeOpacity={0.35}
                    />
                  );
                })
              : survRings.map((ring, i) => (
                  <SvgCircle
                    key={ring.target}
                    cx={cx} cy={cy} r={px(ring.d)}
                    fill={p.sea} opacity={0.34 - i * 0.09}
                    stroke={p.ink} strokeWidth={0.75} strokeOpacity={0.35}
                  />
                ))}

            {/* admissible-centre disc */}
            {model !== 'free' ? (
              <SvgCircle
                cx={cx} cy={cy} r={px(Math.max(rNow - rFinal, 0))}
                stroke={p.ink} strokeWidth={1} strokeDasharray="4,4" fill="none" opacity={0.45}
              />
            ) : null}

            {rho > 0 ? (
              <SvgCircle cx={cx} cy={cy} r={px(rho)} stroke={p.ink} strokeWidth={1.5} strokeDasharray="1,3" fill="none" opacity={0.7} />
            ) : null}

            {/* current circle — the only magenta */}
            <SvgCircle cx={cx} cy={cy} r={px(rNow)} stroke={p.caution} strokeWidth={2} fill="none" />
            <Line x1={cx - 7} y1={cy} x2={cx + 7} y2={cy} stroke={p.caution} strokeWidth={2} />
            <Line x1={cx} y1={cy - 7} x2={cx} y2={cy + 7} stroke={p.caution} strokeWidth={2} />
          </Svg>
        </View>

        <Text style={[FONT.small, { color: p.inkSoft, marginTop: 10 }]}>
          {view === 'density'
            ? 'Rings hold 50, 75, 90 and 95 percent of the next centre’s probability mass. Magenta is the current circle; the dashed ring is where its centre may move to.'
            : 'Rings mark where a stationary team has a 90, 60 and 30 percent chance of still being inside the zone.'}
        </Text>
      </Card>

      <Card title={view === 'density' ? 'How concentrated is it?' : 'Survival by distance'}>
        {view === 'density' ? (
          <>
            {LEVELS.map((lv, i) => (
              <Row
                key={lv}
                label={`${Math.round(lv * 100)}% of mass within`}
                value={`${(quantiles[i] * 100).toFixed(1)}% of map width`}
              />
            ))}
            <Note>
              {quantiles[2] > rNow * 0.9
                ? 'Close to flat at this lookahead. Treat it as a constraint on where the zone cannot be, not as a read.'
                : 'Usably concentrated. Plan rotations that stay valid across the 90 percent ring.'}
            </Note>
          </>
        ) : (
          <>
            <Row label="Standing at the current centre" value={`${(atCentre * 100).toFixed(0)}%`} tone={atCentre > 0.8 ? 'ok' : atCentre > 0.4 ? 'warn' : 'bad'} />
            {survRings.map((r) => (
              <Row
                key={r.target}
                label={`${Math.round(r.target * 100)}% safe out to`}
                value={`${(r.d * 100).toFixed(1)}% of map width`}
              />
            ))}
            <Note>
              A point can sit well off centre and still be safe, because it falls inside many of the
              sampled circles. That is why positioning uses this field and not the density.
            </Note>
          </>
        )}
      </Card>

      <Card title="Guaranteed safe">
        <Row
          label={`Disc radius, ${steps} phase${steps > 1 ? 's' : ''} ahead`}
          value={rho > 0 ? `${(rho * 100).toFixed(2)}% of map width` : 'none'}
          tone={rho > 0 ? 'ok' : 'bad'}
        />
        <Note>
          {model === 'free'
            ? 'The null baseline drops containment, so nothing is guaranteed.'
            : rho > 0
            ? 'Ground inside this ring cannot be caught outside for any admissible draw. This is geometry, not a forecast.'
            : `At a ratio of ${ratio.toFixed(2)} the circle can shrink past its own centre, so no ground is guaranteed. Centre play stops being free below 0.50.`}
        </Note>
      </Card>

      <Card title="Current circle">
        <Slider label="Radius (fraction of map width)" value={rNow} min={0.02} max={0.45} step={0.005} onChange={setRNow} format={(v) => v.toFixed(3)} />
        <Slider label="Next radius ÷ current" value={ratio} min={0.3} max={0.85} step={0.01} onChange={setRatio} format={(v) => v.toFixed(2)} />
        <Slider label="Phases ahead" value={steps} min={1} max={3} step={1} onChange={setSteps} />
        <View style={{ height: 6 }} />
        <Segmented
          value={model}
          onChange={setModel}
          options={[
            { key: 'disc', label: 'Disc' },
            { key: 'spiral', label: 'Spiral' },
            { key: 'half', label: 'Half' },
            { key: 'free', label: 'Null' },
          ]}
        />
        <Note>
          The radius ratio is a placeholder and propagates into every number here. Measure it from
          your own annotated matches before quoting any of these figures.
        </Note>
      </Card>
    </Screen>
  );
}

const s = StyleSheet.create({});
