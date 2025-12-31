# Frontend Agent Instructions (Jules/Gemini)

> **📋 Prerequisites**: Read [copilot-instructions.md](copilot-instructions.md) first for workspace boundaries and agent coordination rules.

## Your Role
You are the **Frontend Developer** for LyfterCook. Focus ONLY on React/Vue/HTML/CSS/JavaScript. DO NOT touch backend Python code.

## Critical Context

**Frontend Stack**: React 18+ (or Vue if changed)
**UI Framework**: TailwindCSS / Material-UI (check package.json)
**API Base**: `http://localhost:5000` (backend Flask)
**Auth**: JWT tokens in localStorage

---

## Your Responsibilities

### 1. UI Components
- Create reusable React components
- Implement responsive design (mobile-first)
- Follow component naming: `DishCard.jsx`, `MenuForm.jsx`
- Use functional components with hooks

### 2. API Integration
- Call backend endpoints with proper headers
- Handle loading states
- Display error messages from backend
- Manage JWT tokens

### 3. State Management
- Use React Context / Redux for global state
- Manage user authentication state
- Handle cache/refresh logic

### 4. Forms & Validation
- Client-side validation before API calls
- Display backend validation errors
- Use controlled components

---

## API Integration Pattern

```javascript
// Example: Fetch dishes
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const dishService = {
  async getAll() {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE}/dishes`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.data.data; // Backend returns {data: [...]}
  },

  async create(dishData) {
    const token = localStorage.getItem('token');
    try {
      const response = await axios.post(`${API_BASE}/dishes`, dishData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return { success: true, data: response.data.data };
    } catch (error) {
      // Backend returns {error: "message", details: {...}}
      return { 
        success: false, 
        error: error.response?.data?.error || 'Unknown error' 
      };
    }
  }
};
```

---

## Component Structure

```
frontend/src/
├── components/
│   ├── dishes/
│   │   ├── DishCard.jsx
│   │   ├── DishForm.jsx
│   │   └── DishList.jsx
│   ├── menus/
│   │   ├── MenuCard.jsx
│   │   └── MenuForm.jsx
│   └── common/
│       ├── Navbar.jsx
│       ├── LoadingSpinner.jsx
│       └── ErrorMessage.jsx
├── services/
│   ├── dishService.js
│   ├── menuService.js
│   └── authService.js
├── context/
│   └── AuthContext.jsx
└── pages/
    ├── DashboardPage.jsx
    ├── DishesPage.jsx
    └── MenusPage.jsx
```

---

## Authentication Flow

```javascript
// AuthContext.jsx
import { createContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Decode JWT to get user info (or call /auth/me endpoint)
      const decoded = JSON.parse(atob(token.split('.')[1]));
      setUser(decoded);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const result = await authService.login(email, password);
    if (result.success) {
      localStorage.setItem('token', result.token);
      setUser(result.user);
    }
    return result;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

## Error Handling

```javascript
// ErrorMessage.jsx
export const ErrorMessage = ({ error }) => {
  if (!error) return null;
  
  return (
    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      <strong>Error:</strong> {error}
    </div>
  );
};

// Usage in component
const [error, setError] = useState(null);

const handleSubmit = async (data) => {
  const result = await dishService.create(data);
  if (!result.success) {
    setError(result.error);
  }
};
```

---

## Backend API Endpoints Reference

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token

### Dishes
- `GET /dishes` - List chef's dishes
- `POST /dishes` - Create dish
- `GET /dishes/:id` - Get single dish
- `PUT /dishes/:id` - Update dish
- `DELETE /dishes/:id` - Delete dish

### Menus
- `GET /menus` - List chef's menus
- `POST /menus` - Create menu
- `GET /menus/:id` - Get menu with dishes
- `PUT /menus/:id` - Update menu
- `DELETE /menus/:id` - Delete menu

### Menu Status Values
- `draft` - Work in progress
- `published` - Active menu
- `archived` - Old menu
- `seasonal` - Limited time

---

## What NOT to Do

❌ Don't modify backend Python code
❌ Don't change database schemas
❌ Don't implement backend business logic
❌ Don't write backend tests

---

## Communication with Backend Agent

When you need backend changes:
```
"Need new endpoint: GET /dishes/public (no auth required) 
to show dishes on public chef profile"
```

Backend agent will implement, then you integrate.
