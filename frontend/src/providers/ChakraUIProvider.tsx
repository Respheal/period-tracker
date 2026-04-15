'use client';

import {
  ChakraProvider,
  createSystem,
  defaultConfig,
  defineConfig,
} from '@chakra-ui/react';
import { ThemeProvider } from 'next-themes';

interface ChakraUIProviderProps {
  children: React.ReactNode;
  palette?: string;
}

function generateSystem(palette: string) {
  return createSystem(
    defaultConfig,
    defineConfig({
      globalCss: {
        html: { colorPalette: palette },
      },
    }),
  );
}

export function ChakraUIProvider(props: ChakraUIProviderProps) {
  const system = generateSystem(props.palette || 'gray');
  return (
    <ChakraProvider value={system}>
      <ThemeProvider attribute='class'>{props.children}</ThemeProvider>
    </ChakraProvider>
  );
}
