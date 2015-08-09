"""Make sure we don't hammer the API."""

import re
import time
from subprocess import check_output, STDOUT

from tests.helpers import change_doc, init_sample_docs

COMMAND = ['sphinx-build', '-n', '-N', '-W', '.', '_build/html']


def test_first_run(tmpdir_module):
    """First run."""
    init_sample_docs(tmpdir_module)
    check_output(COMMAND, cwd=str(tmpdir_module), stderr=STDOUT)

    outdir = tmpdir_module.join('_build', 'html')
    out_doc1_html = outdir.join('doc1.html').read()
    out_doc2_html = outdir.join('doc2.html').read()
    assert 'The title is: Title.' in out_doc1_html
    assert 'And the description: Desc' in out_doc1_html
    assert 'The title is: Title2.' in out_doc2_html


def test_remove_imgur_api_test_response(tmpdir_module):
    """Remove imgur_api_test_response from conf.py. Extension should only use cached data."""
    conf_py = tmpdir_module.join('conf.py').read()
    new_conf_py = re.sub(r'\nimgur_api_test_response [^}]+\n}', '', conf_py).strip()
    tmpdir_module.join('conf.py').write(new_conf_py + '\n')
    assert 'imgur_api_test_response' not in new_conf_py

    time.sleep(2)
    change_doc(tmpdir_module)
    check_output(COMMAND, cwd=str(tmpdir_module), stderr=STDOUT)

    outdir = tmpdir_module.join('_build', 'html')
    out_doc1_html = outdir.join('doc1.html').read()
    out_doc2_html = outdir.join('doc2.html').read()
    assert 'The title is still: Title.' in out_doc1_html
    assert 'And the description: Desc' in out_doc1_html
    assert 'The title is: Title2.' in out_doc2_html
