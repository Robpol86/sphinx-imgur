"""Sphinx test configuration."""
exclude_patterns = ["_build"]
extensions = ["sphinx_imgur.imgur"]
html_theme = "basic"
master_doc = "index"
nitpicky = True

imgur_target_default_page = True
