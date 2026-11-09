## What changed

- Add token validation to the login endpoint.
- Return a consistent 401 error for invalid tokens.

## Why

Expired tokens were accepted by the handler, which allowed stale sessions.

## Testing

1. Run `pytest tests/auth/test_token.py`.
2. Send an expired token and expect a 401 response.

## Checklist

- [x] Tests added or updated
- [x] Documentation updated
- [x] No secret or sensitive data included
