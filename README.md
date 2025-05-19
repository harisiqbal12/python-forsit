# Project Documentation
## Overview
This project is a Python-based backend application using FastAPI, PostgreSQL, Redis, and Kafka. It supports user management, product and inventory management, order processing, sales tracking, and more. The project uses Alembic for database migrations and Docker Compose for local development.

## Table of Contents
1. Project Structure
2. Setup Instructions
3. Environment Variables
4. Database Schema & Diagram
5. Running Migrations
6. Running the Application
7. Database Dump & Restore
8. Security (RLS)
9. Testing
10. Useful Commands
## Project Structure
```
python_assign/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schema/
│   └── main.py
├── migrations/
│   ├── sql/
│   │   ├── v1__create_table.sql
│   │   ├── v2__create_tables_indexes.sql
│   │   ├── V3__sales_table.sql
│   │   └── V4__enable_rls.sql
│   └── versions/
├── seed/
│   └── db_data_dump.sql
├── tests/
├── docker-compose.yml
├── .env
├── requirement.txt
└── main.py
```
## Setup Instructions
### 1. Clone the Repository
```
git clone <your-repo-url>
cd python_assign
```
### 2. Create and Activate Virtual Environment
```
python3 -m venv virtual
source virtual/bin/activate
```
### 3. Install Dependencies
```
pip3 install -r requirement.txt
```
### 4. Configure Environment Variables
Copy .env and adjust values if needed.

## Environment Variables
The .env file contains:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=66f3f58cb1210164f47909106190eef336f38224adb69018b98337089df159de
ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_ALGORITHM=HS256
HTTP_MAX_ATTEMPTS=5
HTTP_ATTEMPT_COOLDOWN=60
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_ORDER=orders_event
KAFKA_GROUP_ID=forsit_group
REDIS_INCOMING_ORDER=CHANNEL_INCOMING_ORDER
REDIS_LOW_INVENTORY=REDIS_LOW_INVENTORY
KAFKA_TOPIC_SALES=sales_event
REDIS_QUEUE_ORDER=REDIS_QUEUE_ORDER
```
## Database Schema
### Main Tables
- users : User accounts
- category : Product categories (self-referencing parent)
- product : Products (linked to category and user)
- investory : Inventory for products
- inventory_history : Inventory change logs
- sales_channel : Sales channels (e.g., online, retail)
- orders : Orders (linked to sales_channel)
- order_items : Items in each order (linked to product)
- sales : Sales records (linked to orders, order_items, product, etc.)
- sales_snapshot : Aggregated sales data
## Running Migrations
1. Ensure PostgreSQL is running (via Docker Compose or locally).
2. Run Alembic migrations:
```
alembic upgrade head
```
This will apply all migrations, including schema, indexes, and RLS.

## Running the Application
### Using Docker Compose
```
docker-compose up --build
```
This will start all services: app, postgres, redis, kafka, zookeeper.

### Running Locally
1. Start PostgreSQL, Redis, and Kafka (see docker-compose for configuration).
2. Run the FastAPI app:
```
uvicorn app.main:app --reload
```
## Database Dump & Restore
### Dump Data
```
pg_dump -U postgres -h localhost -p 5432 -d fastapi_db --inserts > seed/db_data_dump.sql
```
### Restore Data
```
psql -U postgres -h localhost -p 5432 -d fastapi_db < seed/db_data_dump.sql
```
## Security (RLS)
Row Level Security (RLS) is enabled on all main tables. Note: By default, a permissive policy is set for users (for demo).

## Testing
To run tests (if available):

```
pytest
```
## Useful Commands
- Build Docker Images: docker-compose build
- Start Services: docker-compose up
- Stop Services: docker-compose down
- Run Alembic Migration: alembic upgrade head
- Dump Database: pg_dump ...
- Restore Database: psql ...
- dump database: 
```
docker exec -i python_assign-postgres-1 psql -U postgres -d fastapi_db < /Users/harisiqbal/Develop/python_assign/seed/db_data_dump.sql
```

## Notes
- All SQL migrations are in migrations/sql/ .
- Alembic migration scripts are in migrations/versions/ .
- Models are in app/models/ .
- Adjust environment variables as needed for your deployment.


---

## API Endpoints

### **1. Login**

**Endpoint:** `POST /api/v1/user/login`

**Description:**
Accepts an email or username along with a password. Upon successful authentication, returns a secure JWT token.

**Features:**

* Implements rate limiting using Redis.
* The returned JWT token is stored in Redis for session management.
* Each user is allowed only one active session at a time.

---

### **2. Register**

**Endpoint:** `POST /api/v1/user/register`

**Description:**
Accepts user data based on the `UserCreate` schema and registers a new user. Upon success, returns a secure JWT token.

**Features:**

* Implements rate limiting using Redis.
* The JWT token is stored in Redis, similar to the login endpoint.
* Follows the same session management strategy as login (one session per user).

---

### **3. Get Products**

**Endpoint:** `GET /api/v1/product`

**Description:**
Retrieves a list of products with support for searching, filtering, sorting, and pagination.

**Query Parameters:**

* `search` (string, optional): Matches against SKU, name, or description.
* `category_id` (string, optional): Filters products by category ID.
* `created_by` (string, optional): Filters products by the creator's user ID.
* `sort_price` (string, optional): Sorts by price (`asc` or `desc`).
* `sort_cost_price` (string, optional): Sorts by cost price (`asc` or `desc`).
* `sort_name` (string, optional): Sorts by product name (`asc` or `desc`).
* `sort_created_at` (string, optional): Sorts by creation date (`asc` or `desc`).
* `limit` (integer, optional, default=20): Maximum number of products to return.
* `skip` (integer, optional, default=0): Number of products to skip (for pagination).

**Response:**

```json
{
  "message": "Status message",
  "data": [/* List of products as ProductSecondarySchema */],
  "total": 100,
  "limit": 20,
  "skip": 0
}
```

**Notes:**

* Supports flexible querying through chaining of search, filter, and sort parameters.
* Pagination is controlled using `limit` and `skip`.
* Sorting is available on `price`, `cost_price`, `name`, and `created_at`—each can be sorted independently.

---


---

## GET `/product/{product_sku}`

**Description:**  
Retrieve detailed information about a single product using its SKU.

**Path Parameters:**
- `product_sku` (string, required): The SKU (Stock Keeping Unit) of the product to retrieve.

**Query Parameters:**  
_None_

**Request Example:**
```
GET /product/ABC123
```

**Response:**
- `message`: A status message indicating the result.
- `data`: The product details, validated using `ProductSchema`.

**Response Example:**
```json
{
  "message": "Product retrieve successful",
  "data": {
    // Fields as defined in ProductSchema, e.g.:
    "id": "uuid-string",
    "name": "Product Name",
    "sku": "ABC123",
    "description": "Product description",
    "price": 100.0,
    "cost_price": 80.0,
    "avatar": "image_url",
    "status": "active",
    "created_by": "user_id",
    "category_id": "category_id",
    "creator": { /* user info */ },
    "category": { /* category info */ },
    // ...other fields...
  }
}
```

**Status Codes:**
- `200 OK`: Product found and returned successfully.
- `404 Not Found`: No product exists with the given SKU.

**Error Response Example:**
```json
{
  "detail": "Product not found"
}
```

**Notes:**
- The endpoint loads related `creator` and `category` information using SQLAlchemy's `joinedload`.
- If the product is not found, a 404 error is returned.
- The returned data structure is defined by your `ProductSchema` and may include nested user and category information.

---

This endpoint is useful for retrieving all details about a specific product by its SKU, including related creator and category data.

---

## POST `/product/`

**Description:**  
Create a new product in the system.

**Request Body:**  
- `name` (string, required): Name of the product.
- `description` (string, required): Description of the product.
- `sku` (string, required): Unique SKU for the product.
- `price` (number, required): Selling price of the product.
- `cost_price` (number, required): Cost price of the product.
- `avatar` (string, optional): URL or identifier for the product image.
- `status` (string, required): Status of the product.
- `category_identifier` (string, optional): Identifier for the product's category.

**Authentication:**  
- Requires the current user (via dependency injection).

**Behavior:**  
- If `category_identifier` is provided, the endpoint looks up the category and assigns its ID to the product.
- Attempts to create a new product with the provided details.
- If the SKU already exists, returns a 400 error with the message "Sku already exists".
- On other database errors, returns a 400 error with "Database integerity error".

**Response Example (Success):**
```json
{
  "message": "product added succesfully"
}
```

**Response Example (SKU Exists):**
```json
{
  "detail": "Sku already exists"
}
```

**Response Example (Other Error):**
```json
{
  "detail": "Database integerity error"
}
```

---

## PATCH `/product/{product_id}`

**Description:**  
Update an existing product by its UUID.

**Path Parameters:**  
- `product_id` (UUID, required): The UUID of the product to update.

**Request Body:**  
- Any subset of product fields as defined in `ProductUpdateSchema`.  
- If `category_identifier` is provided, the endpoint will update the product's category.

**Behavior:**  
- Looks up the product by `product_id`.
- If not found, returns a 404 error: "Unable to find the product".
- If `category_identifier` is provided, looks up the category and updates the product's `category_id`.
- Updates all other provided fields.
- On database integrity error, returns a 400 error: "Unable to update the product".
- On success, returns the updated product data.

**Response Example (Success):**
```json
{
  "message": "product updated successfully",
  "data": {
    // Product fields as defined in ProductSchema
  }
}
```

**Response Example (Product Not Found):**
```json
{
  "detail": "Unable to find the product"
}
```

**Response Example (Category Not Found):**
```json
{
  "detail": "Unable to find category with the provided identifier"
}
```

**Response Example (Integrity Error):**
```json
{
  "detail": "Unable to update the product"
}
```

---

**Notes:**
- Both endpoints use SQLAlchemy for database operations and handle integrity errors gracefully.
- The `PATCH` endpoint supports partial updates and category reassignment by identifier.
- Both endpoints require authentication and proper user context.

---

## GET `/sales-channels/`

**Description:**  
Retrieve a list of all sales channels.

**Method:**  
GET

**Request Parameters:**  
None

**Response Example:**
```json
{
  "message": "retrive sales channel list",
  "data": [
    {
      // SalesChannelSchema fields for each channel
    }
  ]
}
```

**Status Codes:**
- 200: List returned successfully

---

## POST `/sales-channels/`

**Description:**  
Add a new sales channel.

**Method:**  
POST

**Request Body:**
- `name` (string): Name of the sales channel
- `status` (string): Status of the sales channel

**Response Example (Success):**
```json
{
  "message": "added sales channel",
  "data": {
    // SalesChannelSchema fields for the created channel
  }
}
```

**Response Example (Failure):**
```json
{
  "detail": "unable to add sales channel at the moment"
}
```

**Status Codes:**
- 200: Sales channel added successfully
- 500: Failed to add sales channel

---

**Note:**  
- Both endpoints use standard HTTP status codes and return a message along with the relevant data.
- The POST endpoint expects a JSON body with the required fields for a sales channel.  
- Error handling is basic and returns a generic error message on failure.

        

---

## POST `/orders/`

**Description:**  
Place a new order.

**Method:**  
POST

**Request Body:**  
- Expects a JSON object matching the `OrderCreate` schema, which includes:
  - `channel_id`: ID of the sales channel
  - `order_date`: (optional) Date of the order
  - `status`: Status of the order
  - `customer_name`: Name of the customer
  - `customer_email`: Email of the customer
  - `shipping_address`: Shipping address
  - `billing_address`: Billing address
  - `items`: List of order items, each with:
    - `product_id`: ID of the product
    - `quantity`: Quantity ordered

**Authentication:**  
- Requires the current user (via dependency injection).

**Behavior:**  
- Generates a unique order number.
- Validates product existence, status, and inventory.
- Calculates total, tax, shipping, and discount amounts.
- Creates the order and order items in the database.
- Updates inventory and logs inventory history.
- Publishes order and sales events in the background.

**Response Example (Success):**
```json
{
  "message": "order placed successfully",
  "data": {
    // Order fields as defined in OrderSchema
  }
}
```

**Response Example (Product Not Found):**
```json
{
  "detail": "Product with id <product_id> does not exist"
}
```

**Response Example (Product Not Active):**
```json
{
  "detail": "Product with id <product_id> is not active"
}
```

**Response Example (Not Enough Inventory):**
```json
{
  "detail": "Not enough inventory for product id <product_id>. Requested: <quantity>, Available: <available_qty>"
}
```

**Response Example (General Error):**
```json
{
  "detail": "Failed to place order: <error message>"
}
```

**Status Codes:**
- 200: Order placed successfully
- 400: Bad request (e.g., product not active, not enough inventory)
- 404: Product not found
- 500: Internal server error (e.g., database or processing error)

---

**Notes:**
- The endpoint uses SQLAlchemy for database operations and handles errors with appropriate HTTP status codes.
- Background tasks are used to send order and sales events after the order is placed.
- The endpoint expects all required fields for order creation and validates inventory and product status before processing.

---

## GET `/inventory/{product_sku}`

**Description:**  
Retrieve the latest inventory details for a product by its SKU.

**Path Parameters:**
- `product_sku` (string, required): The SKU of the product whose inventory details are to be fetched.

**Features:**
- Joins the inventory with its related product.
- Returns the most recently created inventory record for the given SKU.
- If no inventory is found, returns a 404 error with a descriptive message.
- The response includes detailed inventory information as defined by `InventoryDetailsSchema`.

**Response Example (Success):**
```json
{
  "message": "product inventory details retrieved",
  "data": {
    // InventoryDetailsSchema fields
  }
}
```

**Response Example (Not Found):**
```json
{
  "detail": "Inventory not found for this product SKU"
}
```

---

## PATCH `/inventory/{inventory_id}`

**Description:**  
Update an existing inventory record by its UUID.

**Path Parameters:**
- `inventory_id` (UUID, required): The UUID of the inventory record to update.

**Request Body:**  
- Fields as defined in `InventoryUpdate`, such as:
  - `quantity` (integer, required): The new quantity for the inventory.
  - `last_restock_date` (date, optional): The date of the last restock.
  - `change_reason` (string, required): Reason for the inventory change.

**Features:**
- Fetches the latest inventory record by ID.
- Updates the quantity and optionally the last restock date.
- Records the change in `InventoryHistory` with previous and new quantities, reason, and user.
- Rolls back and returns a 500 error if the update fails.
- Returns the updated inventory details on success.

**Response Example (Success):**
```json
{
  "message": "inventory updated",
  "data": {
    // InventorySchema fields
  }
}
```

**Response Example (Not Found):**
```json
{
  "detail": "Inventory not found"
}
```

**Response Example (Failure):**
```json
{
  "detail": "Failed to update inventory and history"
}
```

---

## POST `/inventory/`

**Description:**  
Add a new inventory record for a product.

**Request Body:**  
- Fields as defined in `InventoryCreate`, such as:
  - `product_id` (UUID, required): The product to which this inventory belongs.
  - `quantity` (integer, required): The initial quantity.
  - `last_restock_date` (date, optional): The date of the last restock.
  - `change_reason` (string, required): Reason for the inventory addition.

**Features:**
- Checks if inventory already exists for the product and prevents duplicate active inventory.
- Creates a new inventory record and an associated inventory history record.
- Rolls back and returns a 500 error if the operation fails.
- Returns a success message on successful addition.

**Response Example (Success):**
```json
{
  "message": "Added inventory"
}
```

**Response Example (Already Exists):**
```json
{
  "detail": "Inventory already exists for this product please update instead"
}
```

**Response Example (Failure):**
```json
{
  "detail": "Failed to add inventory and history"
}
```

---

**General Notes:**
- All endpoints use dependency injection for database session and user context.
- Inventory changes are always logged in the inventory history for traceability.
- Error handling is robust, with clear messages for not found and failure cases.
- The API is designed to prevent duplicate inventory records for the same product and to ensure all changes are auditable.

---

## POST `/category/`

**Description:**  
Create a new category.

**Features:**
- Accepts a JSON body with fields: `name`, `description`, `status`, `identifier`, and optionally `parent_id`.
- Attempts to create a new category in the database.
- If the `identifier` is not unique, returns a 400 error with a clear message.
- On success, returns a message and the created category data.

**Request Body Example:**
```json
{
  "name": "Electronics",
  "description": "Electronic devices and gadgets",
  "status": "active",
  "identifier": "electronics",
  "parent_id": null
}
```

**Response Example (Success):**
```json
{
  "message": "category added successfully",
  "data": {
    // CategorySchema fields
  }
}
```

**Response Example (Identifier Exists):**
```json
{
  "detail": "category identifier already exists"
}
```

---

## GET `/category/{identifier}`

**Description:**  
Retrieve details of a category by its unique identifier.

**Features:**
- Accepts a path parameter `identifier` to look up the category.
- Recursively includes parent category details in the response.
- If the category is not found, returns a 404 error with a descriptive message.
- Returns a message and the category details, including parent hierarchy.

**Response Example (Success):**
```json
{
  "message": "retrieved category details",
  "data": {
    // CategorySchema fields, with a nested "parent" field if applicable
  }
}
```

**Response Example (Not Found):**
```json
{
  "detail": "unable to find category, invalid identifier"
}
```

---

## GET `/category/`

**Description:**  
Retrieve a list of all categories.

**Features:**
- Returns all categories in the database.
- Each category is serialized using `CategorySchema`.
- Returns a message and the list of categories.

**Response Example:**
```json
{
  "message": "successfully fetched the categories list",
  "data": [
    // Array of CategorySchema objects
  ]
}
```

---

**General Notes:**
- All endpoints use dependency injection for database access.
- Error handling is robust, with clear messages for unique constraint violations and not found cases.
- The category details endpoint supports recursive parent category inclusion, enabling hierarchical category structures.
- The API is designed for extensibility and clear client feedback on both success and failure.

---

## GET `/alerts/low-stock`

**Description:**  
Provides a real-time server-sent events (SSE) stream for low stock inventory alerts.

**Features:**
- Establishes a streaming connection using the `text/event-stream` media type.
- Subscribes to the Redis channel specified by `settings.REDIS_LOW_INVENTORY`.
- Immediately yields a connection status message:  
  `data: {"status": "connected"}\n\n`
- For every message published to the Redis low inventory channel, yields the message as an SSE event to the client.
- Keeps the connection alive with a short sleep (`time.sleep(0.01)`) between messages.
- Closes the Redis pubsub connection gracefully when the stream ends or is interrupted.

**Response Example (SSE event):**
```
data: {"status": "connected"}

data: {"sku": "ABC123", "quantity": 2}
```

---

## GET `/alerts/incoming-order`

**Description:**  
Provides a real-time server-sent events (SSE) stream for incoming order alerts.

**Features:**
- Establishes a streaming connection using the `text/event-stream` media type.
- Subscribes to the Redis channel specified by `settings.REDIS_INCOMING_ORDER`.
- Immediately yields a connection status message:  
  `data: {"status": "connected"}\n\n`
- For every message published to the Redis incoming order channel, yields the message as an SSE event to the client.
- Keeps the connection alive with a short sleep (`time.sleep(0.01)`) between messages.
- Closes the Redis pubsub connection gracefully when the stream ends or is interrupted.

**Response Example (SSE event):**
```
data: {"status": "connected"}

data: {"order_id": "ORD-20240519-XYZ1", "customer": "John Doe"}
```

---

**General Notes:**
- Both endpoints use Redis pub/sub to provide real-time notifications to clients via SSE.
- The endpoints are suitable for dashboards or UIs that need to react instantly to inventory or order events.
- The connection remains open, and clients receive updates as soon as events are published to the relevant Redis channels.
- Graceful resource cleanup is ensured by closing the pubsub connection in a `finally` block.


---

## GET `/sales/revenue`

**Description:**  
Retrieve aggregated revenue and sales count, grouped by a specified period.

**Features:**
- Supports grouping by `day`, `week`, `month`, or `year` using the `group_by` query parameter.
- Allows filtering by `start_date`, `end_date`, `product_id`, `category_id`, and `channel_id`.
- Returns total revenue and total sales for each group.
- Returns a 400 error if an invalid `group_by` value is provided.

**Query Parameters:**
- `start_date` (optional, date): Filter sales from this date.
- `end_date` (optional, date): Filter sales up to this date.
- `product_id` (optional, string): Filter by product.
- `category_id` (optional, string): Filter by category.
- `channel_id` (optional, string): Filter by sales channel.
- `group_by` (optional, string): One of `day`, `week`, `month`, `year` (default: `day`).

**Response Example:**
```json
{
  "message": "Revenue data",
  "data": [
    {
      "total_revenue": 1234.56,
      "total_sales": 42,
      "period": "2024-05-19"
    }
  ]
}
```

---

## GET `/sales/compare`

**Description:**  
Compare total revenue between two periods.

**Features:**
- Requires two periods, each defined by a start and end date.
- Optionally filter by `category_id`.
- Returns revenue for each period and the difference.

**Query Parameters:**
- `period1_start` (required, date): Start date of first period.
- `period1_end` (required, date): End date of first period.
- `period2_start` (required, date): Start date of second period.
- `period2_end` (required, date): End date of second period.
- `category_id` (optional, string): Filter by category.

**Response Example:**
```json
{
  "message": "Revenue comparison",
  "period1": {"start": "2024-05-01", "end": "2024-05-15", "revenue": 1000},
  "period2": {"start": "2024-05-16", "end": "2024-05-31", "revenue": 1200},
  "difference": 200
}
```

---

## GET `/sales/by-product`

**Description:**  
Get total revenue and sales count grouped by product.

**Features:**
- Allows filtering by `start_date`, `end_date`, and `category_id`.
- Returns a list of products with their total revenue and sales count.

**Query Parameters:**
- `start_date` (optional, date): Filter sales from this date.
- `end_date` (optional, date): Filter sales up to this date.
- `category_id` (optional, string): Filter by category.

**Response Example:**
```json
{
  "message": "Sales by product",
  "data": [
    {
      "product_id": "abc123",
      "total_revenue": 500.0,
      "total_sales": 10
    }
  ]
}
```

---

## GET `/sales/by-category`

**Description:**  
Get total revenue and sales count grouped by category.

**Features:**
- Allows filtering by `start_date` and `end_date`.
- Returns a list of categories with their total revenue and sales count.

**Query Parameters:**
- `start_date` (optional, date): Filter sales from this date.
- `end_date` (optional, date): Filter sales up to this date.

**Response Example:**
```json
{
  "message": "Sales by category",
  "data": [
    {
      "category_id": "cat001",
      "total_revenue": 2000.0,
      "total_sales": 25
    }
  ]
}
```

---

**General Notes:**
- All endpoints use dependency injection for database access.
- Aggregations are performed using SQL functions for efficiency.
- Error handling is robust, with clear messages for invalid input.
- The API is designed for flexible reporting and analytics on sales data.

                