"""Unit tests for security utilities."""

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password():
    password = "testpassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0


def test_verify_password():
    password = "testpassword123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    data = {"sub": "1", "role": "agent"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_refresh_token():
    data = {"sub": "1", "role": "agent"}
    token = create_refresh_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_access_token():
    data = {"sub": "1", "role": "agent"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["role"] == "agent"
    assert payload["type"] == "access"


def test_decode_refresh_token():
    data = {"sub": "1", "role": "admin"}
    token = create_refresh_token(data)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["type"] == "refresh"


def test_decode_invalid_token():
    payload = decode_token("invalid-token")
    assert payload is None
