"""Defines fixtures available to all tests."""
import os
import pytest

import cronos

TEST_PATH = 'tests'


@pytest.fixture(scope='module')
def app():
    return cronos.app.test_client()

@pytest.fixture(scope='module')
def login():
    return [os.environ['MINERVA_USER'], os.environ['MINERVA_SECRET']]


w14_path = os.path.join(TEST_PATH, 'winter_2014.html')


@pytest.fixture(scope="module")
def w14_info(login):
    return login + ['winter', 2014]


@pytest.fixture(scope="module")
def w14_html(login):
    return open(w14_path).read()
