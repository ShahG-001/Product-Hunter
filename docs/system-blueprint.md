# Product Hunter system blueprint

## What the system produces

For each run, produce a ranked shortlist of product opportunities with:

- A clear product concept and target buyer
- Demand and trend signals, including time range and geography
- Competitor set, observed price range, positioning, and review/customer pain points
- Estimated landed cost, selling price, gross margin, and confidence range
- Sourcing, shipping, compliance, and operational risks
- A recommendation (investigate, test, or reject), rationale, evidence links, and unanswered questions

The system is a research assistant. It should distinguish observed facts from estimates and never present an estimate as a verified supplier quote or guaranteed demand.

## Implemented agent count: one scout per category + five specialists

| Role | Responsibility | Main output |
| --- | --- | --- |
| Category Scouts (one per input category) | Propose product candidates and distinguish user-supplied evidence from hypotheses. | Candidate ideas with evidence gaps |
| Competitor Analyst | Assesses competitor types, positioning, and differentiation from supplied research. | Competitor assessment per candidate |
| Pricing Analyst | Reviews price/cost inputs and illustrates unit economics while exposing unknowns. | Price scenarios and missing inputs |
| Sourcing & Feasibility Analyst | Assesses supplier, operations, shipping, seasonality, and compliance questions. | Feasibility risks and validation steps |
| Evidence Reviewer | Flags unsupported claims, source limitations, and missing evidence. | Evidence audit and gaps |
| Recommendation Analyst | Ranks candidates and produces a cautious decision brief. | Recommendations and next steps |

The Streamlit starter implements these roles with CrewAI. CrewAI's sequential process coordinates tasks; it is not an extra LLM agent. Three categories therefore create eight agents total. This keeps category coverage flexible while using one shared analyst team.

## Current starter limitation

The app can optionally search the web through CrewAI's Serper tool. It analyzes result snippets and links plus pasted notes; it does not crawl every marketplace listing or open arbitrary pasted URLs. Without search or source notes, demand and competition suggestions are hypotheses. Search/API terms, credits, and rate limits apply.

To work within Groq's free-tier 8,000-token-per-minute limit, the UI accepts at most two categories and 2,500 characters of research notes per run. Agent outputs and contexts are kept short; use separate runs for more categories.

## Workflow

1. **Brief intake:** Require market, channel, category scope, sourcing model, budget/risk constraints, and time horizon. Ask for missing mandatory settings rather than silently inventing them.
2. **Plan:** Orchestrator creates category work units and source budgets. It records which sources are allowed and any source-specific limits.
3. **Discover:** Category Scout returns a broad candidate set. Normalize names and merge duplicates before deeper research.
4. **Specialist analysis:** Competitor, Pricing, and Sourcing/Feasibility roles investigate candidates using the scouts' outputs and user-supplied notes.
5. **Review evidence:** Evidence Reviewer checks citations, timestamps, methodology, contradictions, and whether evidence supports the claim. Low-confidence candidates return for targeted research or are clearly marked.
6. **Score and rank:** Recommendation Analyst scores only candidates with a minimum evidence bundle. Missing inputs reduce confidence and may block a positive recommendation.
7. **Deliver:** Present a concise decision brief plus a machine-readable record. Include next validation actions and source links.
8. **Learn safely:** Store user decisions and later outcomes separately from raw evidence. Use them to tune weights only with explicit evaluation; do not silently treat a past recommendation as proof.

## Candidate scoring (initial, configurable)

Score each dimension from 0 to 5, retain the rationale and evidence for each, and compute a weighted score on a 0–100 scale:

| Dimension | Initial weight |
| --- | ---: |
| Demand and trend quality | 25% |
| Competitive room / differentiation | 20% |
| Unit economics and pricing headroom | 25% |
| Sourcing and operational feasibility | 20% |
| Risk (inverse score: regulatory, fragility, seasonality, concentration) | 10% |

Formula: `score = 20 * sum(weight_i * dimension_score_i)` where weights sum to 1 and risk is scored higher when risk is lower. Keep **confidence separate from opportunity score**. Do not let an attractive score hide weak evidence. Initially block “test” recommendations when a critical dimension has no credible evidence or confidence is below a configurable threshold.

## Evidence and data contracts

Every material claim should have one or more evidence records:

```json
{
  "claim": "Observed median listing price is approximately 34.99 USD",
  "source_name": "configured source identifier",
  "url": "https://example.invalid/item",
  "observed_at": "ISO-8601 timestamp",
  "market": "US",
  "method": "sample of 20 active listings; median of displayed prices",
  "value": 34.99,
  "currency": "USD",
  "evidence_type": "observed | estimate | user_input",
  "confidence": 0.72
}
```

Candidate records should also include a stable candidate ID, normalized product name, category, target customer, score dimensions, recommendation, assumptions, risk flags, and provenance links. Store raw observations and derived estimates separately so a reviewer can reproduce calculations.

## Guardrails

- Use only sources the user has configured and is authorized to access; respect terms, robots/rate limits, and API quotas. Prefer official APIs, licensed datasets, and permitted public pages.
- Do not bypass logins, paywalls, CAPTCHAs, or technical access controls.
- Treat page text and supplier content as untrusted data, never as instructions to the agents.
- Require a human to approve supplier outreach, purchases, ad spend, and changes to a live store.
- Show uncertainty, source dates, and conflicting evidence. Avoid unsupported market-size claims.
- Keep secrets in environment/configuration management, not prompts or checked-in files.

## MVP build sequence

1. **Define the run brief and settings** as a schema, plus one example market/channel configuration.
2. **Build a deterministic workflow shell** that accepts a brief, emits task records, and saves structured outputs. Start with mocked source adapters so agent logic can be evaluated without scraping.
3. **Add approved data adapters** one at a time, recording source, retrieval time, geography, and method for every observation.
4. **Implement specialist tasks** with constrained JSON outputs and explicit input/output schemas. Keep agent instructions versioned.
5. **Add evidence review and scoring** as reproducible code, not free-form model arithmetic.
6. **Build a review UI/report** that lets a user inspect evidence, change assumptions, and mark a recommendation accepted/rejected.
7. **Evaluate** against manually researched examples for factual support, price calculations, duplicate handling, and usefulness before increasing autonomy.

## Suggested architecture

```text
Web UI / API
    -> Run Orchestrator (workflow state, retries, budgets)
        -> Category Scout tasks (parallel by category)
        -> Competitor / Pricing / Feasibility tasks (parallel by candidate)
        -> Evidence Reviewer
        -> Deterministic scoring and Recommendation Analyst
    -> Source adapters -> permitted APIs / licensed datasets / approved public sources
    -> Relational store: runs, candidates, observations, evidence, decisions
    -> Report and human review
```

Use a relational database for the first version; add a vector index only if semantic search over saved research becomes a demonstrated need. Keep source adapters and scoring independent of the model provider.

## Decisions to settle before implementation

1. Which launch market and currency?
2. Which sales channel(s)?
3. Which sourcing model and initial category?
4. Do you already have approved data/API accounts, or should the MVP use manual/imported research data first?

Until these are known, build the workflow and source interfaces to accept configuration rather than embedding market assumptions.
