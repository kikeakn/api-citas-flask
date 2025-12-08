import json


def test_register_login_and_get_centers(client):
    # 1. Registro de usuario
    register_payload = {
        "username": "usuario_test",
        "password": "password_test",
        "name": "Nombre",
        "lastname": "Apellido",
        "email": "test@example.com",
        "phone": "600000000",
        "date": "01/01/2000",
    }

    r = client.post(
        "/register",
        data=json.dumps(register_payload),
        content_type="application/json",
    )
    assert r.status_code == 200

    # 2. Login
    login_payload = {"username": "usuario_test", "password": "password_test"}
    r = client.post(
        "/login",
        data=json.dumps(login_payload),
        content_type="application/json",
    )
    assert r.status_code == 200

    data = r.get_json()
    assert "access_token" in data
    token = data["access_token"]

    # 3. Obtener centros
    r = client.get("/centers", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    centers = r.get_json()
    assert isinstance(centers, list)
    assert len(centers) >= 2
