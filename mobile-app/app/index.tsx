import { View, Text, Pressable, StyleSheet } from 'react-native';
import { Link } from 'expo-router';
import { usePalette, FONT } from '../src/theme';
import { Screen, H1, Card, Note } from '../src/components/ui';

const MODULES = [
  { href: '/simulator', title: 'Zone simulator', body: 'Watch the zone close phase by phase, drag your team into its path, and see whether they get out. Accumulates match data into the test battery.' },
  { href: '/chart', title: 'Probability chart', body: 'Where the next circle can reach, and where a team can stand and stay inside. Centre density and survival are different questions.' },
  { href: '/combat', title: 'Combat math', body: 'Weapon database, 1v4 ammunition budget with the armour sensitivity grid, and ranked double-gun loadouts.' },
  { href: '/playbook', title: 'Playbook', body: 'Anti-rush defence, the 1v4 clutch method, and map analysis for the 2026 tournament pool.' },
];

export default function Home() {
  const p = usePalette();
  return (
    <Screen>
      <H1 sub="A competitive analysis toolkit. Everything here is a model of a candidate algorithm or a calculation over community-sourced numbers — not a measurement of the live game.">
        Zone Analyst
      </H1>

      {MODULES.map((m) => (
        <Link key={m.href} href={m.href as any} asChild>
          <Pressable>
            <View style={[s.tile, { backgroundColor: p.paper2, borderColor: p.rule }]}>
              <Text style={[FONT.h2, { color: p.ink }]}>{m.title}</Text>
              <Text style={[FONT.small, { color: p.inkSoft, marginTop: 5 }]}>{m.body}</Text>
            </View>
          </Pressable>
        </Link>
      ))}

      <Card title="Read this once">
        <Text style={[FONT.small, { color: p.inkSoft, lineHeight: 19 }]}>
          The zone models come from a published Tencent patent describing a candidate
          centre-selection routine. A patent describes an embodiment, not shipped code.
          {'\n\n'}
          The weapon numbers are community private-lobby estimates. PUBG Mobile publishes no stat
          table, the sources contradict each other, and most reload times could not be sourced at
          all. Rows carry their own confidence grade.
          {'\n\n'}
          Everything computes from those inputs, so your own measurements replace them and the
          answers update. Quote the method, not the numbers.
        </Text>
      </Card>

      <Note>Not affiliated with, endorsed by, or connected to KRAFTON, Tencent or PUBG Mobile.</Note>
    </Screen>
  );
}

const s = StyleSheet.create({
  tile: { borderWidth: 1, padding: 15, marginBottom: 12 },
});
