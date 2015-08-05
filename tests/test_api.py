"""Test imgur.api functions."""

from sphinxcontrib.imgur import api


def test_purge_orphaned_entries():
    # Do nothing on empty.
    env = type('FakeEnv', (), {})()
    api.purge_orphaned_entries(env, 'TestDoc')
    assert not hasattr(env, 'imgur_api_cache')
    env.imgur_api_cache = dict()
    api.purge_orphaned_entries(env, 'TestDoc')
    assert not env.imgur_api_cache

    # Remove those with no docnames.
    env.imgur_api_cache = {'a/album': dict(_docnames=set(), images=set()), 'image': dict(_docnames=set(), images=set())}
    api.purge_orphaned_entries(env, 'TestDoc')
    assert env.imgur_api_cache == dict()
    env.imgur_api_cache = {'a/album': dict(_docnames={'TestDoc'}, images=set()),
                           'image': dict(_docnames={'TestDoc'}, images=set())}
    api.purge_orphaned_entries(env, 'TestDoc')
    assert env.imgur_api_cache == dict()

    # Remove one docname.
    env.imgur_api_cache = {'a/album': dict(_docnames={'TestDoc', 'Other'}, images=set()),
                           'image': dict(_docnames={'TestDoc', 'Other'}, images=set())}
    api.purge_orphaned_entries(env, 'TestDoc')
    assert env.imgur_api_cache == {'a/album': dict(_docnames={'Other'}, images=set()),
                                   'image': dict(_docnames={'Other'}, images=set())}

    # Keep image with no docnames.
    env.imgur_api_cache = {'a/album': dict(_docnames={'Other'}, images={'image'}),
                           'image': dict(_docnames={}, images=set())}
    api.purge_orphaned_entries(env, 'TestDoc')
    assert env.imgur_api_cache == {'a/album': dict(_docnames={'Other'}, images={'image'}),
                                   'image': dict(_docnames={}, images=set())}


def test_queue_new_imgur_ids_or_add_docname():
    env = type('FakeEnv', (), {})()
    env.imgur_api_cache = dict()
    imgur_ids = {'image'}

    api.queue_new_imgur_ids_or_add_docname(env, imgur_ids, 'TestDoc')
    assert env.imgur_api_cache['image']['_docnames'] == {'TestDoc'}

    api.queue_new_imgur_ids_or_add_docname(env, imgur_ids, 'TestDoc2')
    assert env.imgur_api_cache['image']['_docnames'] == {'TestDoc', 'TestDoc2'}
