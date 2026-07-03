from app.services.auth import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_token():
    subject = "test-user-id"
    token = create_access_token(subject=subject)
    payload = decode_access_token(token)
    assert payload["sub"] == subject
