import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("supersecret123")
    assert h != "supersecret123"
    assert verify_password("supersecret123", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token = create_access_token(user_id=7, org_id=3)
    payload = decode_access_token(token)
    assert payload["sub"] == "7"
    assert payload["org"] == 3


def test_jwt_garbage_returns_none():
    assert decode_access_token("not.a.jwt") is None


@pytest.mark.asyncio
async def test_register_and_login(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "owner@acme.com", "password": "password123", "org_name": "Acme"},
    )
    assert r.status_code == 201
    assert r.json()["access_token"]

    # duplicate
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "owner@acme.com", "password": "password123", "org_name": "Acme"},
    )
    assert r.status_code == 409

    r = await client.post(
        "/api/v1/auth/login", json={"email": "owner@acme.com", "password": "password123"}
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = await client.post("/api/v1/auth/login", json={"email": "owner@acme.com", "password": "nope"})
    assert r.status_code == 401
    return token


@pytest.mark.asyncio
async def test_protected_route_requires_token(client, real_auth):
    # With the override removed, no Authorization header -> 401
    r = await client.post("/api/v1/seo/keywords", json={"seed": "x"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_real_token_grants_access(client, real_auth):
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "u@acme.com", "password": "password123", "org_name": "Acme"},
    )
    token = reg.json()["access_token"]
    r = await client.get("/api/v1/org", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["name"] == "Acme"
