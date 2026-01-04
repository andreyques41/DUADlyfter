# Copilot Instructions for LyfterCook

## Project Overview

LyfterCook is a recipe and meal planning application that helps users discover, save, and organize recipes while managing their meal planning and shopping lists.

## Development Guidelines

### Code Style & Standards

- Follow language-specific best practices (PEP 8 for Python, ESLint for JavaScript/TypeScript)
- Use descriptive variable and function names
- Write clear, concise comments for complex logic
- Keep functions small and focused on a single responsibility
- Use type hints/annotations where applicable

### Architecture Principles

- **Separation of Concerns**: Organize code into logical layers (routes, controllers, services, repositories)
- **DRY Principle**: Avoid code duplication by creating reusable components
- **Repository Pattern**: Abstract data access logic from business logic
- **Dependency Injection**: Pass dependencies rather than hardcoding them
- **Error Handling**: Implement comprehensive error handling with meaningful messages

### Testing Requirements

- Write unit tests for services and business logic
- Write integration tests for API endpoints
- Maintain minimum 75% code coverage
- All tests must pass before merging
- Use descriptive test names that explain what is being tested

### Documentation

- Keep README.md up to date with setup instructions
- Document all API endpoints with request/response examples
- Create decision documents (ADRs) for significant architectural choices
- Document environment variables and configuration options
- Maintain a clear project overview document

### Security Best Practices

- Never commit secrets or credentials to the repository
- Use environment variables for sensitive configuration
- Implement proper authentication and authorization
- Validate and sanitize all user inputs
- Use parameterized queries to prevent SQL injection
- Hash passwords using strong algorithms (e.g., bcrypt)

### Git Workflow

- Write descriptive commit messages
- Keep commits focused and atomic
- Reference issue numbers in commits when applicable
- Create feature branches for new work
- Ensure all tests pass before pushing

### Code Review Focus Areas

- Security vulnerabilities
- Performance implications
- Test coverage
- Code clarity and maintainability
- Adherence to project conventions

## Project-Specific Conventions

### API Design

- Use RESTful conventions for API endpoints
- Return appropriate HTTP status codes
- Include proper error messages in responses
- Version APIs when making breaking changes

### Database

- Use migrations for schema changes
- Include proper indexes for query optimization
- Follow naming conventions for tables and columns
- Document complex queries or stored procedures

### Naming Conventions

- **Files**: Use lowercase with underscores (e.g., `user_service.py`)
- **Classes**: Use PascalCase (e.g., `UserService`)
- **Functions/Methods**: Use snake_case (e.g., `get_user_by_id`)
- **Constants**: Use UPPERCASE with underscores (e.g., `MAX_RETRY_COUNT`)

## Common Tasks

### Adding a New Feature

1. Create models/schemas
2. Implement repository for data access
3. Create service with business logic
4. Add controller for HTTP handling
5. Register routes
6. Write comprehensive tests
7. Update documentation

### Fixing Bugs

1. Write a test that reproduces the bug
2. Fix the issue
3. Verify the test passes
4. Check for similar issues in the codebase
5. Update documentation if needed

### Refactoring

1. Ensure comprehensive test coverage exists
2. Make small, incremental changes
3. Run tests after each change
4. Update documentation to reflect changes
5. Review for performance impact

## Resources

- [Project Documentation](../docs/)
- [API Documentation](../docs/API_ROUTES.md)
- [Architecture Overview](../docs/ARCHITECTURE_OVERVIEW.md)
- [Testing Guide](../docs/TESTING.md)
