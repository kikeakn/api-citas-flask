import json


def _register_and_login(client):
    # Crear usuario de pruebas
    client.post(
        "/register",
        data=json.dumps(
            {
                "username": "user_dates",
                "password": "password_dates",
                "name": "Nombre",
                "lastname": "Apellido",
                "email": "dates@example.com",
                "phone": "611111111",
                "date": "02/02/2000",
            }
        ),
        content_type="application/json",
    )

    # Login
    r = client.post(
        "/login",
        data=json.dumps(
            {"username": "user_dates", "password": "password_dates"}
        ),
        content_type="application/json",
    )
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_create_list_and_delete_date(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Crear cita
    create_payload = {
        "center": "Centro de Salud Madrid Norte",
        "date": "25/12/2025 14:00:00",
    }
    r = client.post(
        "/date/create",
        data=json.dumps(create_payload),
        content_type="application/json",
        headers=headers,
    )
    assert r.status_code == 200

    # 2. Listar citas del usuario
    r = client.get("/date/getByUser", headers=headers)
    assert r.status_code == 200
    dates = r.get_json()
    assert len(dates) == 1

    # 3. Borrar cita
    delete_payload = {
        "center": "Centro de Salud Madrid Norte",
        "date": "25/12/2025 14:00:00",
    }
    r = client.post(
        "/date/delete",
        data=json.dumps(delete_payload),
        content_type="application/json",
        headers=headers,
    )
    assert r.status_code == 200

    # 4. Comprobar que ya no hay citas
    r = client.get("/date/getByUser", headers=headers)
    assert r.status_code == 200
    dates = r.get_json()
    assert dates == []
