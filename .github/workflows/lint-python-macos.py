# This workflow will install Python dependencies, run tests and lint with a variety of Python versions
# For more information see: https://help.github.com/actions/language-and-framework-guides/using-python-with-github-actions

name: Lint python

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  build:
    runs-on: macos-latest
    strategy:
      matrix:
        python-version: [2.7]
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v1
      with:
        python-version: ${{ matrix.python-version }}
    - name: version
      run: python --version --version
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pylint pylint-quotes
    - name: Lint with Pylint
      run: |
        pylint host/open-in-mpv
        pylint host/test-open
