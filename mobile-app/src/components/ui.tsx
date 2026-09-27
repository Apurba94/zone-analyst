import React from 'react';
import { View, Text, StyleSheet, Pressable, ScrollView } from 'react-native';
import { usePalette, FONT, type Palette } from '../theme';

export function Card({ title, children }: { title?: string; children: React.ReactNode }) {
  const p = usePalette();
  return (
    <View style={[s.card, { backgroundColor: p.paper2, borderColor: p.rule }]}>
      {title ? (
        <View style={[s.cardHead, { borderBottomColor: p.rule }]}>
          <Text style={[FONT.h3, { color: p.ink }]}>{title}</Text>
        </View>
      ) : null}
      <View style={s.cardBody}>{children}</View>
    </View>
  );
}

export function Note({ children, tone }: { children: React.ReactNode; tone?: 'bad' | 'warn' | 'ok' }) {
  const p = usePalette();
  const color = tone === 'bad' ? p.caution : tone === 'ok' ? p.good : tone === 'warn' ? p.warn : p.inkSoft;
  return <Text style={[FONT.small, { color, marginTop: 6 }]}>{children}</Text>;
}

export function Row({ label, value, tone }: { label: string; value: string; tone?: 'bad' | 'warn' | 'ok' }) {
  const p = usePalette();
  const color = tone === 'bad' ? p.caution : tone === 'ok' ? p.good : tone === 'warn' ? p.warn : p.ink;
  return (
    <View style={[s.row, { borderBottomColor: p.rule }]}>
      <Text style={[FONT.small, { color: p.inkSoft, flex: 1 }]}>{label}</Text>
      <Text style={[FONT.num, { color, fontWeight: '600' }]}>{value}</Text>
    </View>
  );
}

/** A dependency-free slider. PanResponder keeps the install surface small. */
export function Slider({
  label, value, min, max, step, onChange, format,
}: {
  label: string; value: number; min: number; max: number; step: number;
  onChange: (v: number) => void; format?: (v: number) => string;
}) {
  const p = usePalette();
  const [w, setW] = React.useState(1);
  const frac = (value - min) / (max - min);

  const set = (x: number) => {
    const raw = min + (Math.min(Math.max(x, 0), w) / w) * (max - min);
    onChange(Math.round(raw / step) * step);
  };

  return (
    <View style={{ marginBottom: 14 }}>
      <View style={s.sliderLabel}>
        <Text style={[FONT.small, { color: p.inkSoft, flex: 1 }]}>{label}</Text>
        <Text style={[FONT.num, { color: p.ink, fontWeight: '600' }]}>
          {format ? format(value) : String(value)}
        </Text>
      </View>
      <View
        onLayout={(e) => setW(e.nativeEvent.layout.width)}
        onStartShouldSetResponder={() => true}
        onMoveShouldSetResponder={() => true}
        onResponderGrant={(e) => set(e.nativeEvent.locationX)}
        onResponderMove={(e) => set(e.nativeEvent.locationX)}
        style={s.sliderTrackWrap}
        accessibilityRole="adjustable"
        accessibilityLabel={label}
      >
        <View style={[s.sliderTrack, { backgroundColor: p.rule }]}>
          <View style={[s.sliderFill, { backgroundColor: p.sea, width: `${frac * 100}%` }]} />
        </View>
        <View
          style={[s.sliderKnob, { backgroundColor: p.ink, borderColor: p.paper2, left: `${frac * 100}%` }]}
          pointerEvents="none"
        />
      </View>
    </View>
  );
}

export function Segmented<T extends string>({
  options, value, onChange,
}: { options: { key: T; label: string }[]; value: T; onChange: (v: T) => void }) {
  const p = usePalette();
  return (
    <View style={[s.seg, { borderColor: p.rule }]}>
      {options.map((o, i) => {
        const on = o.key === value;
        return (
          <Pressable
            key={o.key}
            onPress={() => onChange(o.key)}
            accessibilityRole="button"
            accessibilityState={{ selected: on }}
            style={[
              s.segBtn,
              { backgroundColor: on ? p.ink : p.paper, borderRightWidth: i === options.length - 1 ? 0 : 1, borderRightColor: p.rule },
            ]}
          >
            <Text style={[FONT.small, { color: on ? p.paper : p.inkSoft, fontWeight: on ? '600' : '400' }]}>
              {o.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export function Screen({ children }: { children: React.ReactNode }) {
  const p = usePalette();
  return (
    <ScrollView
      style={{ backgroundColor: p.paper }}
      contentContainerStyle={{ padding: 16, paddingBottom: 48 }}
    >
      {children}
    </ScrollView>
  );
}

export function H1({ children, sub }: { children: string; sub?: string }) {
  const p = usePalette();
  return (
    <View style={{ marginBottom: 14 }}>
      <Text style={[FONT.h1, { color: p.ink }]}>{children}</Text>
      {sub ? <Text style={[FONT.small, { color: p.inkSoft, marginTop: 4 }]}>{sub}</Text> : null}
    </View>
  );
}

export const styles = (p: Palette) => s;

const s = StyleSheet.create({
  card: { borderWidth: 1, marginBottom: 14 },
  cardHead: { paddingHorizontal: 13, paddingVertical: 9, borderBottomWidth: 1 },
  cardBody: { padding: 13 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 6, borderBottomWidth: 1, gap: 10 },
  sliderLabel: { flexDirection: 'row', alignItems: 'baseline', marginBottom: 6, gap: 8 },
  sliderTrackWrap: { height: 28, justifyContent: 'center' },
  sliderTrack: { height: 3, borderRadius: 2 },
  sliderFill: { height: 3, borderRadius: 2 },
  sliderKnob: { position: 'absolute', width: 18, height: 18, borderRadius: 9, borderWidth: 2, marginLeft: -9 },
  seg: { flexDirection: 'row', borderWidth: 1 },
  segBtn: { flex: 1, paddingVertical: 9, alignItems: 'center' },
});
