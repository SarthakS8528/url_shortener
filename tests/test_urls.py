def test_create_short_url(client):

    response = client.post(
        "/shorten",
        json={
            "original_url": "https://youtube.com/",
            "custom_alias": "test123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["short_code"] == "test123"
    assert data["original_url"] == "https://youtube.com/"

def test_duplicate_custom_alias(client):

    payload = {
        "original_url": "https://youtube.com/",
        "custom_alias": "test123"
    }

    first_response = client.post(
        "/shorten",
        json=payload
    )

    second_response = client.post(
        "/shorten",
        json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_redirect_short_url(client):
    # First, create a short URL
    create_response = client.post(
        "/shorten",
        json={
            "original_url": "https://youtube.com/",
            "custom_alias": "redirect123"
        }
    )

    assert create_response.status_code == 201

    # Now, access the shortened URL
    redirect_response = client.get(
        "/redirect123",
        follow_redirects=False
    )

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == "https://youtube.com/"


def test_analytics_endpoint(client):
    # Create a short URL
    client.post(
        "/shorten",
        json={
            "original_url": "https://youtube.com/",
            "custom_alias": "analytics123"
        }
    )

    # Visit the shortened URL to generate a click
    client.get("/analytics123", follow_redirects=False)

    # Fetch analytics
    response = client.get("/analytics/analytics123")

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == "analytics123"
    assert data["total_clicks"] == 1
