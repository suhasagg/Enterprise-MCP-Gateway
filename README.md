# Enterprise MCP Gateway — Python + Java

 a governed Model Context Protocol gateway between AI agents and enterprise tools.

## What this repository demonstrates

- MCP Streamable HTTP
- Python AI client using OpenAI Agents SDK
- Java 21 / Spring Boot / Spring AI MCP servers
- Gateway pattern for enterprise tools
- tenant isolation
- bearer-token authentication demo
- RBAC/scopes
- tool registry and routing
- tool allow/deny policy
- high-risk action approval
- rate limiting
- audit logging
- idempotency
- downstream tool abstraction
- PostgreSQL + Redis
- Prometheus metrics
- Docker Compose
- tests + security/evaluation harness

## Architecture

```text
OpenAI Agent / Enterprise Copilot
              |
              | MCP Streamable HTTP
              v
       Python MCP Gateway :8000
       +----------------------+
       | AuthN / tenant       |
       | AuthZ / scopes       |
       | Tool registry        |
       | Policy engine        |
       | Rate limiting        |
       | Approval enforcement |
       | Audit / metrics      |
       +----------+-----------+
                  |
       +----------+-----------+
       |                      |
       v                      v
Java CRM MCP :8081      Java Ops MCP :8082
       |                      |
 Customers/Tickets       Deployments/Restart
```

## Gateway tools

The gateway exposes a stable enterprise tool surface:

- `crm_get_customer`
- `crm_create_ticket`
- `ops_get_deployment`
- `ops_restart_service`

The AI never receives direct service credentials.

## Demo identity model

Bearer tokens in `.env.example` are intentionally simple local-development tokens:

- `demo-reader-token`: read-only
- `demo-operator-token`: read + write

Production should replace this with OAuth 2.1 / OIDC / Entra ID and audience-scoped access tokens.

## Run

```bash
cp .env.example .env
docker compose up --build
```

List/use gateway tools from the included agent client:

```bash
docker compose exec python-gateway \
  python -m app.agent_client "Look up customer CUST-1001"
```

Create a ticket:

```bash
docker compose exec python-gateway \
  env MCP_CLIENT_TOKEN=demo-operator-token \
  python -m app.agent_client "Create a high priority support ticket for CUST-1001 titled Payment failure"
```


The hard problem is not calling an MCP server. It is creating a scalable trust boundary for hundreds of agents and tools:
authentication, authorization, tenant isolation, tool discovery, schema governance, approvals, blast-radius control, auditability, versioning, failure handling and observability.

See `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, and `docs/INTERVIEW.md`.


---

# Engineering Guide

## 1. Executive Architecture View

**Purpose.** Centralizes authentication, tenant isolation, authorization, policy, approvals, routing, rate limits and audit between agents and MCP services.

The repository deliberately separates **probabilistic AI reasoning** from **deterministic enterprise controls**. Model outputs may propose plans, rank evidence, summarize observations or choose among permitted tools, but identity, tenancy, authorization, approval, idempotency, rate limits and destructive-action boundaries belong to ordinary software.

### Control Plane vs Data / Action Plane

| Plane | Responsibilities |
|---|---|
| AI / Control Plane | Request interpretation, planning, routing, model invocation, agent coordination, evaluation hooks |
| Context Plane | Retrieval, memory, telemetry, documents, evidence and provenance |
| Policy Plane | Tenant context, RBAC/scopes, risk classification, approval and quotas |
| Action Plane | Narrow Java APIs/MCP tools that perform enterprise operations |
| State Plane | PostgreSQL/pgvector and Redis where used |
| Observability Plane | Metrics, traces, audit events, health and evaluation evidence |

### Trust Boundaries

```text
Untrusted user/content
        |
        v
API validation / identity
        |
        v
AI reasoning boundary
        |
        v
Policy + tool schema boundary
        |
        v
MCP / Java action boundary
        |
        v
Enterprise systems / durable state
```

A production implementation should assume that user prompts, retrieved documents, tool outputs and model-generated arguments can all be hostile or malformed.

## 2. Repository Structure

```text
.env.example
.gitignore
Makefile
README.md
docker-compose.yml
docs/
  ARCHITECTURE.md
  INTERVIEW.md
  SECURITY.md
evals/
  security_eval.py
java-services/
  Dockerfile
  pom.xml
  src/
    main/
    test/
python-gateway/
  Dockerfile
  app/
    __init__.py
    agent_client.py
    audit.py
    config.py
    database.py
    downstream.py
    gateway.py
    models.py
    policy.py
    rate_limit.py
    security.py
  requirements.txt
  tests/
    test_policy.py
```

## 3. End-to-End Request Lifecycle

1. **Ingress** — validate request shape, establish tenant/principal context and attach a correlation id.
2. **Context assembly** — load only the memory, documents, telemetry or metadata required for the task.
3. **AI decision** — invoke the configured model/agent using structured contracts where possible.
4. **Policy decision** — independently check tool/model entitlement, risk, tenant and approval requirements.
5. **Execution** — invoke a narrow downstream API or MCP tool with bounded timeout/retry behavior.
6. **Verification** — validate tool result, citations, tests, health signals or other task-specific evidence.
7. **Persistence** — store durable domain state and minimal audit/evaluation evidence.
8. **Response** — return a stable API contract without leaking provider credentials or internal secrets.

## 4. API Surface

| Method | Endpoint | Service |
|---|---|---|
| — | — | MCP/tool-driven surface; inspect tool classes |

MCP tools form a separate typed API surface. The Java tool classes and Python MCP client/runtime are the authoritative definitions for those schemas.

## 5. Configuration

```bash
cp .env.example .env
```

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Runtime configuration |
| `OPENAI_MODEL` | Runtime configuration |
| `DATABASE_URL` | Runtime configuration |
| `REDIS_URL` | Runtime configuration |
| `CRM_MCP_URL` | Runtime configuration |
| `OPS_MCP_URL` | Runtime configuration |
| `MCP_CLIENT_TOKEN` | Runtime configuration |

Use a secrets manager or workload identity in production. Never place long-lived service credentials inside prompts, model instructions or model-visible tool arguments.

## 6. Local Development

```bash
docker compose up --build
```

Useful test commands:

```bash
make python-test
make java-test
```

If a target is not defined in the Makefile, run `pytest` in the Python service and `mvn test` in the Java service.

## 7. Reliability Engineering

Production hardening should include:

- Explicit deadlines for model, database, MCP and downstream calls.
- Bounded retries with exponential backoff and jitter.
- Idempotency keys for every mutation that may be retried.
- Circuit breaking for unhealthy providers or downstream services.
- Cancellation propagation for abandoned requests.
- Concurrency limits to prevent retry storms and resource exhaustion.
- Persistent evidence for ambiguous failures where the caller cannot know whether a side effect committed.
- Schema/version compatibility checks between Python and Java boundaries.
- Graceful degradation when optional AI capabilities are unavailable.

## 8. Security & Governance

- Replace development tokens with OAuth/OIDC or workload identity.
- Validate tenant authorization at **every** storage and action boundary.
- Give agents narrow tools rather than unrestricted database/shell/cloud credentials.
- Treat RAG documents, webpages, images and tool results as untrusted data.
- Add enterprise DLP/PII controls; regex examples are not a complete DLP solution.
- Enforce egress allowlists and SSRF protection in connector services.
- Require human approval and separation of duties for high-impact actions.
- Redact secrets and sensitive payloads from traces.
- Export audit events to immutable/WORM storage when compliance requires it.

## 9. Observability

Correlate the following with a request/workflow/task/incident id:

| Signal | Examples |
|---|---|
| AI | model/provider, latency, tokens, tool calls, retries |
| Retrieval | query latency, candidate count, rerank latency, citations |
| Tools | tool name, decision, latency, success/failure, approval wait |
| Platform | HTTP latency, DB latency, queue depth, Redis errors |
| Business | task success, incident recovery, workflow completion, eval gate |
| Cost | input/output tokens, model cost, tool/infrastructure cost |

Do not log raw prompts or documents by default when they can contain confidential information.

## 10. Testing Strategy

### Deterministic software tests
Unit-test schemas, policy, routing, parsing, idempotency and tool adapters.

### Integration tests
Exercise PostgreSQL/pgvector, Redis, MCP/API contracts and provider adapters.

### AI evaluations
Use versioned datasets for correctness, groundedness, tool selection, citation behavior and refusal/safety behavior.

### Failure and security tests
Inject timeouts, duplicate requests, provider outages, malformed tool output, prompt injection, cross-tenant requests and approval bypass attempts.

## 11. Scaling and Production Topology

Keep gateway replicas stateless, centralize distributed limits/approval state, shard tools by trust domain and use workload identity downstream.

A typical production topology is:

```text
Global / Regional Load Balancer
            |
     Stateless API replicas
            |
    +-------+--------+
    |                |
AI workers       Policy services
    |                |
Retrieval        Approval/Audit
    |
Java/MCP tool services
    |
Enterprise systems

Managed PostgreSQL / Vector Store
Managed Redis
OpenTelemetry Collector
Secrets / Workload Identity
```

## 12. Key Trade-Off

The gateway adds latency and critical-path infrastructure, but prevents policy and credential sprawl across every agent.

The architecture should be evaluated on a **quality × latency × cost × reliability × security** frontier rather than optimizing model quality alone.

## 13. CI/CD and Deployment Roadmap

```text
Pull Request
   |
lint + unit tests
   |
integration tests
   |
AI/security eval gates
   |
container build + SBOM
   |
staging / shadow traffic
   |
canary
   |
production
   |
SLO + eval monitoring
```

Recommended next production steps:

- Kubernetes/Helm or a managed container platform.
- Workload identity and centralized secrets.
- OpenTelemetry propagation across Python → MCP → Java.
- Schema registry/versioning for tool contracts.
- Per-tenant quotas and cost budgets.
- Durable audit/event retention.
- Load tests and chaos/failure tests.
- Model/prompt/tool-policy canary rollout and rollback.
- Anonymized production-trace sampling into evaluation datasets.


1. Why Python owns AI-heavy orchestration while Java owns enterprise/action-plane concerns.
2. Which decisions must remain deterministic and outside the model.
3. Tenant identity propagation and confused-deputy prevention.
4. Idempotency under retries and ambiguous side-effect failures.
5. Provider/MCP failure modes and graceful degradation.
6. Schema evolution across polyglot services.
7. Human approval and separation-of-duties design.
8. Quality evaluation independent of uptime/latency.
9. Cost controls and token/tool-call budgets.
10. 10×/100× scaling and multi-region/data-residency changes.
11. Observability without leaking confidential prompts.
12. Threat modeling for prompt injection and poisoned tool/RAG content.

## 15. Portfolio Description

> **Enterprise MCP Gateway** — Designed and implemented a Python/Java enterprise AI reference platform with explicit control-plane/action-plane boundaries, production-oriented reliability, security/governance, observability, testing and AI evaluation patterns. 

## 16. Production Disclaimer

This is a reference implementation. Before production use, pin and verify SDK/model versions, perform full dependency and container security scans, run end-to-end integration/load/security tests, and integrate the platform with the organization's real identity, secrets, policy, audit, DLP and compliance systems.
