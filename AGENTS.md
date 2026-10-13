# legion-llm Agent Notes

## Scope

`legion-llm` provides provider configuration, chat/embed/structured interfaces, dynamic routing, escalation, quality checks, and pipeline execution for Legion.

## Fast Start

```bash
bundle install
bundle exec rspec
bundle exec rubocop
```

## Primary Entry Points

- `lib/legion/llm.rb`
- `lib/legion/llm/call/providers.rb`
- `lib/legion/llm/router/`
- `lib/legion/llm/inference/`
- `lib/legion/llm/call/structured_output.rb`
- `lib/legion/llm/call/embeddings.rb`
- `lib/legion/llm/fleet/`

## Guardrails

- Keep typed error behavior and retry semantics stable (`ProviderDown`, `RateLimitError`, `EscalationExhausted`, etc.).
- Routing and escalation must remain deterministic given the same inputs/settings.
- Preserve pipeline feature-flag behavior; avoid forcing pipeline-only code paths.
- Keep provider credentials resolved through settings secret resolution flow; never hardcode secrets.
- Maintain compatibility with direct methods (`chat_direct`, `embed_direct`, `structured_direct`) and daemon-aware flows.
- Health tracker and rule scoring are contract-sensitive; changes require spec updates.

## Validation

- Run targeted specs for modified router/pipeline/provider code.
- Before handoff, run full `bundle exec rspec` and `bundle exec rubocop`.

## Fork-local workflow

Read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for canonical validation boundaries and the repository-specific helper. Use the `review-legion-routing` skill in `.agents/skills/` for this review workflow.
