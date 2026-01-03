# 🍳 LyfterCook Frontend

Vanilla JavaScript frontend for the LyfterCook platform.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (or use `pnpm` with any Node version)
- pnpm (recommended) or npm

### Setup Commands

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview
```

Development server runs at: `http://localhost:5173`  
Backend API: `http://localhost:5000`

---

## 📚 Full Documentation

For complete documentation, see [`docs/frontend/`](../docs/frontend/):

- **[Frontend Plan](../docs/frontend/FRONTEND_PLAN.md)** - Development roadmap & milestones
- **[Tools & Resources](../docs/frontend/TOOLS_AND_RESOURCES.md)** - Design tools, assets, icon libraries
- **[Vite Guide](../docs/frontend/VITE_GUIDE.md)** - Vite configuration & deployment

---

## 📁 Project Structure

```
frontend/
├── index.html              # Entry point
├── pages/                  # HTML pages
│   ├── auth/               # Login, Register
│   └── dashboard/          # Protected dashboard
├── scripts/
│   ├── core/               # App initialization, router, config
│   ├── services/           # API clients (auth, dishes, menus, etc.)
│   └── views/              # Page-specific logic
├── styles/                 # CSS files
│   ├── main.css            # Global styles
│   └── dashboard.css       # Dashboard styles
└── components/             # Reusable components (future)
```

---

## 📊 Status

- ✅ Auth pages (login, register)
- ✅ Dashboard structure
- ✅ Routing system
- 🔄 Clients management (in progress)
- ⏳ Dishes management
- ⏳ Menus management
- ⏳ Quotations management
- ⏳ Public pages

---

## 🔗 API Integration

- Backend base URL configured in `scripts/core/config.js`
- JWT authentication via localStorage
- Axios for HTTP requests
- Auto-redirect on 401 Unauthorized

---

**Tech Stack:** Vanilla JS (ES6 Modules) | Vite 5 | Axios | CSS3  
**Last Updated:** January 3, 2026
