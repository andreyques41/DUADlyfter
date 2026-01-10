# Finance Tracker Desktop

> Python GUI application for personal finance management

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FreeSimpleGUI](https://img.shields.io/badge/FreeSimpleGUI-Desktop-green.svg)](https://github.com/PySimpleGUI/FreeSimpleGUI)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

A **desktop application** for tracking personal income and expenses, built with Python and a modern GUI framework. Demonstrates object-oriented design, data persistence, and input validation patterns.

### Problem Statement

Personal finance management requires:
- Easy categorization of income and expenses
- Persistent storage across sessions
- Clear visualization of financial movements
- Data validation to prevent entry errors

### Solution

A desktop application with:
- **OOP design** using `Movement` and `FinanceMonth` classes
- **CSV persistence** for data portability and backup
- **GUI interface** for intuitive interaction
- **Input validation** with meaningful error messages

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 main_gui.py                           │   │
│  │         (FreeSimpleGUI window management)             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 gui_helpers.py                        │   │
│  │            (UI utilities, popups)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LAYER                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               finance_movements.py                    │   │
│  │         Movement + FinanceMonth classes               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  utilities.py                         │   │
│  │         Validation and helper functions               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                csv_handler.py                         │   │
│  │           CSV import/export operations                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Key Classes

```python
class Movement:
    """Single financial transaction (income or expense)"""
    - name: str          # Transaction description
    - category: str      # Category (Food, Transport, Salary, etc.)
    - movement_type: str # 'Income' or 'Expense'
    - amount: float      # Positive value

class FinanceMonth:
    """Collection of movements for a specific month"""
    - month: str
    - year: int
    - movements: List[Movement]
    
    + add_movement(movement)
    + remove_movement(movement)
    + convert_to_list_of_dict()  # For CSV export
    + add_movements_from_list()   # From CSV import
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| **OOP structure** | Encapsulates validation logic within domain objects |
| **CSV storage** | Human-readable, portable, no external DB required |
| **Type validation** | Prevents invalid data at entry point |
| **Separation of concerns** | GUI, business logic, and data handling in separate modules |

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.8+ |
| **GUI** | FreeSimpleGUI |
| **Data Storage** | CSV files |
| **Testing** | pytest |

---

## 📦 Project Structure

```
week_17/
├── finance_tracker.py      # Application entry point
├── Clases/
│   └── finance_movements.py  # Movement, FinanceMonth classes
├── Gui/
│   ├── main_gui.py          # Main window and event loop
│   └── gui_helpers.py       # UI utility functions
├── DataHandler/
│   └── csv_handler.py       # CSV import/export
├── Utilities/
│   └── utilities.py         # Validation helpers
├── Tests/
│   └── test_finance_movements.py  # Unit tests
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Navigate to project
cd M1/week_17

# Install dependencies
pip install FreeSimpleGUI

# Run application
python finance_tracker.py
```

### Usage

1. **Launch** the application
2. **Add movements** using "Add Income" or "Add Expense" buttons
3. **Categorize** each entry (Food, Transport, Entertainment, etc.)
4. **View summary** in the main data table
5. **Data auto-saves** to `finance_data.csv` on changes

---

## 🧪 Testing

```bash
# Run unit tests
pytest Tests/test_finance_movements.py -v
```

### Test Coverage
- Movement validation (type, amount constraints)
- FinanceMonth operations (add, remove, convert)
- CSV round-trip (export then import)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Add Income** | Record positive cash flow with category |
| **Add Expense** | Record spending with category |
| **Category Management** | Create custom categories |
| **Data Table** | View all movements with filtering |
| **Auto-Save** | Persist data on every change |
| **Auto-Load** | Restore previous session on startup |
| **Validation** | Prevent invalid amounts and types |

---

## 📊 Project Status

| Component | Status |
|-----------|--------|
| Core classes | ✅ Complete |
| CSV persistence | ✅ Complete |
| GUI implementation | ✅ Complete |
| Input validation | ✅ Complete |
| Unit tests | ✅ Complete |
| Monthly summaries | ⏳ Planned |
| Charts/graphs | ⏳ Planned |

---

## 🎯 What This Demonstrates

### Engineering Skills
- **OOP Design**: Domain-driven modeling with `Movement` and `FinanceMonth`
- **Validation Patterns**: Type constraints, amount validation, error handling
- **Separation of Concerns**: Clear layers between UI, logic, and data
- **Data Persistence**: CSV handling with proper encoding

### Python Proficiency
- Type hints for documentation
- Exception handling with informative messages
- List comprehensions for data transformation
- Class design with clear interfaces

---

## 📄 License

MIT License

---

*Developed as part of the Lifter Software Engineering Program (Costa Rica, 2024-2025)*
