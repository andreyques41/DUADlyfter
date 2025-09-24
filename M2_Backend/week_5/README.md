# Car Rental System - Week 5

A comprehensive PostgreSQL-based car rental management system with multiple exercise modules and REST API functionality.

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- PostgreSQL database
- Required Python packages (install with `pip install -r requirements.txt`)

### Database Setup
Ensure PostgreSQL is running with:
- Database: `postgres`
- User: `postgres` 
- Password: `postgres`
- Host: `localhost`
- Port: `5432`

## 📋 Main Runner (run.py)

The main entry point provides an interactive menu to execute different exercises:

```bash
python run.py
```

### Available Options:

| Option | Description | Module |
|--------|-------------|---------|
| **0** | Exit | - |
| **1** | Create Tables | `exercise1` |
| **2** | Run Queries | `exercise2` |
| **3** | Run API Server | `exercise3` |
| **4** | Database Backup | `exercise_extra1` |
| **5** | Database Health Check | `exercise_extra2` |
| **6** | Data Seeding with Faker | `exercise_extra3` |

### Usage Example:
```
Available exercises:
0 - Exit
1 - Create Tables (exercise1)
2 - Run Queries (exercise2)
3 - Run API Server (exercise3)
4 - Database Backup (exercise_extra1)
5 - Database Health Check (exercise_extra2)
6 - Data Seeding with Faker (exercise_extra3)

Which exercise? (0-6): 5
[INFO] Starting database health check...
[SUCCESS] Database operational normally. Available cars: 15
```

## 🌐 REST API (Option 3)

### Starting the API Server
```bash
python run.py
# Select option 3
```
Server will start on: `http://localhost:8000`

### API Endpoints

#### 👥 Users API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | Get all users |
| GET | `/users/1` | Get user by ID |
| POST | `/users/` | Create new user |
| PUT | `/users/1` | Update user |
| DELETE | `/users/1` | Delete user |

#### 🚗 Cars API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cars/` | Get all cars |
| GET | `/cars/1` | Get car by ID |
| POST | `/cars/` | Create new car |
| PUT | `/cars/1` | Update car |
| DELETE | `/cars/1` | Delete car |

#### 🏢 Rentals API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rentals/` | Get all rentals |
| GET | `/rentals/1` | Get rental by ID |
| POST | `/rentals/` | Create new rental |
| PUT | `/rentals/1` | Update rental |
| DELETE | `/rentals/1` | Delete rental |

### 📮 Postman Examples

**Base URL:** `http://localhost:8000`

#### Create User (POST /users/)
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "username": "johndoe",
  "password": "secure123",
  "birthday": "1990-05-15",
  "account_status_id": 1
}
```

#### Create Car (POST /cars/)
```json
{
  "model_id": 1,
  "year": 2023,
  "state_id": 1
}
```

#### Create Rental (POST /rentals/)
```json
{
  "user_id": 1,
  "car_id": 1
}
```

#### Update User (PUT /users/1)
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "username": "janedoe",
  "password": "newpassword123",
  "birthday": "1985-03-22",
  "account_status_id": 2
}
```

### 🎯 Industry Standard Foreign Key Handling

**IMPORTANT: This API follows industry standards for handling foreign key relationships:**

#### 1. API Workflow
1. **Frontend loads reference data** from separate queries if needed
2. **Display friendly names** to users in dropdowns  
3. **Send IDs** in POST/PUT requests (not names)

#### 2. Updated API Response Examples

**Get All Users Response (includes both ID and name):**
```json
{
  "users": [
    {
      "id": 1,
      "full_name": "John Doe", 
      "email": "john@example.com",
      "username": "johndoe",
      "birthday": "1990-05-15",
      "account_status_id": 1,
      "account_status_name": "Active"
    }
  ]
}
```

**Get All Cars Response (includes both ID and name):**
```json
{
  "cars": [
    {
      "id": 1,
      "year": 2023,
      "model_id": 5,
      "state_id": 1, 
      "brand": "Toyota",
      "model_name": "Corolla",
      "state_name": "Available"
    }
  ]
}
```

#### 3. Correct PUT Request Example
```json
PUT /cars/1
{
  "model_id": 2,     // ✅ Send ID, not name
  "year": 2024       // Only fields to update
}
```

## 🔧 Additional Features

### Database Backup (Option 4)
- Creates timestamped CSV backups of all tables
- Includes column headers for easy data analysis
- Saves to `db_backups/` folder

### Health Check (Option 5)
- Tests database connectivity
- Verifies required tables exist
- Counts available cars
- Returns system status

### Data Seeding (Option 6)
- Generates 200 fake users using Faker library
- Creates 100 cars with random models/years
- Generates 50-150 random rental records

## 📁 Project Structure

```
week_5/
├── run.py                 # Main runner script
├── requirements.txt       # Python dependencies
├── exercise1/            # Table creation
├── exercise2/            # Query operations
├── exercise3/            # REST API
├── exercise_extra1/      # Database backup
├── exercise_extra2/      # Health check
├── exercise_extra3/      # Data seeding
├── utilities/            # Database utilities
└── db_backups/          # CSV backup files
```

## 🛠️ Development

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Database Schema
The system uses the `lyfter_car_rental` schema with tables:
- `users` - User accounts and profiles
- `cars` - Vehicle inventory
- `rentals` - Rental transactions
- `model` - Car models and brands
- `account_status` - User account states
- `car_state` - Vehicle availability states
- `rent_state` - Rental transaction states

