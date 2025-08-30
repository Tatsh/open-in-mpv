(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Host-side of the extension to open any link or page URL in mpv via the browser context menu.',
  keywords: ['audio', 'browser extension', 'multimedia', 'mpv', 'video'],
  project_name: 'open-in-mpv',
  version: '0.1.3',
  want_main: true,
  citation+: {
    'date-released': '2025-04-17',
  },
  copilot: {
    intro: 'open-in-mpv is a browser extension that allows users to open links or the current page in mpv via the context menu.',
  },
  package_json+: {
    devDependencies+: {
      '@eslint/compat': '^1.2.9',
      '@eslint/js': '^9.26.0',
      '@types/chrome': '^0.0.317',
      cspell: '^8.19.3',
      eslint: '^9.26.0',
      'eslint-config': '^0.3.0',
      globals: '^16.0.0',
    },
  },
  pyproject+: {
    project+: {
      scripts+: {
        'open-in-mpv-install': 'open_in_mpv.install:main',
        'open-in-mpv-test': 'open_in_mpv.test_open:main',
        'open-in-mpv-uninstall': 'open_in_mpv.uninstall:main',
      },
    },
    tool+: {
      commitizen+: {
        version_files+: ['src/manifest.json'],
      },
      poetry+: {
        dependencies+: {
          platformdirs: '^4.3.6',
        },
      },
    },
  },
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
  ],
  local funding_name = '%s2' % std.asciiLower(self.github_username),
  github_username: 'Tatsh',
  github+: {
    funding+: {
      ko_fi: funding_name,
      liberapay: funding_name,
      patreon: funding_name,
    },
  },
}
