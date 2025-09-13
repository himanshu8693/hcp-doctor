import pytest
from flask.testing import FlaskClient
import importlib
import sys

@pytest.fixture(scope="module")
def app():
    # Import the Flask app from the web module
    sys.modules.pop('hashicorp_doctor.web', None)  # Ensure fresh import
    web_mod = importlib.import_module('hashicorp_doctor.web')
    return web_mod.app

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

def test_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'HashiCorp Doctor' in resp.data

def test_vault_page(client):
    resp = client.get('/vault')
    assert resp.status_code == 200
    assert b'Vault Diagnostics' in resp.data

def test_consul_page(client):
    resp = client.get('/consul')
    assert resp.status_code == 200
    assert b'Consul Diagnostics' in resp.data

def test_nomad_page(client):
    resp = client.get('/nomad')
    assert resp.status_code == 200
    assert b'Nomad Diagnostics' in resp.data


def test_html_report(client):
    resp = client.get('/report/html')
    assert resp.status_code == 200
    assert b'<html>' in resp.data

def test_html_report_download(client):
    resp = client.get('/report/html/download')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'].startswith('text/html')
    assert 'attachment' in resp.headers.get('Content-Disposition', '')

def test_txt_report(client):
    resp = client.get('/report/txt')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'].startswith('text/plain')
    assert 'attachment' in resp.headers.get('Content-Disposition', '')

