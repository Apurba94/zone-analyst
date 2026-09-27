import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { usePalette, FONT } from '../src/theme';
import { Screen, H1, Card } from '../src/components/ui';
import { PLAYBOOK, type Block } from '../src/playbookData';

export default function Playbook() {
  const p = usePalette();
  const [open, setOpen] = React.useState<number | null>(0);

  return (
    <Screen>
      <H1 sub="Anti-rush defence, the 1v4 clutch method, and map analysis for the 2026 tournament pool.">
        Playbook
      </H1>

      {PLAYBOOK.map((sec, i) => {
        const isOpen = open === i;
        return (
          <View key={sec.title} style={[s.sec, { borderColor: p.rule, backgroundColor: p.paper2 }]}>
            <Pressable
              onPress={() => setOpen(isOpen ? null : i)}
              accessibilityRole="button"
              accessibilityState={{ expanded: isOpen }}
              style={[s.head, { borderBottomWidth: isOpen ? 1 : 0, borderBottomColor: p.rule }]}
            >
              <Text style={[FONT.h3, { color: p.ink, flex: 1 }]}>{sec.title}</Text>
              <Text style={[FONT.small, { color: p.inkSoft }]}>{isOpen ? '−' : '+'}</Text>
            </Pressable>
            {isOpen ? <View style={s.body}>{sec.blocks.map((b, j) => <BlockView key={j} b={b} />)}</View> : null}
          </View>
        );
      })}
    </Screen>
  );
}

function BlockView({ b }: { b: Block }) {
  const p = usePalette();
  if (b.kind === 'h') return <Text style={[FONT.h3, { color: p.ink, marginTop: 14, marginBottom: 4 }]}>{b.text}</Text>;
  if (b.kind === 'rule')
    return (
      <View style={[s.rule, { borderLeftColor: p.caution, backgroundColor: p.paper }]}>
        <Text style={[FONT.body, { color: p.ink }]}>{b.text}</Text>
      </View>
    );
  if (b.kind === 'fail')
    return (
      <Text style={[FONT.small, { color: p.inkSoft, marginTop: 6, marginBottom: 4 }]}>
        <Text style={{ color: p.caution, fontWeight: '600' }}>Failure mode: </Text>
        {b.text}
      </Text>
    );
  if (b.kind === 'li')
    return (
      <View style={{ flexDirection: 'row', marginBottom: 6, gap: 8 }}>
        <Text style={[FONT.body, { color: p.inkSoft }]}>·</Text>
        <Text style={[FONT.body, { color: p.ink, flex: 1 }]}>{b.text}</Text>
      </View>
    );
  return <Text style={[FONT.body, { color: p.ink, marginBottom: 10 }]}>{b.text}</Text>;
}

const s = StyleSheet.create({
  sec: { borderWidth: 1, marginBottom: 12 },
  head: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 10 },
  body: { padding: 14 },
  rule: { borderLeftWidth: 3, padding: 12, marginVertical: 10 },
});
