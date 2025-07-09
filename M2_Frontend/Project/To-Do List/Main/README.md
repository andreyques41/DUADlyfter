# To-Do List Application

A modular task management application with clean architecture and modern JavaScript practices.

## 📁 Project Structure

```
Main/
├── main.html                   # Application entry point
├── styles/                     # CSS styling
│   ├── main.css               # Core application styles
│   ├── components.css         # UI component styles
│   └── tasks.css              # Task-specific styles
└── scripts/                    # JavaScript modules
    ├── core/                   # Application foundation
    ├── services/               # External integrations
    ├── storage/                # Data persistence
    ├── models/                 # Data structures
    ├── business-logic/         # Application logic
    └── ui/                     # User interface
        ├── components/         # Reusable UI elements
        └── views/              # Page-level UI
```

## 🗂️ Folder Responsibilities

| Folder                | Purpose            | Contains                                      |
| --------------------- | ------------------ | --------------------------------------------- |
| **`core/`**           | App infrastructure | Configuration, utilities, session management  |
| **`services/`**       | External APIs      | API synchronization, third-party integrations |
| **`storage/`**        | Data persistence   | Local storage operations, data validation     |
| **`models/`**         | Data structures    | Category management, domain models            |
| **`business-logic/`** | App logic          | Task operations, filtering, state management  |
| **`ui/components/`**  | UI elements        | Reusable components, event handlers           |
| **`ui/views/`**       | View controllers   | Complex UI modules, form handling             |

## 📄 File Overview

### Core Files

- **`app.js`** - Application initialization and bootstrap
- **`config.js`** - Global configuration and utility functions
- **`user-session.js`** - User authentication and session management

### Services & Storage

- **`api-sync.js`** - API synchronization and conflict resolution
- **`local-storage.js`** - Local storage CRUD operations

### Data Models

- **`category-dropdown.js`** - Category dropdown population and sync
- **`category-operations.js`** - Category CRUD operations and validation

### Business Logic

- **`task-completion.js`** - Task completion state and section movement
- **`task-manager.js`** - Core task business logic and operations
- **`category-filter.js`** - Category filtering and view management

### UI Components

- **`category-ui.js`** - Category visual components and colors
- **`category-events.js`** - Category interaction event handlers
- **`task-elements.js`** - Task UI element factory and creation

### UI Views

- **`task-render.js`** - Task list rendering and display logic
- **`task-forms.js`** - Task form handling (add/edit sidebars)
- **`navigation-sidebar.js`** - Main navigation and sidebar controls

## 🚀 Key Features

- **Modular Architecture** - Clean separation of concerns
- **Task Management** - Create, edit, complete, and delete tasks
- **Category System** - Color-coded task categorization
- **Date Organization** - Today, tomorrow, this week sections
- **Data Persistence** - Local storage with API sync capability
- **Responsive UI** - Modern, accessible interface

## 🛠️ Development Notes

- **Loading Order**: Core → Services → Models → Business Logic → UI → App
- **Dependencies**: Uses Axios for HTTP requests
- **Standards**: JSDoc documentation, consistent naming conventions
- **Architecture**: Follows MVC patterns with clear layer separation

## 📱 Usage

Open `main.html` in a web browser. The application will automatically:

1. Initialize core services and storage
2. Load user session and data
3. Render the task interface
4. Set up event listeners and interactions

All task data persists locally and can sync with external APIs when configured.
