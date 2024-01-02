# Configuration file for the Sphinx documentation builder.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "K2 Base Camp"
copyright = "2023, Ingenia Motion Control"
author = "Ingenia Motion Control"
release = "unreleased"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.6", None),
    "ingenialink": (
        "https://distext.ingeniamc.com/doc/ingenialink-python/7.1.0",
        None,
    ),
    "ingeniamotion": (
        "https://distext.ingeniamc.com/doc/ingeniamotion/0.7.0",
        None,
    ),
    "PySide6": ("https://doc.qt.io/qtforpython-6", "PySide6.inv"),
}
