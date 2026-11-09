## Summary

- Adds token validation to the login endpoint.
- Rejects expired and malformed tokens before the handler runs.
- Returns a consistent 401 error to API clients.

## Changes

- `src/auth/token.py`: validate the token signature and expiry.
- `src/auth/handlers.py`: return 401 for invalid tokens.
- `tests/auth/test_token.py`: cover expired, malformed, and valid tokens.

## Related issue

Closes #482

## How to test

1. Run `pytest tests/auth/test_token.py`.
2. Send a request with an expired token.
3. Expect a 401 response with the `invalid_token` error code.

## Risks and notes

- Existing sessions with tokens older than the new expiry window must re-authenticate.
- Reviewers should focus on the clock-skew handling in `src/auth/token.py`.

## Checklist

- [x] Tests added or updated
- [x] Lint and typecheck passed
- [x] Documentation updated when applicable
- [x] No secret or sensitive data included
