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