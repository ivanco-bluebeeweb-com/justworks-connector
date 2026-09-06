# Justworks Connector — Auth & Credentials Standard (B1–B10)

## Security Standards Compliance
- **B1-B3 (Credential Types & Storage):** API Bearer Token stored in encrypted app secret store.
- **B7 (Multi-Region / Multi-Env):** Optional custom `base_url` for sandbox or Enterprise endpoints.
- **B8 (Secret Sanitization & Error Handling):** `_sanitize_msg` redacts tokens from error messages. HTTP 429 (`RATE_LIMITED` with `Retry-After`), 401 (`UNAUTHORIZED`), 403 (`FORBIDDEN`) classified explicitly.
- **B9 (Multi-Tenant Isolation):** Multiple connections isolated by unique UUID and `connection_id`.
