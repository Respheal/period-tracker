'use client';

import {
  ChakraProvider,
  createSystem,
  defaultConfig,
  defineConfig,
} from '@chakra-ui/react';
import { ColorModeProvider, type ColorModeProviderProps } from './color-mode';

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

export function Provider(props: ColorModeProviderProps) {
  return (
    <ChakraProvider value={generateSystem(props.palette ?? 'gray')}>
      <ColorModeProvider {...props} />
    </ChakraProvider>
  );
}
