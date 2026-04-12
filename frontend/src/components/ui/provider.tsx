'use client';

import {
  ChakraProvider,
  createSystem,
  defaultConfig,
  defineRecipe,
} from '@chakra-ui/react';
import { ColorModeProvider, type ColorModeProviderProps } from './color-mode';

const buttonRecipe = defineRecipe({
  variants: {
    variant: {
      cyan: {
        bg: 'bg',
        borderColor: 'cyan.fg',
        color: 'cyan.fg',
        _hover: { bg: 'cyan.emphasized' },
        _selected: { bg: 'cyan.fg', color: 'cyan.muted', _hover: { color: 'cyan.fg' } },
      },
    },
  },
  defaultVariants: {
    variant: 'cyan',
  },
});

const system = createSystem(defaultConfig, {
  theme: {
    recipes: { button: buttonRecipe },
  },
});

export function Provider(props: ColorModeProviderProps) {
  return (
    <ChakraProvider value={system}>
      <ColorModeProvider {...props} />
    </ChakraProvider>
  );
}
