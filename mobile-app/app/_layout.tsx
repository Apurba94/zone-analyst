import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from 'react-native';
import { usePalette } from '../src/theme';

export default function Layout() {
  const p = usePalette();
  const scheme = useColorScheme();
  return (
    <>
      <StatusBar style={scheme === 'dark' ? 'light' : 'dark'} />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: p.paper2 },
          headerTintColor: p.ink,
          headerTitleStyle: { fontSize: 16, fontWeight: '600' },
          contentStyle: { backgroundColor: p.paper },
        }}
      >
        <Stack.Screen name="index" options={{ title: 'Zone Analyst' }} />
        <Stack.Screen name="simulator" options={{ title: 'Zone simulator' }} />
        <Stack.Screen name="chart" options={{ title: 'Probability chart' }} />
        <Stack.Screen name="combat" options={{ title: 'Combat math' }} />
        <Stack.Screen name="playbook" options={{ title: 'Playbook' }} />
      </Stack>
    </>
  );
}
