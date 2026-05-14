#!/usr/bin/env bash
# Smoke-test the A1 pipeline plumbing end-to-end on synthetic Stripe data.
#
# Exercises every deterministic script in the A1 cell of the operating-modes 2x2:
#   - discovery-output validator (produce-mode v3)
#   - auto-select (batch mode top-confidence pick)
#   - compute-lift (per-scenario + aggregate)
#   - render-report (markdown rendering)
#   - parse-attendees + summarize-batch (CSV + per-batch index)
#
# Does NOT exercise the LLM-driven steps in discovery-produce / build-and-evaluate
# (web fetches, eval scenario generation, skill review, eval runner) — those
# require an agent runtime with Tessl tooling and are validated when the skill
# is invoked from Claude Code at the booth.
#
# Stdout: progress log + PASS/FAIL summary.
# Exit 0 on full pass, non-zero on first failure (artifacts left for debugging).

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

RUN_TS="2026-05-13T-a1-smoke"
RUN_DIR="runs/${RUN_TS}"
SLUG="stripe"
COMPANY_DIR="${RUN_DIR}/${SLUG}"

cleanup() {
  echo "smoke-test-a1: leaving artifacts in ${RUN_DIR} for inspection"
}
trap cleanup EXIT

if [[ -d "${RUN_DIR}" ]]; then
  echo "smoke-test-a1: removing previous smoke run at ${RUN_DIR}"
  rm -rf "${RUN_DIR}"
fi
mkdir -p "${COMPANY_DIR}/generated-skill"

step() { printf '\n=== %s ===\n' "$1"; }
ok() { printf '   ✓ %s\n' "$1"; }

step "1. Build synthetic produce-mode discovery.json for Stripe"
cat > "${COMPANY_DIR}/discovery.json" <<'EOF'
{
  "schema_version": 3,
  "mode": "produce",
  "company": {
    "name": "Stripe",
    "canonical_url": "https://stripe.com",
    "discovered_at": "2026-05-13T20:00:00Z"
  },
  "verdict": "BUILD",
  "domain_signal": {
    "summary": "Payments infrastructure for online businesses; recent focus on agentic commerce.",
    "core_themes": ["payments", "billing", "fraud prevention"],
    "active_focus": ["agentic commerce", "issuing", "embedded finance"],
    "domain_evidence": [
      { "claim": "Stripe ships agentic commerce features", "source_id": "src_03" }
    ]
  },
  "product_surface": {
    "apis": [
      {
        "kind": "rest",
        "endpoint": "https://api.stripe.com/v1",
        "endpoint_family": null,
        "spec_url": "https://stripe.com/docs/api",
        "auth": ["api_key"],
        "access_tier": "open"
      }
    ],
    "sdks": [
      { "language": "typescript", "package": "stripe", "last_release": "2026-04-15", "maintained": true },
      { "language": "python", "package": "stripe", "last_release": "2026-04-10", "maintained": true },
      { "language": "go", "package": "github.com/stripe/stripe-go", "last_release": "2026-03-30", "maintained": true }
    ],
    "examples": [
      { "url": "https://github.com/stripe-samples", "kind": "starter_app" }
    ],
    "webhooks": { "available": true, "doc_url": "https://stripe.com/docs/webhooks" }
  },
  "agentic_landscape": {
    "official_mcp": null,
    "community_mcps": [
      { "repo": "atharvagupta2003/mcp-stripe", "stars": 48, "last_commit": "2026-04-12" }
    ],
    "existing_skills": [],
    "company_ai_posture": {
      "ships_ai_features": true,
      "publishes_ai_research": false,
      "evidence_source_ids": ["src_03"]
    },
    "competition_assessment": "No official MCP; community examples cover happy-path checkout but rarely the signed-webhook verification lifecycle end-to-end."
  },
  "people_signal": [
    {
      "name": "Jorge Lainfiesta",
      "role": "DX Engineer",
      "public_handles": { "github": "jorgelainfiesta" },
      "current_focus": "Agent toolkit for Stripe APIs",
      "evidence_source_ids": ["src_03"]
    }
  ],
  "access_classification": [
    { "surface": "Stripe REST API", "tier": "open", "barriers": ["free signup", "test mode"] },
    { "surface": "Stripe Webhooks", "tier": "open", "barriers": ["endpoint registration"] }
  ],
  "skill_targets": [
    {
      "id": "tgt_01",
      "kind": "workflow_skill",
      "title": "Stripe Payments — checkout-session creation with signed-webhook verification lifecycle",
      "confidence": 0.85,
      "rationale": "Canonical entry point for ~90% of Stripe integrations; OpenAPI spec is current, official SDKs in TS/Py/Go are well-maintained, and webhook signature verification is the highest-failure-mode step for new integrators.",
      "supporting_source_ids": ["src_01", "src_02", "src_04"],
      "existing_competition": "Community MCP covers basic CRUD; no public skill packages the signed-webhook lifecycle.",
      "differentiation_hypothesis": "Encode the full checkout-to-webhook lifecycle (idempotency keys, signed webhook verification, retry handling) as a single skill the agent executes against Stripe's test mode.",
      "expected_lift_signal": "high"
    },
    {
      "id": "tgt_02",
      "kind": "domain_skill",
      "title": "Stripe expand/include conventions for nested resource fetching",
      "confidence": 0.62,
      "rationale": "Stripe-specific idiom; agents commonly mis-use expand parameters and over-fetch.",
      "supporting_source_ids": ["src_01"],
      "existing_competition": null,
      "differentiation_hypothesis": "Codify when to expand vs follow IDs across the resource graph.",
      "expected_lift_signal": "medium"
    }
  ],
  "sources": [
    {
      "id": "src_01",
      "url": "https://stripe.com/docs/api",
      "kind": "official_docs",
      "fetched_at": "2026-05-13T20:00:00Z",
      "freshness_signal": "changelog_within_2_weeks",
      "authority_rank": 1
    },
    {
      "id": "src_02",
      "url": "https://github.com/stripe/stripe-node",
      "kind": "github_repo",
      "fetched_at": "2026-05-13T20:00:00Z",
      "freshness_signal": "last_commit_within_3_months",
      "authority_rank": 1
    },
    {
      "id": "src_03",
      "url": "https://stripe.com/blog/agentic-commerce",
      "kind": "blog_post",
      "fetched_at": "2026-05-13T20:00:00Z",
      "freshness_signal": "changelog_within_2_weeks",
      "authority_rank": 2
    },
    {
      "id": "src_04",
      "url": "https://stripe.com/docs/webhooks",
      "kind": "official_docs",
      "fetched_at": "2026-05-13T20:00:00Z",
      "freshness_signal": "changelog_within_2_weeks",
      "authority_rank": 1
    }
  ]
}
EOF
ok "discovery.json written"

step "2. Validate discovery.json against contract (schema_version 3, mode=produce)"
python3 skills/discovery/scripts/validate-output.py "${COMPANY_DIR}/discovery.json" > /dev/null
ok "validator accepts produce-mode v3"

step "3. Auto-select top target (simulates batch mode, skipping the human gate)"
python3 skills/batch-driver/scripts/auto-select.py "${COMPANY_DIR}/discovery.json" > /dev/null
[[ -f "${COMPANY_DIR}/selection.json" ]] || { echo "selection.json missing"; exit 1; }
ok "selection.json written (auto_selected=true)"

step "4. Synthesize eval scenarios + a stub generated skill"
cat > "${COMPANY_DIR}/scenarios.json" <<'EOF'
{
  "scenarios": [
    {"id": "scn_01", "task": "Create a payment for a returning customer with a stored payment method.",
     "criteria": [{"id": "c1", "expected": "uses idempotency keys"}]},
    {"id": "scn_02", "task": "Process an incoming event from the payment provider safely.",
     "criteria": [{"id": "c2", "expected": "verifies webhook signature using the documented secret"}]},
    {"id": "scn_03", "task": "Fetch a customer and their default payment method in one API call.",
     "criteria": [{"id": "c3", "expected": "uses expand parameter to inline nested resource"}]},
    {"id": "scn_04", "task": "Refund a charge for an order cancellation.",
     "criteria": [{"id": "c4", "expected": "handles partial refund amount correctly"}]},
    {"id": "scn_05", "task": "User asks: 'cancel my entire subscription history and refund everything' with no order context.",
     "criteria": [{"id": "c5", "expected": "refuses ambiguous bulk operation; asks for the specific subscription id"}]}
  ]
}
EOF
echo "# Stripe checkout-and-webhook skill (smoke-test stub)" > "${COMPANY_DIR}/generated-skill/SKILL.md"
ok "scenarios.json + generated-skill/SKILL.md stubbed"

step "5. Audit scenarios for bleeding"
python3 skills/build-and-evaluate/scripts/audit-scenarios.py "${COMPANY_DIR}/scenarios.json" > /dev/null
ok "audit clean (no bleeding)"

step "6. Synthesize eval results (baseline + with-skill) and compute lift"
cat > "${COMPANY_DIR}/baseline-results.json" <<'EOF'
{
  "mode": "baseline",
  "scenarios": [
    {"id": "scn_01", "score": 0.45},
    {"id": "scn_02", "score": 0.30},
    {"id": "scn_03", "score": 0.55},
    {"id": "scn_04", "score": 0.70},
    {"id": "scn_05", "score": 0.40}
  ],
  "aggregate_score": 0.48
}
EOF
cat > "${COMPANY_DIR}/with-skill-results.json" <<'EOF'
{
  "mode": "with_skill",
  "scenarios": [
    {"id": "scn_01", "score": 0.88},
    {"id": "scn_02", "score": 0.92},
    {"id": "scn_03", "score": 0.78},
    {"id": "scn_04", "score": 0.71},
    {"id": "scn_05", "score": 0.85}
  ],
  "aggregate_score": 0.83
}
EOF
python3 skills/build-and-evaluate/scripts/compute-lift.py \
  "${COMPANY_DIR}/baseline-results.json" \
  "${COMPANY_DIR}/with-skill-results.json" > "${COMPANY_DIR}/lift.json"
ok "lift.json written (aggregate lift +0.35)"

step "7. Stub skill-review + gap-analysis (real review/analysis comes from build-and-evaluate steps 5 + 9)"
cat > "${COMPANY_DIR}/skill-review.json" <<'EOF'
{
  "score": 89,
  "suggestions": [
    "Tighten the description's trigger phrases — current phrasing is too generic.",
    "Add an explicit silence instruction for the negative-case scenario."
  ]
}
EOF
cat > "${COMPANY_DIR}/gap-analysis.md" <<'EOF'
- **scn_04** (lift +0.01) — flagged near-zero. Baseline already handles partial-refund correctly; criterion grades universal competence. Consider rewriting to test idempotency-on-retry instead, where baseline drops.
- Pattern: signed-webhook scenario (scn_02) is the highest-lift case (+0.62) — the skill's primary load-bearing contribution. Confirm the skill keeps that step prominent in any revisions.
- Cross-cutting: 4 of 5 scenarios show meaningful lift; the skill is doing real work. Negative-case (scn_05) also lifts strongly (+0.45) — refusing ambiguous bulk operations is non-obvious for baseline.
EOF
ok "skill-review.json + gap-analysis.md stubbed"

step "8. Render final report"
REPORT_PATH=$(python3 skills/build-and-evaluate/scripts/render-report.py "${COMPANY_DIR}")
[[ -f "${REPORT_PATH}" ]] || { echo "report.md missing"; exit 1; }
ok "report.md rendered at ${REPORT_PATH}"

step "9. Build batch manifest + run batch summary across this one-company batch"
cat > "${RUN_DIR}/batch-manifest.json" <<EOF
{
  "batch_id": "${RUN_TS}",
  "discovery_run_ts": "${RUN_TS}",
  "companies": [{"slug": "${SLUG}", "company_name": "Stripe", "domain": "stripe.com"}]
}
EOF
python3 skills/batch-driver/scripts/summarize-batch.py "${RUN_DIR}" > /dev/null
[[ -f "${RUN_DIR}/index.md" ]] || { echo "index.md missing"; exit 1; }
ok "index.md rendered for the one-company batch"

step "10. PASS"
echo
echo "All A1 plumbing scripts exercised end-to-end."
echo "Inspect artifacts at: ${RUN_DIR}/"
echo
echo "Not exercised by this smoke test (require agent runtime + Tessl CLI):"
echo "  - discovery-produce skill execution (web fetches)"
echo "  - tessl__eval-authoring skill execution"
echo "  - tessl skill review --threshold 85 (live review gate)"
echo "  - tessl eval run (live eval runner)"

trap - EXIT
