import { includeIgnoreFile } from '@eslint/compat';
import js from '@eslint/js';
import globals from 'globals';
import { defineConfig, globalIgnores } from 'eslint/config';
import { fileURLToPath } from 'node:url';

export default defineConfig([
  globalIgnores(['.yarn/**/*.cjs']),
  includeIgnoreFile(fileURLToPath(new URL('.gitignore', import.meta.url))),
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      globals: {
        ...globals.browser,
        ...globals.webextensions,
      },
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
