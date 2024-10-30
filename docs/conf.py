"""See https://www.sphinx-doc.org/en/master/usage/configuration.html."""
from datetime import UTC, datetime
from operator import itemgetter
from pathlib import Path
import sys

import tomlkit

with (Path(__file__).parent.parent / 'pyproject.toml').open('rb') as f:
    poetry = tomlkit.load(f).unwrap()['tool']['poetry']
    authors, name, version = itemgetter('authors', 'name', 'version')(poetry)
# region Path setup
# If extensions (or modules to document with autodoc) are in another directory, add these
# directories to sys.path here. If the directory is relative to the documentation root, use
# str(Path().parent.parent) to make it absolute, like shown here.
sys.path.insert(0, str(Path(__file__).parent.parent))
# endregion
author = authors[0]
copyright = str(datetime.now(UTC).year)  # noqa: A001
project = name
release = f'v{version}'
extensions = [
    'sphinx_immaterial', 'sphinx.ext.napoleon', 'sphinx_datatables', 'sphinx.ext.intersphinx',
    'sphinxcontrib.jquery', *(['sphinx_click'] if poetry.get('scripts') else [])
]
exclude_patterns: list[str] = []
master_doc = 'index'
html_static_path: list[str] = []
html_theme = 'sphinx_immaterial'
html_theme_options = {'palette': {'scheme': 'slate'}}
templates_path = ['_templates']

datatables_class = 'sphinx-datatable'
datatables_options = {'paging': 0}
datatables_version = '1.13.4'
intersphinx_mapping = {'python': ('https://docs.python.org/3.12', None)}
