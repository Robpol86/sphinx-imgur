"""Sphinx test configuration."""
exclude_patterns = ["_build"]
extensions = ["sphinx_imgur.imgur", "sphinxext.opengraph"]
html_theme = "basic"
master_doc = "index"
nitpicky = True

ogp_site_url = "https://robpol86.com"
ogp_use_first_image = True
