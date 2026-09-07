def test_register_new_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_rejected(client):
    payload = {"email": "dupe@example.com", "password": "strongpassword123"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


def test_login_with_correct_credentials(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "strongpassword123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "strongpassword123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "password": "strongpassword123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass@example.com", "password": "notthepassword"},
    )
    assert response.status_code == 401