# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AgentShip'
copyright = '2026, AgentShip Contributors'
author = 'AgentShip Contributors'

version = '1.0.0'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',  # Google/NumPy style docstrings
    'sphinx_autodoc_typehints',  # Type hints in docs
    'myst_parser',  # Markdown support (for user guides from docs/)
]

# Add napoleon extension (it's built-in but needs to be imported)
try:
    import sphinx.ext.napoleon
except ImportError:
    pass

templates_path = ['_templates']
exclude_patterns = []

# Support both RST and Markdown files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Use furo theme (modern, compatible with Sphinx 9+)
html_theme = 'furo'
html_static_path = ['_static']

# Branding
html_logo = '_static/logo-icon.png'
html_favicon = '_static/favicon-32.png'

# Custom CSS to hide right sidebar
html_css_files = ['custom.css']

# Sidebar configuration - ensure consistent navigation across all pages
# This forces the master toctree from index.rst to always be shown
# Right sidebar (table of contents) is disabled - navigation only via left sidebar
html_sidebars = {
    '**': [
        'sidebar/scroll-start.html',
        'sidebar/brand.html',
        'sidebar/search.html',
        'sidebar/navigation.html',  # Shows master toctree from index.rst
        'sidebar/ethical-ads.html',
        'sidebar/scroll-end.html',
    ]
}

# Disable right sidebar (table of contents) - navigation only via left sidebar
html_theme_options = {
    'sidebar_hide_name': False,
    'navigation_with_keys': True,
    'announcements': {},
    'top_of_page_button': 'edit',
    'show_navbar_depth': 1,
    'toc_title': None,  # Hide TOC title
}

# -- Autodoc configuration ---------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': False,  # Don't show undocumented members
    'exclude-members': '__weakref__'
}
autodoc_mock_imports = ['google.adk', 'google.genai', 'opik', 'litellm']

# Suppress forward reference warnings
typehints_fully_qualified = False
always_document_param_types = False

# -- Napoleon configuration (for Google-style docstrings) -------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
