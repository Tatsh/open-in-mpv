local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Host-side of the extension to open any link or page URL in mpv via the browser context menu.',
  keywords: ['audio', 'browser extension', 'multimedia', 'mpv', 'video'],
  project_name: 'open-in-mpv',
  version: '0.1.3',
  want_main: true,
  want_flatpak: true,
  publishing+: { flathub: 'sh.tat.open-in-mpv' },
  security_policy_supported_versions: { '0.1.x': ':white_check_mark:' },
  package_json+: {
    devDependencies+: {
      '@eslint/compat': utils.latestNpmPackageVersionCaret('@eslint/compat'),
      '@eslint/js': utils.latestNpmPackageVersionCaret('@eslint/js'),
      '@types/chrome': utils.latestNpmPackageVersionCaret('@types/chrome'),
      eslint: utils.latestNpmPackageVersionCaret('eslint'),
      'eslint-config': utils.latestNpmPackageVersionCaret('eslint-config'),
      globals: utils.latestNpmPackageVersionCaret('globals'),
    },
    description: 'Browser side of the extension to open any link or page URL in mpv via the browser context menu.',
    scripts+: {
      qa: 'yarn eslint &&' + super.qa,
    },
  },
  prettierignore+: [
    '*.nsi',
  ],
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
        version_files+: ['installer.nsi', 'src/manifest.json'],
      },
      poetry+: {
        dependencies+: {
          platformdirs: utils.latestPypiPackageVersionCaret('platformdirs'),
        },
      },
    },
  },
  shared_ignore+: ['*.crx', '*.pem'],
  security_addendum: |||
    ### Potential issues that are _not_ considered vulnerabilities

    - In the `open-in-mpv` Python script: running a rogue `mpv` executable (where it is likely a user
      has a compromised system).
    - Anything in the `test-open` script as this is only for testing for use by developers.
    - The lack of a complete uninstaller.
  |||,
  force_eslint: true,
  snapcraft+: { summary: 'Open any link or page URL in mpv via the browser context menu.' },
}
