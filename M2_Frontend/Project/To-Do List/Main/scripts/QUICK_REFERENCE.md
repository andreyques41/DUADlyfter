# 🚀 JavaScript Organization - Quick Reference

## 📁 Folder Structure

```
scripts/
├── core/           # Core application logic
├── data/           # Data management and storage
├── features/       # Business logic and features
└── ui/             # User interface components
```

## 📂 File Locations

### 🔧 Core (`core/`)

- **config.js** - App configuration, constants, utilities
- **app.js** - Main application controller and initialization

### 💾 Data (`data/`)

- **storage-core.js** - localStorage operations
- **storage-sync.js** - API synchronization
- **categories.js** - Category management

### 📋 Features (`features/`)

- **task-manager.js** - Task business logic
- **user-session.js** - User authentication and session

### 🎨 UI (`ui/`)

- **render.js** - DOM rendering
- **task-sidebar.js** - Task sidebar interface
- **sidebar-ui.js** - Main sidebar interface

## 🎯 Quick Navigation

### Adding a new feature?

→ Put business logic in `features/`
→ Put UI components in `ui/`
→ Put data handling in `data/`

### Looking for configuration?

→ Check `core/config.js`

### Need to modify storage?

→ Check `data/storage-core.js` for localStorage
→ Check `data/storage-sync.js` for API sync

### Working on UI?

→ Check `ui/` folder for all interface components

## 🔄 Loading Order

1. **Core** (config, user-session)
2. **Data** (storage, categories)
3. **Features** (task-manager)
4. **UI** (render, sidebars)
5. **App** (initialization)
