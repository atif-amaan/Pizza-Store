# Pizza Store Management API

A RESTful backend API for managing a pizza store — built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. Features full JWT-based authentication (access + refresh token flow), role-based access control, and complete order lifecycle management.

---

## Features

- **JWT Authentication** — Secure login with separate access & refresh token flow
- **Role-Based Access Control** — Staff vs. regular user permissions
- **Order Management** — Full CRUD for pizza orders with status tracking
- **Input Validation** — Pydantic v2 schemas with email validation and type constraints
- **Auto-generated Docs** — Interactive Swagger UI at `/docs`
- **PostgreSQL** — Production-ready relational database via SQLAlchemy ORM

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL |
| Auth | JWT (PyJWT) + Werkzeug password hashing |
| Validation | Pydantic v2 |
| Config | pydantic-settings + `.env` |
| Server | Uvicorn |

---

## Project Structure

```
Pizza_managment/
├── main.py                  # App entry point, router registration
├── requirements.txt
├── .env                     # Environment variables (not committed)
├── docs/
│   └── ROUTES.md            # API route reference
└── src/
    ├── user/
    │   ├── user_models.py   # SQLAlchemy UserModel
    │   ├── user_schema.py   # Pydantic schemas (Register, Login, UserResponse)
    │   ├── user_routers.py  # Auth routes (/user/...)
    │   └── controller.py    # Auth business logic + JWT helpers
    └── order/
    │   ├── order_models.py  # SQLAlchemy OrderModel
    │   ├── order_schema.py  # Pydantic schemas (OrderSchema, PatchOrder, ...)
    │   ├── order_routers.py # Order routes (/order/...)
    │   └── controller.py    # Order business logic
    └── utils/
        ├── db.py            # DB engine, session, get_db dependency
        └── settings.py      # pydantic-settings config
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- PostgreSQL running locally or via a cloud provider

### 1. Clone the repository
```bash
git clone https://github.com/atif-amaan/Pizza-Store.git
cd Pizza-Store
```

### 2. Create a virtual environment
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/macOS
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/pizza_db
JWT_SECRET=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_TIME=30        # minutes
REFRESH_TOKEN_EXPIRY_TIME=7        # days
```

### 5. Run the server
```bash
uvicorn main:app --reload
```

API will be available at `http://127.0.0.1:8000`  
Swagger UI at `http://127.0.0.1:8000/docs`

---

## API Endpoints

### Auth — `/user`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/user/register` | Register a new user | No |
| `POST` | `/user/login` | Login — returns access + refresh tokens | No |
| `GET` | `/user/auth` | Get currently authenticated user | Bearer token |
| `GET` | `/user/refresh` | Exchange refresh token for new access token | Bearer token |

### Orders — `/order`

| Method | Endpoint | Description | Auth | Staff Only |
|--------|----------|-------------|------|------------|
| `POST` | `/order/create_order` | Place a new pizza order | Yes | No |
| `GET` | `/order/orders` | Get all orders | Yes | Yes |
| `GET` | `/order/orders/{user_id}` | Get all orders for a specific user | Yes | Yes |
| `GET` | `/order/user/orders/{order_id}` | Get a specific order (owner or staff) | Yes | No |
| `PATCH` | `/order/orders/update/{order_id}` | Update order details | Yes | No |
| `PATCH` | `/order/orders/status/{order_id}` | Update order status | Yes | Yes |
| `DELETE` | `/order/orders/delete/{order_id}` | Delete an order | Yes | Yes |

---

## Authentication Flow

```
POST /user/register  ->  Create account
POST /user/login     ->  { access_token, refresh_token, token_type: "bearer" }

All protected endpoints:
  Authorization: Bearer <access_token>

When access token expires:
GET /user/refresh    ->  Authorization: Bearer <refresh_token>
                     <-  { access_token, token_type: "bearer" }
```

---

## Order Status Lifecycle

```
pending  ->  in-transit  ->  delivered
```

Pizza sizes: `small` | `medium` | `large` | `extra-large`

---

## Security Notes

- Passwords are hashed using Werkzeug's PBKDF2-SHA256
- JWT tokens are signed with HMAC (configurable algorithm via `.env`)
- `is_active` and `is_staff` flags are never accepted from the client — set server-side only
- DB-level `UNIQUE` constraints on `username` and `email`
- Generic error messages on login to prevent user enumeration

---

## Swagger UI

Once the server is running, visit [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) for the full interactive API documentation.

---

## License

This project is open source and available under the [MIT License](LICENSE).
