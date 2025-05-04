local utils = import 'utils.libjsonnet';

local utils = import 'utils.libjsonnet';

(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Host-side of the extension to open any link or page URL in mpv via the browser context menu.',
  keywords: ['audio', 'browser extension', 'multimedia', 'mpv', 'video'],
  project_name: 'open-in-mpv',
  version: '0.1.0',
  want_main: true,
  citation+: {
    'date-released': '2025-04-17',
  },
  package_json+: {
    devDependencies+: {
      '@types/chrome': '^0.0.317',
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
