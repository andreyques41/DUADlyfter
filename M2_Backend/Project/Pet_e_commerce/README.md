# Pet E-commerce Backend

## 📁 Project Structure

```text
Pet_e_commerce/
├── run.py                  # App entry point
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── blueprints.py       # Blueprint registration
│   ├── shared/             # Shared utilities, enums, DB, logging
│   ├── auth/               # Authentication domain
│   │   ├── models/         # User model
│   │   ├── schemas/        # User schema
│   │   ├── routes/         # Auth endpoints
│   │   └── services/       # Auth business logic
│   ├── products/           # Products domain
│   │   ├── models/         # Product model
│   │   ├── schemas/        # Product schema
│   │   ├── routes/         # Product endpoints
│   │   └── services/       # Product business logic
│   └── sales/              # Sales domain (carts, orders, bills, returns)
│       ├── models/         # Cart, Order, Bill, Return models
│       ├── schemas/        # Cart, Order, Bill, Return schemas
│       ├── routes/         # Sales endpoints
│       └── services/       # Sales business logic
├── config/                 # App config, logging, requirements
├── docs/                   # API usage/reference docs
│   └── USAGE_API_REFERENCE.md
├── tests/                  # Test suite
└── ...
```

---

## 📖 API Usage

For detailed API endpoints, authentication, and usage examples, see:

**[docs/USAGE_API_REFERENCE.md](docs/USAGE_API_REFERENCE.md)**

---

## 🚀 Quick Start

1. Clone the repo and `cd` into the project folder.
2. Create and activate a Python virtual environment.
3. Install dependencies:
   ```sh
   pip install -r config/requirements.txt
   ```
4. Run the app:
   ```sh
   python run.py
   ```
5. Access the API at [http://localhost:8000](http://localhost:8000)

---

## 🛠️ Features

- Modular, scalable Flask backend for e-commerce
- JWT authentication and role-based access
- Public product browsing, admin product management
- Shopping cart, order, billing, and returns workflows
- JSON file-based persistence (easy to swap for DB)
- Centralized logging and error handling
- Comprehensive API documentation
