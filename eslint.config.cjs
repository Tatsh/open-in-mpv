import { defineConfig } from 'eslint-define-config';

export default defineConfig([
  {
    env: {
      browser: true,
      es6: true,
      webextensions: true,
    },
    extends: ['eslint:recommended'],
    parserOptions: {
      ecmaVersion: 8,
    },
    rules: {
      'no-alert': 'error',
      'no-debugger': 'error',
      'no-lonely-if': 'error',
      'no-magic-numbers': [
        'error',
        {
          enforceConst: true,
          ignore: [0],
          ignoreArrayIndexes: true,
        },
      ],
      quotes: ['error', 'single'],
    },
  },
]);
