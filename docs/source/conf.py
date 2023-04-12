import os
import sys
from textwrap import dedent

sys.path.insert(0, os.path.abspath('.'))

project = 'MAxPy'
copyright = '2023, MAxPy Project'
author = 'MAxPy Project'
release = '0.1'

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.autosectionlabel',
]

templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
html_static_path = []

html_logo = "img/logo-maxpy.png"
