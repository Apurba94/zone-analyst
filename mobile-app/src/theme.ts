/**
 * Shared design tokens.
 *
 * Same hydrographic-chart palette as the web tools so the app reads as part of
 * the same toolkit: chart ink on paper in light, an ECDIS-style night palette in
 * dark. Magenta is reserved exclusively for things the user controls.
 */
import { useColorScheme } from 'react-native';
import type { TextStyle } from 'react-native';

const light = {
  paper: '#E9E0CC',
  paper2: '#E1D6BE',
  ink: '#16324A',
  inkSoft: '#516A7C',
  rule: '#C3B69A',
  caution: '#A6205F',
  sea: '#3F7CA6',
  danger: 'rgba(63,124,166,0.30)',
  good: '#2F6B4F',
  warn: '#8A5410',
};

const dark = {
  paper: '#0E1A22',
  paper2: '#132430',
  ink: '#CBDDE8',
  inkSoft: '#8AA3B1',
  rule: '#263A46',
  caution: '#E4629A',
  sea: '#6FB3D6',
  danger: 'rgba(111,179,214,0.26)',
  good: '#7FC4A0',
  warn: '#D9A15A',
};

export type Palette = typeof light;

export function usePalette(): Palette {
  return useColorScheme() === 'dark' ? dark : light;
}

export const FONT: Record<'h1' | 'h2' | 'h3' | 'body' | 'small' | 'num', TextStyle> = {
  h1: { fontSize: 26, fontWeight: '600', letterSpacing: -0.4 },
  h2: { fontSize: 17, fontWeight: '600' },
  h3: { fontSize: 14, fontWeight: '600' },
  body: { fontSize: 15, lineHeight: 22 },
  small: { fontSize: 12.5, lineHeight: 18 },
  // Tabular figures keep numbers from jittering as they update each frame.
  num: { fontSize: 15, fontVariant: ['tabular-nums'] },
};
