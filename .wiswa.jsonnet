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
  pyproject+: {
    tool+: {
      poetry+: {
        dependencies+: {
          click: '^8.1.8',
          platformdirs: '^4.3.6',
          psutil: '^7.0.0',
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-psutil': '^7.0.0.20250401',
            },
          },
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
