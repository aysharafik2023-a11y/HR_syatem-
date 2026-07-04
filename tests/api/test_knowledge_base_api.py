"""API tests for knowledge base endpoints."""


def test_create_knowledge_entry(client, admin_auth_headers):
    response = client.post(
        "/api/v1/knowledge-base",
        json={
            "title": "Password Reset Guide",
            "content": "To reset your password, go to Settings > Security > Reset Password.",
            "category": "account",
            "tags": "password,reset,security",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Password Reset Guide"
    assert data["category"] == "account"


def test_create_knowledge_entry_unauthorized(client, auth_headers):
    response = client.post(
        "/api/v1/knowledge-base",
        json={
            "title": "Test",
            "content": "Test content",
            "category": "test",
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_list_knowledge_entries(client, auth_headers, admin_auth_headers):
    # Create entries as admin
    for i in range(3):
        client.post(
            "/api/v1/knowledge-base",
            json={
                "title": f"Article {i}",
                "content": f"Content {i}",
                "category": "general",
            },
            headers=admin_auth_headers,
        )

    response = client.get("/api/v1/knowledge-base", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_search_knowledge_base(client, auth_headers, admin_auth_headers):
    client.post(
        "/api/v1/knowledge-base",
        json={
            "title": "How to Reset Password",
            "content": "Navigate to settings and click reset.",
            "category": "account",
            "tags": "password,reset",
        },
        headers=admin_auth_headers,
    )
    client.post(
        "/api/v1/knowledge-base",
        json={
            "title": "Billing FAQ",
            "content": "You can update your payment method in billing settings.",
            "category": "billing",
            "tags": "payment,billing",
        },
        headers=admin_auth_headers,
    )

    response = client.get("/api/v1/knowledge-base/search?q=password", headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any("Password" in r["title"] for r in results)


def test_delete_knowledge_entry(client, admin_auth_headers):
    create_response = client.post(
        "/api/v1/knowledge-base",
        json={
            "title": "To Delete",
            "content": "Will be deleted",
            "category": "test",
        },
        headers=admin_auth_headers,
    )
    entry_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/knowledge-base/{entry_id}", headers=admin_auth_headers)
    assert response.status_code == 204
