import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: './openapi.json',
  output: {
    postProcess: ['eslint', 'prettier'],
    path: './src/client',
    indexFile: false,
  },
  plugins: [
    '@hey-api/client-ky',
    '@hey-api/schemas',
    '@hey-api/transformers',
    {
      name: '@hey-api/typescript',
      enums: 'javascript',
    },
    {
      name: '@hey-api/sdk',
      transformer: true,
    },
    '@tanstack/react-query',
  ],
});
