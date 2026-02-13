## Relevant Files

- `src/api/routes.py` - Implement `/gaps/analyze`, tighten request schema defaults, and improve error handling.
- `src/contracts/content_gap.py` - Confirm/update API-facing input contract compatibility for endpoint payload.
- `src/models/topics.py` - Verify topic model mapping used by gap-analysis endpoint.
- `src/agents/content_gap.py` - Reuse existing gap-analysis behavior and verify API integration assumptions.
- `run.py` - Ensure CLI report generation behavior remains backward compatible after API adjustments.
- `tests/unit/test_api_routes.py` - New unit tests for API endpoints and validation/failure behavior.
- `tests/integration/test_orchestrator_pipeline.py` - New integration-style deterministic pipeline execution test.
- `docs/user-guide.md` - Document `/gaps/analyze` usage and request/response expectations.

### Notes

- Keep endpoint behavior deterministic under `NO_NETWORK_MODE=true`.
- Preserve existing API routes and response structure where possible.
- Use `PYTHONPATH=src` for test execution commands.

## Tasks

- [ ] 1.0 Implement gap-analysis API endpoint parity
### 1.1 Wire `ContentGapAgent` into `/gaps/analyze`
- Description: Replace `not_implemented` response with typed processing path using existing agent + contracts.
- Effort: Medium (4-6 hours)
- Dependencies: None
- Acceptance Criteria: Valid payload returns computed gap analysis with structured response data.

### 1.2 Add request schema and payload validation for gaps endpoint
- Description: Define explicit request model(s) and enforce required fields and type constraints.
- Effort: Medium (2-4 hours)
- Dependencies: 1.1
- Acceptance Criteria: Invalid payloads return deterministic `4xx` responses with concise error details.

### 1.3 Normalize model conversions for topics and competitors
- Description: Ensure conversion from request dicts to typed models follows current conventions.
- Effort: Small (1-2 hours)
- Dependencies: 1.1
- Acceptance Criteria: Endpoint handles mixed dict/model inputs without runtime conversion errors.

- [ ] 2.0 Fix schema safety and API robustness gaps
### 2.1 Replace mutable defaults in API request models
- Description: Update list defaults (for example `keywords=[]`) to safe factories.
- Effort: Small (30-60 minutes)
- Dependencies: None
- Acceptance Criteria: No mutable-default anti-pattern remains in API request schema models.

### 2.2 Standardize API exception handling for downstream failures
- Description: Wrap agent/integration exceptions into consistent HTTP errors without leaking internals.
- Effort: Medium (2-3 hours)
- Dependencies: 1.1
- Acceptance Criteria: Known failure scenarios return stable status codes and actionable messages.

### 2.3 Preserve current report generation compatibility
- Description: Verify and adjust route code so existing report generation payloads remain valid.
- Effort: Small (1-2 hours)
- Dependencies: 2.1
- Acceptance Criteria: Existing `/reports/generate` contract continues to work with no regressions.

- [ ] 3.0 Add test coverage for API and orchestrator paths
### 3.1 Add route unit tests for keyword, cluster, trends, gaps, and report endpoints
- Description: Create `tests/unit/test_api_routes.py` covering success and validation failures.
- Effort: Medium (4-6 hours)
- Dependencies: 1.0, 2.0
- Acceptance Criteria: Route tests pass locally and cover both happy path and error path for implemented endpoints.

### 3.2 Add integration-style deterministic orchestrator test
- Description: Create pipeline test using no-network defaults from `tests/conftest.py`.
- Effort: Medium (3-5 hours)
- Dependencies: 3.1
- Acceptance Criteria: Full pipeline executes under deterministic settings and asserts expected output artifacts.

### 3.3 Run quality gate commands and fix regressions
- Description: Run lint, typecheck, and unit tests; resolve failures.
- Effort: Small to Medium (1-3 hours)
- Dependencies: 3.1, 3.2
- Acceptance Criteria: `ruff check`, `mypy`, and unit tests pass with no new warnings/errors.

- [ ] 4.0 Update documentation and release readiness artifacts
### 4.1 Document `/gaps/analyze` endpoint contract and examples
- Description: Add usage guidance and request/response examples in user-facing docs.
- Effort: Small (1-2 hours)
- Dependencies: 1.0
- Acceptance Criteria: Docs include endpoint purpose, payload schema, and sample responses.

### 4.2 Capture implementation summary and remaining follow-ups
- Description: Record what was fixed, what remains deferred, and any follow-up PRD recommendations.
- Effort: Small (1 hour)
- Dependencies: 3.3, 4.1
- Acceptance Criteria: Final summary exists in project docs and references measurable outcomes.

## Suggested Agent Consultations

- `business-analyst`: verify endpoint consumer requirements and acceptance criteria completeness.
- `code-reviewer`: review API error-handling and conversion logic for maintainability.
- `security-reviewer`: verify error-message hygiene and request validation boundaries.
- `debugger-agent`: investigate any flaky behavior found in integration-style pipeline tests.
