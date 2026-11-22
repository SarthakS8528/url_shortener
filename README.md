
# 🔗 URL Shortener

A backend URL shortening service built using **FastAPI, PostgreSQL, SQLAlchemy, and Redis**.

The application converts long URLs into compact, shareable links while supporting custom aliases, expiration, click tracking, and analytics. It uses Redis caching to reduce repeated database lookups and Docker Compose for containerized deployment.

## ✨ Features

- **URL Shortening:** Generate unique short codes for long URLs.
- **Custom Aliases:** Create personalized short URLs.
- **URL Expiration:** Configure expiration timestamps for shortened links.
- **HTTP Redirection:** Redirect users using HTTP 302 responses.
- **Redis Caching:** Implement cache-aside caching to reduce database reads.
- **Click Tracking:** Record visits with timestamps and IP addresses.
- **Click Analytics:** Retrieve total clicks for individual shortened URLs.
- **Database Migrations:** Manage schema changes using Alembic.
- **Containerization:** Run the application and its dependencies using Docker Compose.
- **Automated Testing:** Test core API functionality using Pytest and FastAPI TestClient.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | FastAPI |
| Programming Language | Python 3.11 |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Caching | Redis |
| Database Migrations | Alembic |
| Containerization | Docker & Docker Compose |
| Testing | Pytest, HTTPX |

---

## 🏗️ Architecture

The application follows a layered architecture where FastAPI handles incoming HTTP requests, PostgreSQL provides persistent storage, and Redis acts as a caching layer.

### System Architecture

```mermaid
flowchart TD
    A[Client] --> B[FastAPI Application]
    B --> C[API Routes]
    C --> D[Service Layer]
    D --> E[(PostgreSQL)]
    C <--> F[(Redis Cache)]
    E --> G[URLs Table]
    E --> H[Clicks Table]
```

### URL Redirection Flow

The application uses the **Cache-Aside Pattern** to optimize URL redirection.

```mermaid
flowchart TD
    A[Client requests short URL] --> B[Check Redis Cache]
    B -->|Cache Hit| C[Retrieve original URL]
    B -->|Cache Miss| D[Query PostgreSQL]
    D --> E{URL exists and is valid?}
    E -->|No| F[Return 404]
    E -->|Yes| G[Store URL in Redis]
    G --> C
    C --> H[Record Click in PostgreSQL]
    H --> I[HTTP 302 Redirect]
```

### Caching Strategy

- **Cache Lookup:** When a short URL is requested, the application first checks Redis for the corresponding URL.
- **Cache Hit:** If the URL exists in Redis, the cached destination is retrieved without querying PostgreSQL.
- **Cache Miss:** If the URL is unavailable in Redis, PostgreSQL is queried.
- **Cache Population:** The retrieved URL is stored in Redis for subsequent requests.
- **TTL Management:** Cache entries have a default TTL of 3600 seconds. If a URL has an expiration time, the cache TTL is restricted to its remaining validity period.
- **Fault Tolerance:** If Redis is unavailable, the application falls back to PostgreSQL.

This reduces repeated database reads while keeping PostgreSQL as the source of truth.

---

## 🗄️ Database Schema

The application uses PostgreSQL with two primary tables: `urls` and `clicks`.

### Entity Relationship Diagram

```mermaid
erDiagram
    URLS ||--o{ CLICKS : records

    URLS {
        int id PK
        string original_url
        string short_code UK
        datetime created_at
        datetime expires_at
        boolean is_active
        string description
    }

    CLICKS {
        int id PK
        int url_id FK
        datetime clicked_at
        string ip_address
    }
```

### Table Descriptions

#### 1. `urls`

Stores information about shortened URLs.

| Column | Description |
|---|---|
| `id` | Primary key |
| `original_url` | Original destination URL |
| `short_code` | Unique identifier for the shortened URL |
| `created_at` | URL creation timestamp |
| `expires_at` | Optional expiration timestamp |
| `is_active` | Indicates whether the URL is active |
| `description` | Optional URL description |

#### 2. `clicks`

Stores individual visits to shortened URLs.

| Column | Description |
|---|---|
| `id` | Primary key |
| `url_id` | Foreign key referencing `urls.id` |
| `clicked_at` | Timestamp of the visit |
| `ip_address` | IP address of the visitor |

### Relationship

- A URL can have multiple associated click records.
- Each click belongs to exactly one URL.
- The foreign key uses `ON DELETE CASCADE` to maintain referential integrity.
- SQLAlchemy relationships manage the one-to-many association between URLs and clicks.

---

## 📡 API Documentation

The application exposes three primary endpoints.

### 1. Create a Short URL

Creates a shortened URL with an automatically generated code or a custom alias.

**Endpoint:** `POST /shorten`

**Request Body:**

```json
{
  "original_url": "https://www.youtube.com/",
  "custom_alias": "myvideo",
  "expires_at": null
}
```

`custom_alias` and `expires_at` are optional.

**Successful Response:** `201 Created`

```json
{
  "original_url": "https://www.youtube.com/",
  "short_code": "myvideo",
  "short_url": "http://localhost:8000/myvideo",
  "created_at": "2026-11-21T10:30:00",
  "expires_at": null
}
```

### 2. Redirect to Original URL

Redirects the client to the original destination associated with the supplied short code.

**Endpoint:** `GET /{short_code}`

**Example:**

```http
GET /myvideo
```

**Successful Response:** `302 Found`

The response contains a `Location` header pointing to the original URL.

**Possible Error Response:**

- `404 Not Found` — Short code does not exist, is inactive, or has expired.

### 3. Retrieve URL Analytics

Returns click statistics for a shortened URL.

**Endpoint:** `GET /analytics/{short_code}`

**Example:**

```http
GET /analytics/myvideo
```

**Successful Response:** `200 OK`

```json
{
  "short_code": "myvideo",
  "original_url": "https://www.youtube.com/",
  "total_clicks": 42,
  "created_at": "2026-11-21T10:30:00",
  "expires_at": null
}
```

The analytics endpoint reports the total number of recorded clicks associated with the shortened URL.

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/SarthakS8528/url-shortener.git
cd url_shortener
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://admin:password@localhost:5432/urlshortener
REDIS_URL=redis://localhost:6379/0
BASE_URL=http://localhost:8000
```

> Docker Compose overrides the database and Redis URLs for the application container, using the internal service names `postgres` and `redis`.

### 3. Build and Start the Application

```bash
docker compose up --build -d
```

This starts the following services:

- FastAPI application
- PostgreSQL database
- Redis cache

### 4. Apply Database Migrations

```bash
docker compose exec app alembic upgrade head
```

### 5. Access the Application

Once the containers are running, access:

| Resource | URL |
|---|---|
| API Base URL | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

### 6. Stop the Application

To stop the containers:

```bash
docker compose down
```

To stop containers and remove the database volume as well:

```bash
docker compose down -v
```

> **Warning:** The `-v` option deletes persisted PostgreSQL data.

---

## 🧪 Running Tests

The project uses **Pytest** and FastAPI's `TestClient` to verify core application functionality.

Run the test suite from the project root:

```bash
python -m pytest -v
```

### Test Coverage

The current test suite verifies:

| Test Case | Description |
|---|---|
| URL Creation | Verifies successful creation of a shortened URL |
| Duplicate Alias | Ensures duplicate custom aliases are rejected |
| URL Redirection | Verifies HTTP 302 redirection to the original URL |
| Click Analytics | Verifies that recorded clicks are reflected in analytics |

---

## 📁 Project Structure

```text
url_short/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── redis_client.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── urls.py
│   │
│   └── services/
│       ├── __init__.py
│       └── url_service.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_urls.py
│
├── alembic/
├── .env
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔮 Future Improvements

Potential enhancements for future iterations include:

- **Rate Limiting:** Protect API endpoints against excessive requests.
- **Authentication:** Introduce user accounts and ownership of shortened URLs.
- **Advanced Analytics:** Add daily click trends, geographic insights, and referral tracking.
- **Asynchronous Click Processing:** Use a message queue or background workers to improve redirect throughput.
- **Load Testing:** Evaluate application performance under concurrent traffic.
- **CI/CD:** Automate testing and deployment using GitHub Actions.

---

## 👨‍💻 Author

**Sarthak Srivastava**

- GitHub: (https://github.com/SarthakS8528)
- LinkedIn: (www.linkedin.com/in/sarthak-srivastava-a7070227a)
