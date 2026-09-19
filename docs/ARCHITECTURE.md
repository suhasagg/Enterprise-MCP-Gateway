# Architecture

## Gateway responsibilities
1. Authenticate caller.
2. Establish tenant/principal context.
3. Authorize requested tool.
4. Validate policy.
5. Enforce rate limits.
6. Require approval for risky actions.
7. Route to the correct MCP server.
8. Audit decision and result.
9. Return a stable gateway contract.

## Why a gateway?
Direct agent-to-tool connections become difficult to govern as tool count and agent count grow. The gateway centralizes cross-cutting controls without embedding credentials or policy in prompts.

## Scale-out
The gateway is stateless apart from external PostgreSQL/Redis. Production routing should use service discovery and health-aware pools. Cache tool lists/schemas with versioned invalidation.

## Failure semantics
A timeout on a read can normally be retried. A timeout after a mutation is an ambiguous outcome: do not blindly retry. Use idempotency keys and reconcile the downstream state.

## Versioning
Expose stable enterprise names at the gateway and map them to backend versions. Tool schema changes require compatibility checks and canary rollout.
