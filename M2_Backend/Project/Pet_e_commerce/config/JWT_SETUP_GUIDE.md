# JWT Security Configuration Setup

## Environment Variables

To ensure secure JWT token management, set the following environment variable:

### For Development

```bash
# Windows Command Prompt
set JWT_SECRET_KEY=your-very-secure-secret-key-here

# Windows PowerShell
$env:JWT_SECRET_KEY="your-very-secure-secret-key-here"

# Linux/Mac
export JWT_SECRET_KEY="your-very-secure-secret-key-here"
```

### For Production

Make sure to set a strong, randomly generated secret key:

```bash
# Example of a strong secret key (generate your own!)
JWT_SECRET_KEY="your-production-super-secure-random-256-bit-key-here"
```

## Security Notes

1. **Never commit secret keys to version control**
2. Use a different secret key for each environment (dev, staging, production)
3. Generate cryptographically secure random keys for production
4. Rotate keys periodically for enhanced security
5. Store production keys securely (e.g., AWS Secrets Manager, Azure Key Vault)

## Key Generation Example

You can generate a secure key using Python:

```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={secret_key}")
```

## Configuration

The JWT configuration is centrally managed in `app/config/security_config.py`:

- **Secret Key**: Retrieved from `JWT_SECRET_KEY` environment variable
- **Algorithm**: HS256 (HMAC SHA-256)
- **Token Expiration**: 24 hours (configurable)

## Usage

Both `auth_decorators.py` and `auth_service.py` now import and use the centralized configuration, ensuring consistency across the application.
