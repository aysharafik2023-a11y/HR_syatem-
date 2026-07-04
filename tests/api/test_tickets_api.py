"""API tests for ticket endpoints."""


def test_create_ticket(client, auth_headers):
    response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Test Customer",
            "customer_email": "customer@example.com",
            "subject": "Help with login",
            "description": "I cannot login to my account since yesterday.",
            "channel": "web_portal",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Test Customer"
    assert data["subject"] == "Help with login"
    assert data["status"] == "open"


def test_create_ticket_unauthorized(client):
    response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Test",
            "customer_email": "test@example.com",
            "subject": "Test",
            "description": "Test",
        },
    )
    assert response.status_code == 403


def test_list_tickets(client, auth_headers):
    # Create tickets
    for i in range(3):
        client.post(
            "/api/v1/tickets",
            json={
                "customer_name": f"Customer {i}",
                "customer_email": f"c{i}@example.com",
                "subject": f"Issue {i}",
                "description": f"Description {i}",
            },
            headers=auth_headers,
        )

    response = client.get("/api/v1/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["tickets"]) == 3


def test_list_tickets_pagination(client, auth_headers):
    for i in range(5):
        client.post(
            "/api/v1/tickets",
            json={
                "customer_name": f"Customer {i}",
                "customer_email": f"c{i}@example.com",
                "subject": f"Issue {i}",
                "description": f"Description {i}",
            },
            headers=auth_headers,
        )

    response = client.get("/api/v1/tickets?page=1&page_size=2", headers=auth_headers)
    data = response.json()
    assert data["total"] == 5
    assert len(data["tickets"]) == 2
    assert data["page"] == 1


def test_get_ticket(client, auth_headers):
    create_response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Jane",
            "customer_email": "jane@example.com",
            "subject": "Billing question",
            "description": "When is my next payment?",
        },
        headers=auth_headers,
    )
    ticket_id = create_response.json()["id"]

    response = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_get_ticket_not_found(client, auth_headers):
    response = client.get("/api/v1/tickets/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_ticket(client, auth_headers):
    create_response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Mike",
            "customer_email": "mike@example.com",
            "subject": "Bug report",
            "description": "App crashes on startup",
        },
        headers=auth_headers,
    )
    ticket_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/tickets/{ticket_id}",
        json={"status": "in_progress", "priority": "high"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["priority"] == "high"


def test_delete_ticket(client, auth_headers):
    create_response = client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Delete Me",
            "customer_email": "delete@example.com",
            "subject": "To delete",
            "description": "This will be deleted",
        },
        headers=auth_headers,
    )
    ticket_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 404
