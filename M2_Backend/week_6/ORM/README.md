# DUAD Backend Week 6 - Database Exercises

## Overview
This project contains several exercises for database management using SQLAlchemy and PostgreSQL. The main entry point is `run.py`, which provides a menu to execute different exercises, including table creation, data insertion, queries, and data seeding with Faker.

## How to Run
1. **Install Requirements**
   - Make sure you have Python 3.10+ installed.
   - Install the required packages:
     ```sh
     pip install sqlalchemy psycopg2 faker
     ```
2. **Set Up PostgreSQL**
   - Ensure you have a PostgreSQL server running and a database named `lyfter` created.
   - Update the database connection URI in the code if your credentials differ (default: `postgres:postgres@localhost:5432/lyfter`).

3. **Run the Main Script**
   - In your terminal, activate your virtual environment if needed, then run:
     ```sh
     python run.py
     ```
   - Follow the on-screen menu to select and run an exercise.

## Requirements
- Python 3.10 or higher
- Packages:
  - `sqlalchemy`
  - `psycopg2` (PostgreSQL driver)
  - `faker` (for data seeding)
- PostgreSQL server with a database named `lyfter`

## Notes
- Some exercises will create or modify tables and insert sample data.
- Data seeding uses the Faker library to generate realistic test data.
- Make sure your PostgreSQL server is running before executing the scripts.

---
For any issues, check your database connection settings and package installation.
