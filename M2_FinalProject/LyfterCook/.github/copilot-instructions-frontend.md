# Frontend Agent Instructions (Jules/Gemini)

> **📋 Prerequisites**: Read [copilot-instructions.md](copilot-instructions.md) first for workspace boundaries and agent coordination rules.

## Your Role
You are the **Frontend Developer** for LyfterCook. Focus ONLY on HTML/CSS/JavaScript. DO NOT touch backend Python code.

## Critical Context

**Frontend Stack**: Vanilla JavaScript (ES6 Modules)
**Build Tool**: Vite (for dev server and bundling)
**UI Framework**: TailwindCSS + Custom CSS
**API Base**: `http://localhost:5000` (backend Flask)
**Auth**: JWT tokens in localStorage

---

## Your Responsibilities

### 1. UI Components
- Create reusable JavaScript classes/functions
- Implement responsive design (mobile-first)
- Follow naming conventions: `DishCard.js`, `MenuForm.js`
- Use ES6 modules for code organization

### 2. API Integration
- Call backend endpoints with Fetch API or Axios
- Handle loading states with DOM manipulation
- Display error messages from backend
- Manage JWT tokens in localStorage

### 3. State Management
- Use JavaScript classes for app state
- Manage user authentication state in memory + localStorage
- Handle cache/refresh logic with custom state manager

### 4. Forms & Validation
- Client-side validation before API calls
- Display backend validation errors dynamically
- Use native form validation API + custom validators

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

## Project Structure

```
frontend/
├── index.html                      # Landing page
├── pages/
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── dashboard/
│       ├── clients.html
│       ├── dishes.html
│       ├── menus.html
│       ├── quotations.html
│       └── appointments.html
├── scripts/
│   ├── core/
│   │   ├── app.js                  # App initialization
│   │   ├── router.js               # Client-side routing
│   │   ├── config.js               # API config
│   │   └── state.js                # Global state manager
│   ├── services/
│   │   ├── apiClient.js            # Axios wrapper
│   │   ├── authService.js
│   │   ├── dishService.js
│   │   ├── menuService.js
│   │   └── clientService.js
│   ├── components/
│   │   ├── DishCard.js             # Reusable dish card
│   │   ├── MenuForm.js             # Menu creation form
│   │   ├── Modal.js   (Vanilla JS)

```javascript
// scripts/core/state.js
export class AppState {
  constructor() {
    this.user = null;
    this.token = localStorage.getItem('token');
    this.listeners = [];
    
    if (this.token) {
      this.loadUserFromToken();
    }
  }

  loadUserFromToken() {
    try {
      const payload = this.token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      this.user = {
        id: decoded.sub,
        email: decoded.email,
        role: decoded.role
      };
    } catch (error) {
      this.logout();
    }
  }

  setUser(user, token) {
    this.user = user;
    this.token = token;
    localStorage.setItem('token', token);
    this.notify();
  }

  logout() {
    this.user = null;
    this.token = null;
    localStorage.removeItem('token');
    window.location.href = '/pages/auth/login.html';
  }

  isAuthenticated() {
    return !!this.token;
  }

  subscribe(callback) {
    this.listeners.push(callback);
  }

  notify() {
    this.listeners.forEach(cb => cb(this.user));
  }
}

export const appState = new AppState();

// scripts/services/authService.js
import { API_BASE } from '../core/config.js';
import { appState } from '../core/state.js';

export const authService = {
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
   scripts/components/ErrorMessage.js
export function showError(message, container) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.innerHTML = `
    <strong>Error:</strong> ${message}
    <button class="close-btn" onclick="this.parentElement.remove()">×</button>
  `;
  container.prepend(errorDiv);

  // Auto-remove after 5 seconds
  setTimeout(() => errorDiv.remove(), 5000);
}

export function clearErrors(container) {
  container.querySelectorAll('.error-message').forEach(el => el.remove());
}

// Usage in page
import { showError, clearErrors } from '../components/ErrorMessage.js';

const handleSubmit = async (formData) => {
  const container = document.getElementById('form-container');
  clearErrors(container);

  const result = await dishService.create(formData);
  if (!result.success) {
    showError(result.error, container);
  }
};
```

**CSS for Error Messages** (styles/components.css):
```css
.error-message {
  background-color: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-message .close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #c33;
}
  logout() {
    appState.logout();
  }nst login = async (email, password) => {
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
