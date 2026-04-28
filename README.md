# API Routes

This document lists the application's HTTP routes, with a short description, authentication requirement, request body , response model, and status codes.

**Root**
- **GET /**: Returns a simple greeting message. No auth. Response: {"message": "Hello World!"} (200)

**User (prefix: /user)**
- **POST /user/register**: Register a new user. Request: `Register` model. Response: `UserResponse` (201).
- **POST /user/login**: Login and receive tokens. Request: `Login` model. Response: token payload (202).
- **GET /user/auth**: Authenticate user from request (uses cookies/headers). Requires auth. Response: `UserResponse` (200).
- **GET /user/refresh**: Exchange refresh token for new access token. Uses request (cookie/header). Response: access token (200).

**Order (prefix: /order)**
- **POST /order/create_order**: Create an order. Requires authenticated user. Request: `OrderSchema`. Response: `OrderResponse` (201).
- **GET /order/orders**: Get all orders (superuser/staff only). Requires auth and staff role check. Response: list[`OrderModel`] (200).
- **GET /order/orders/{user_id}**: Get all orders for a specific user (superuser only). Requires auth and staff role. Response: list[`OrderModel`] (200).
- **GET /order/user/orders/{order_id}**: Get a specific order for a user. Only the order owner or staff can access. Requires auth. Response: `OrderModel` (200).
- **PATCH /order/orders/update/{order_id}**: Update an order (partial). Requires auth and owner or staff. Request: `PatchOrder`. Response: `PatchOrderResponse` (202).
- **PATCH /order/orders/status/{order_id}**: Update order status (staff or owner as implemented). Requires auth. Request: `OrderStatusUpdate`. Response: `PatchOrderResponse` (202).
- **DELETE /order/orders/delete/{order_id}**: Delete an order. Requires auth and appropriate permission. Response: status (202).

Notes:
- Models referenced are defined under `src/user/user_schema.py` and `src/order/order_schema.py`.
- Authentication dependency is provided by `src/user/controller.py` (`get_current_user`, `authentication`).
- Database dependency `get_db` (SQLAlchemy `Session`) is provided by `src/utils/db.py`.
