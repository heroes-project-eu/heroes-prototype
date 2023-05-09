# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

# The HEROES project
project = "HEROES"
copyright = "2022, HEROES"
author = "HEROES"

# The full version, including alpha/beta/rc tags
release = "4.0"
version = release


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx_tabs.tabs"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["../templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_show_sphinx = False
html_show_sourcelink = False
html_show_copyright = True
html_domain_indices = True
html_theme = "sphinx_rtd_theme"
html_theme_path = [
    "themes",
]
html_logo = "media/logo.png"
html_favicon = "media/favicon.ico"
html_theme_options = {
    "logo_only": False,
    "display_version": True,
}
html_title = "HEROES documentation"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["../_static"]


# Use our own css file
def setup(app):
    app.add_css_file("css/custom.css")
