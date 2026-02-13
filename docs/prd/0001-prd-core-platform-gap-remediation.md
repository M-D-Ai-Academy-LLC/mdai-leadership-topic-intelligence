# 0001 PRD: Core Platform Gap Remediation

## 1. Introduction and Overview

This PRD defines a focused remediation release for `mdai-leadership-topic-intelligence` based on a codebase scan and the `/create-prd` workflow. The goal is to close functional and quality gaps that currently limit production readiness: incomplete API capability, weak endpoint validation/error behavior, and missing automated test coverage for core runtime paths.

## 2. Goals

1. Ship a complete API path for gap analysis parity with CLI behavior.
2. Eliminate high-risk request/response schema issues in API routes.
3. Add targeted test coverage for API and agent orchestration paths.
4. Improve runtime reliability and observability for pipeline execution.

## 3. User Stories

- As an API consumer, I want a working content-gap endpoint so I can run end-to-end analysis without using the CLI.
- As a platform maintainer, I want deterministic validation and clear failures so debugging production issues is faster.
- As an engineering lead, I want automated tests for core execution paths so releases are safer.

## 4. Functional Requirements

1. The system must implement `/gaps/analyze` in `src/api/routes.py` using the existing `ContentGapAgent` and typed contracts.
2. The system must replace mutable request defaults (for example list defaults) with safe factories in request schemas.
3. The system must add API-level validation and consistent error responses for malformed payloads and downstream integration failures.
4. The system must add unit tests for implemented API endpoints including success and failure cases.
5. The system must add at least one integration-style test for orchestrator execution with deterministic no-network settings.
6. The system must ensure report generation behavior remains backward compatible for current CLI flows.
7. The system must document the endpoint contract for `/gaps/analyze` and update user-facing docs.

## 5. Non-Goals (Out of Scope)

- Re-architecting all agents into a new framework.
- Introducing new external data providers.
- Full enterprise auth/RBAC implementation.
- Frontend/dashboard implementation.

## 6. Branding Requirements

Not applicable. This scope is internal platform engineering work, not a customer-facing visual deliverable.

## 7. Design Considerations

- Preserve existing API path structure and response style.
- Keep request/response contracts explicit and version-compatible.
- Prefer minimal diffs and additive improvements over broad refactors.

## 8. Technical Considerations

- `src/api/routes.py` currently returns `not_implemented` for `/gaps/analyze`; implement with `ContentGapInput` and model conversion patterns used elsewhere.
- `ReportGenerateRequest.keywords` currently uses `[]` default and should use `Field(default_factory=list)`.
- Ensure error handling wraps integration/agent failures into concise HTTP errors without leaking internals.
- Keep compatibility with deterministic test flags from `tests/conftest.py`.

## 9. Quality Standards

- Lint: `ruff check src/ tests/`
- Typecheck: `mypy src/ --ignore-missing-imports`
- Unit tests: `PYTHONPATH=src pytest tests/unit/ -v --tb=short`
- New tests should include API route coverage and one orchestrator execution path.
- Maintain Python 3.11 typing style and current import conventions.

## 10. Compliance and Documentation

- Follow existing attribution policy and repository documentation rules.
- Update API/usage docs where endpoint behavior changes.
- Record execution outcomes in project history/logs if this becomes a release milestone.

## 11. Success Metrics

- `/gaps/analyze` endpoint returns successful analysis for valid payloads.
- API route tests added and passing for all major endpoints.
- No mutable-default warnings in request schemas.
- CI baseline commands pass without regression.

## 12. Open Questions

1. Should `/gaps/analyze` accept raw competitor payloads only, or also auto-fetch competitors when omitted?
2. Do we want endpoint-level caching for repeat requests in this phase?
3. Should orchestrator session artifacts be exposed through an API endpoint in a follow-up PRD?

## Initial Gap Findings from Scan

- Incomplete endpoint: `src/api/routes.py:76` (`/gaps/analyze` not implemented).
- Schema risk: `src/api/routes.py:47` mutable list default in `ReportGenerateRequest`.
- Coverage gap: tests currently focus on config/contracts/models/scoring; no API route test module present.
- Operational gap: no dedicated integration test for full orchestrator pipeline execution path.

Document last updated on 2026-02-13. Verified against project logs, deliverables tracking, and communication archives.
