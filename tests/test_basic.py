def test_root_endpoint(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Hello, World!" in resp.data


def test_apidocs_accessible(client):
    resp = client.get("/apidocs")
    # Puede devolver 200 o redirigir a /apidocs/
    assert resp.status_code in (200, 301, 302, 308)
