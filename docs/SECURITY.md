# Security model

The included static bearer tokens are ONLY a runnable local demo.

Production:
- OAuth 2.1 / OIDC / Entra ID
- validate issuer, signature, expiration and audience
- resource-specific tokens
- least-privilege scopes
- never put access tokens in URLs
- mTLS/service identity between gateway and downstream servers
- validate Origin on Streamable HTTP
- tool argument schema validation
- tenant-aware authorization at every layer
- DLP/PII redaction
- immutable audit storage
- secrets manager
- outbound egress allowlists
- prompt-injection defense
- human approval for irreversible/high-blast-radius tools

Approval should bind to exact principal, tenant, tool, normalized arguments, expiry and nonce. The simplified demo token is intentionally not production-grade.
