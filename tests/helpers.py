"""Common/helper code for all test modules."""

import os
from textwrap import dedent


BASE_CONFIG = dedent("""\
    import sys
    sys.path.append('{}')
    extensions = ['sphinxcontrib.imgur']
    master_doc = 'index'
    nitpicky = True
    """).format(os.path.join(os.path.dirname(__file__), '..'))
