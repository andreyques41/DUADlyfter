# Architectural Decision Record: Public vs Protected Endpoints Separation

**Date:** December 28, 2025  
**Status:** Accepted  
**Deciders:** Development Team

## Context

The Chef module had duplicate functionality:
- `GET /chefs` and `GET /chefs/:id` (basic, no cache)
- `GET /public/chefs` and `GET /public/chefs/:id` (advanced, cached, filtered)

Both served the same purpose: browsing chef profiles. This created confusion about which endpoint to use.

## Decision

**Deprecate the basic `/chefs` and `/chefs/:id` public browsing endpoints.**

Consolidate all public chef browsing to `/public/chefs` endpoints.

## Rationale

1. **Performance**: Public endpoints use Redis cache (5-10min TTL), reducing database load
2. **Semantic Clarity**: 
   - `/chefs/profile` = Authenticated chef managing own profile (protected)
   - `/public/chefs` = Anyone browsing chef listings (public, cached, filtered)
3. **Maintainability**: One way to do each thing eliminates confusion
4. **Scalability**: Caching layer essential for public-facing features

## Consequences

### Positive
- Reduced total endpoints from 62 to 60
- Chef module now has 3 focused endpoints (profile management only)
- All public browsing consolidated under `/public/*` namespace
- Improved cache hit rate and clearer API structure

### Negative
- Any existing consumers using `/chefs` endpoints need to migrate to `/public/chefs`
- Breaking change for API consumers (if any exist)

## Implementation

- Removed `GET /chefs` and `GET /chefs/:id` routes from `chef_routes.py`
- Updated all tests to use `/public/chefs` endpoints
- Updated API documentation to reflect new structure
