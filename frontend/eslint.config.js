import storybook from 'eslint-plugin-storybook';

import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import reactX from 'eslint-plugin-react-x';
import reactDom from 'eslint-plugin-react-dom';
import tseslint from 'typescript-eslint';
import pluginRouter from '@tanstack/eslint-plugin-router';
import eslintConfigPrettier from 'eslint-config-prettier/flat';
import { defineConfig, globalIgnores } from 'eslint/config';

export default defineConfig([
  globalIgnores(['dist', 'src/client']),
  {
    files: ['**/*.{ts,tsx}'],
    ignores: ['src/components/chakra-ui/*'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommendedTypeChecked,
      reactX.configs['recommended-typescript'],
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
      reactDom.configs.recommended,
      eslintConfigPrettier,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    rules: {
      // Supressing error Tanstack Router Route components
      'react-refresh/only-export-components': ['off', { allowExportNames: ['Route', 'router'] }],
    },
  },
  ...storybook.configs['flat/recommended'],
  ...pluginRouter.configs['flat/recommended'],
]);
