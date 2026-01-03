# ADR 002: Monorepo Documentation Structure

**Status:** Accepted  
**Date:** January 3, 2026  
**Decision Makers:** Documentation Agent  
**Tags:** `documentation`, `structure`, `monorepo`, `organization`

---

## Context

The LyfterCook project initially had an inconsistent documentation structure:

### Problems Identified
1. **Structural Inconsistency**: `docs/frontend/` existed but no `docs/backend/`
2. **Empty Directory**: `backend/docs/` folder was empty and unused
3. **Scattered Organization**: Backend docs split across `docs/api/` and `docs/architecture/`
4. **Navigation Complexity**: Developers had to search multiple locations for related documentation
5. **Unclear Responsibility**: Unclear which folder should contain backend documentation

### Initial Structure
```
docs/
├── api/                    # Backend API docs
├── architecture/           # Backend architecture docs
├── frontend/               # Frontend docs
├── archive/
└── decisions/

backend/
└── docs/                   # Empty folder
```

### Options Considered

#### Option A: Consolidated Monorepo Structure (CHOSEN)
```
docs/
├── backend/                # All backend documentation
├── frontend/               # All frontend documentation
├── archive/
└── decisions/
```

**Pros:**
- Single source of truth
- Industry-standard pattern (React, Vue, Next.js, Turborepo)
- Clear separation of concerns
- Easier navigation
- Consistent with existing `docs/frontend/` structure

**Cons:**
- Requires one-time migration effort
- Need to update all cross-references

#### Option B: Distributed Structure
```
backend/
└── docs/                   # Backend documentation

frontend/
└── docs/                   # Frontend documentation

docs/
├── archive/
└── decisions/
```

**Pros:**
- Documentation lives near code
- Independent module documentation

**Cons:**
- Fragments documentation across 3 locations
- Harder to browse all docs in one place
- No clear place for shared documentation
- Inconsistent with current structure

---

## Decision

**We chose Option A: Consolidated Monorepo Structure**

### Implementation

1. **Created** `docs/backend/` directory
2. **Moved** all backend documentation to `docs/backend/`:
   - `docs/api/API_DOCUMENTATION.md` → `docs/backend/API_DOCUMENTATION.md`
   - `docs/architecture/PROJECT_PLAN.md` → `docs/backend/ARCHITECTURE.md`
   - `docs/architecture/CACHE_GUIDE.md` → `docs/backend/CACHE_GUIDE.md`
   - `docs/architecture/ADMIN_ENDPOINTS_DESIGN.md` → `docs/backend/ADMIN_DESIGN.md`
   - `backend/tests/TESTING_GUIDE.md` → `docs/backend/TESTING_GUIDE.md` (copied)
3. **Removed** empty directories: `docs/api/`, `docs/architecture/`, `backend/docs/`
4. **Updated** all cross-references in documentation files
5. **Simplified** `backend/README.md` and `frontend/README.md` to quick-start guides with links to full docs
6. **Updated** [docs/INDEX.md](../INDEX.md) as central navigation hub

### New Structure

```
docs/
├── backend/                        # Backend Documentation
│   ├── API_DOCUMENTATION.md        # 60 endpoints with examples
│   ├── ARCHITECTURE.md             # Tech stack, database schema
│   ├── TESTING_GUIDE.md            # 296 tests documentation
│   ├── CACHE_GUIDE.md              # Redis implementation
│   └── ADMIN_DESIGN.md             # Admin module architecture
│
├── frontend/                       # Frontend Documentation
│   ├── FRONTEND_PLAN.md            # Development roadmap
│   ├── TOOLS_AND_RESOURCES.md      # Design tools, assets
│   ├── VITE_GUIDE.md               # Build configuration
│   └── PAGE_SPECIFICATION_TEMPLATE.md
│
├── archive/                        # Historical documentation
│   ├── SCHEMA_MIGRATION_HISTORY.md
│   └── [7 completed phase documents]
│
├── decisions/                      # Architecture Decision Records
│   ├── 001_public_vs_protected_endpoints.md
│   └── 002_monorepo_documentation_structure.md (this file)
│
└── INDEX.md                        # Central navigation hub
```

---

## Rationale

### Why Consolidated Structure Wins

1. **Industry Standard**: Used by major projects (React, Vue.js, Next.js, Turborepo, Lerna)
2. **Single Source of Truth**: All documentation accessible from one location
3. **Better Navigation**: Developers can browse `docs/` to find everything
4. **Consistency**: Mirrors existing `docs/frontend/` structure
5. **Clearer Organization**: Backend vs Frontend vs Shared (decisions, archive)
6. **Scalability**: Easy to add new documentation types (e.g., `docs/devops/`, `docs/deployment/`)

### Real-World Examples

- **React**: `docs/` folder with `docs/content/reference/`, `docs/content/learn/`
- **Vue.js**: `docs/` folder with `docs/guide/`, `docs/api/`, `docs/examples/`
- **Next.js**: `docs/` folder with `docs/app/`, `docs/pages/`, `docs/api-reference/`
- **Turborepo**: `docs/` folder with `docs/core-concepts/`, `docs/handbook/`

---

## Consequences

### Positive
- ✅ Clear documentation hierarchy
- ✅ Easier onboarding for new developers
- ✅ Consistent with industry best practices
- ✅ Single navigation point ([docs/INDEX.md](../INDEX.md))
- ✅ Room for future expansion (e.g., `docs/devops/`)

### Neutral
- 🔄 One-time migration effort (completed)
- 🔄 Need to update all cross-references (completed)
- 🔄 Update copilot instructions (completed)

### Negative
- ⚠️ Documentation physically separated from code modules
  - **Mitigation**: README files in each module provide quick-start + links to full docs

---

## Verification

### Migration Checklist
- [x] Created `docs/backend/` directory
- [x] Moved 5 backend documentation files
- [x] Removed empty directories (`api/`, `architecture/`, `backend/docs/`)
- [x] Updated [docs/INDEX.md](../INDEX.md)
- [x] Updated [.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- [x] Updated cross-references in [docs/frontend/TOOLS_AND_RESOURCES.md](../frontend/TOOLS_AND_RESOURCES.md)
- [x] Simplified [backend/README.md](../../backend/README.md)
- [x] Simplified [frontend/README.md](../../frontend/README.md)
- [x] Verified no broken links with grep search
- [x] Created this ADR

### File Count
- **Before**: 16 documentation files scattered across 4 directories
- **After**: 18 documentation files organized in 4 logical groups
- **Total Files**: `docs/backend/` (5) + `docs/frontend/` (4) + `docs/archive/` (7) + `docs/decisions/` (2) + `docs/INDEX.md` (1)

---

## References

- **Related ADRs**: [001_public_vs_protected_endpoints.md](001_public_vs_protected_endpoints.md)
- **External Examples**:
  - [React Monorepo Structure](https://github.com/facebook/react/tree/main/docs)
  - [Vue.js Documentation](https://github.com/vuejs/docs)
  - [Next.js Documentation](https://github.com/vercel/next.js/tree/canary/docs)
  - [Turborepo Documentation](https://github.com/vercel/turbo/tree/main/docs)

---

**Last Updated:** January 3, 2026  
**Status:** Implementation complete and validated
