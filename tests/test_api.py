from unittest.mock import patch

from django.urls import reverse
from django.test.client import Client


def test_ping():
    client = Client()
    response = client.get(reverse("api:ping"), content_type="application/json")
    assert response.status_code == 200
    assert response.json() == {"response": "pong"}


def test_auth_bad_creds():
    client = Client()
    response = client.post(
        reverse("api:auth"),
        content_type="application/json",
        data={
            "engine": "email",
            "credentials": {
                "email": "some@email",
                "password": "StrongPassword",
            },
        },
    )
    assert response.status_code == 401


def test_app_version_view():
    client = Client()
    response = client.get(reverse("api:app_versions"), content_type="application/json")
    assert response.status_code == 200
    assert response.json() == {"lamb": "3.0.0", "api": "0.0.1"}


def test_handbooks_list_view():
    client = Client()
    response = client.get(reverse("api:handbooks_list"), content_type="application/json")
    assert response.status_code == 200


def test_handbook_view():
    client = Client()

    # Проверка эндпоинта с handbook_name = "configs"
    handbook_name_configs = "configs"
    response_configs = client.get(reverse("api:handbooks_item_list", args=[handbook_name_configs]),
                                  content_type="application/json")
    assert response_configs.status_code == 200
    # Проверка содержимого ответа для handbook_name = "configs"
    expected_configs = [
        {"name": "access_token_timeout", "value": 4320, "description": "Access token availability time, min"},
        {"name": "refresh_token_timeout", "value": 43200, "description": "Refresh token availability time, min"}
    ]
    assert response_configs.json() == expected_configs

    # Проверка эндпоинта с handbook_name = "user_types"
    handbook_name_user_types = "user_types"
    response_user_types = client.get(reverse("api:handbooks_item_list", args=[handbook_name_user_types]),
                                     content_type="application/json")
    assert response_user_types.status_code == 200
    # Проверка содержимого ответа для handbook_name = "user_types"
    expected_user_types = ["SUPER_ADMIN", "OPERATOR", "USER"]
    assert response_user_types.json() == expected_user_types


def test_auth_register_view():
    client = Client()
    credentials = {
        "email": "super_admin@example.com",
        "password": "StrongPass777",
    }
    response = client.post(
        reverse("api:auth"),
        content_type="application/json",
        data={
            "engine": "email",
            "credentials": credentials,
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user" in response.json()


def test_user_view():
    client = Client()
    response = client.get(reverse("api:user"), content_type="application/json")
    assert response.status_code == 200
    assert response.json() == []


@patch("api.views.store_exchanges_rates_task.apply_async")
def test_store_exchange_rates_view(mock_apply_async):
    client = Client()
    response = client.post(reverse("api:store_exchanges_rates"), content_type="application/json")
    assert response.status_code == 201
    assert mock_apply_async.called
