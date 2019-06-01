#!/usr/bin/env python3.7

from functools import wraps
import json
from operator import itemgetter
from os import environ
from gnlpy.ipvs import IpvsClient
from ipvssync import reload_ipvs
import pytest


def debug(func):
    """Decorator for interactive debug using pydevd (PyCharm)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if environ.get('PYDEV_IP'):
            import pydevd_pycharm
            pydevd_pycharm.settrace(environ.get('PYDEV_IP'),
                                    port=int(environ.get('PYDEV_PORT')),
                                    stdoutToServer=True,
                                    stderrToServer=True)
        return func(*args, **kwargs)
    return wrapper


@pytest.fixture(scope='module')
def ipvs_client():
    return IpvsClient()


@pytest.fixture(autouse=True)
def flush_ipvs_config(ipvs_client):
    ipvs_client.flush()


@pytest.fixture(scope='module')
def load_pools():
    with open('pools.json') as file:
        return json.load(file)


@debug
@pytest.mark.parametrize('indices',
                         [pytest.param([0, 1], id='add_service'),
                          pytest.param([1, 2], id='add_dest'),
                          pytest.param([0, 2], id='add_service_with_dest'),
                          pytest.param([1, 0], id='remove_service'),
                          pytest.param([2, 1], id='remove_dest'),
                          pytest.param([2, 0], id='remove_service_with_dest'),
                          pytest.param([1, 4], id='add_second_service'),
                          pytest.param([2, 3], id='add_second_dest'),
                          pytest.param([5], id='invalid_config', marks=pytest.mark.xfail)
                          ])
def test_reload_ipvs(ipvs_client, load_pools, indices):
    for pools in itemgetter(*indices)(load_pools):
        reload_ipvs(ipvs_client, pools)
        def remove_fwd_method(pool):
            for d in pool['dests']:
                if 'fwd_method' in d:
                    del(d['fwd_method'])
            return pool
        assert [remove_fwd_method(p) for p in pools] == [p.to_dict() for p in ipvs_client.get_pools()]
