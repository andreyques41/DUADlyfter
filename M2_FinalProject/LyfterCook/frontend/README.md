# 🍳 LyfterCook Frontend

Vanilla JavaScript frontend for the LyfterCook platform.

## 📁 Structure

```
frontend/
├── index.html              # Landing page
├── pages/                  # HTML pages
│   ├── auth/               # Login, Register
│   └── dashboard/          # Protected dashboard pages
├── components/             # Reusable UI components (future)
├── scripts/
│   ├── core/               # App initialization, router, config
│   ├── services/           # API clients (auth, dishes, menus, etc.)
│   └── views/              # Page-specific logic
├── styles/                 # CSS files
│   ├── main.css            # Global styles
│   └── dashboard.css       # Dashboard-specific
└── utils/                  # Shared utilities (future)
```

## 🚀 Development

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## 🔗 API Integration

Backend: `http://localhost:5000`

Authentication uses JWT tokens stored in localStorage.

## 📋 Status

- ✅ Auth pages (login, register)
- ✅ Dashboard structure
- ⏳ Clients management
- ⏳ Dishes management
- ⏳ Menus management
- ⏳ Quotations management
- ⏳ Public pages

---

**Last Updated:** January 2, 2026
