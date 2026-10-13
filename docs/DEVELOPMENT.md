# Fork development guide

This guide is for `madhakish/legion-llm`. Upstream architecture remains in [CLAUDE.md](../CLAUDE.md); this file is the canonical fork-local validation and automation guidance. Use the checked-out source and [lib/legion/llm/version.rb](../lib/legion/llm/version.rb) for current behavior/version, rather than historical example counts.

Agent entrypoints: [AGENTS.md](../AGENTS.md) and the [review-legion-routing skill](../.agents/skills/review-legion-routing/SKILL.md).

## Change routing

- Start with `lib/legion/llm.rb`, then `router/`, `inference/`, or `call/` according to the change. `start` loads Claude/Codex configuration, initializes providers, and performs discovery; do not use it as an offline smoke check.
- `spec/spec_helper.rb` stubs Legion logging/settings, resets settings per example, and requires WebMock plus the transport stub. Inspect individual specs before execution; mocks are not proof of real provider interoperability.
- Freeze the clock, provider availability and settings for routing tests. Cover hard privacy constraints, fallback exhaustion and schedule boundaries; keep deterministic ordering explicit.
- For inference changes cover direct/daemon dispatch, streaming event order, typed errors and budget/metering behavior using synthetic responses.
- Preserve repository JSON and logging conventions, but never include prompts, credentials or private response bodies merely to make debug logs diagnostic-complete.

## Safe validation

Do not call model providers, warm Ollama/fleet discovery, read user auth files, or start the daemon during ordinary validation. Use a disposable home and network-restricted test environment with synthetic provider configuration.

Python 3.9+ is sufficient for the read-only helper; it uses only the standard library:

```sh
python3 scripts/spec_plan.py lib/legion/llm/router/rule.rb
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Pass repository-relative changed paths to the planner. It returns existing spec candidates, cross-component review notes, unmapped files and stale curated patterns. It never loads Ruby or executes a test. Basename matching is conservative; inspect the result and add relevant integration coverage. It does not establish coverage or make the Ruby suite safe to run.

With Ruby >= 3.4 and dependencies provisioned in an approved disposable environment, inspect the spec helper, run the targeted specs, then `bundle exec rspec` and non-mutating `bundle exec rubocop`. Run `bundle check` before installing missing gems. Dependency installation may fetch packages and execute build hooks. If Ruby, dependencies or isolation are absent, report the blocked command; do not label static checks as passing RSpec. Autocorrection (`rubocop -A`) is an explicit code change, not a prerequisite to reading or reviewing this fork.

## GitHub Actions recommendations (not activated)

Prioritize router constraint/escalation tests and inference streaming/schema contracts with WebMock and transport doubles. Keep live provider compatibility and paid evaluations opt-in, isolated and separately authorized; no provider secrets in routine validation.

The checked-in workflows do not verify an available self-hosted runner. Direct jobs in this family use `ubuntu-latest`; reusable jobs call `LegionIO/.github` workflows at mutable `@main`. The inspected upstream workflows use `${{ inputs.runner || 'ubuntu-latest' }}` and these callers do not supply `runner`, so they inherit GitHub-hosted defaults at the reviewed snapshot. Before implementing the requested self-hosted policy, inspect the reusable workflows and the registered runner inventory; choose only verified labels. Do not guess OS/architecture labels or silently fall back to GitHub-hosted runners.

Because this is a public repository, never run unreviewed pull-request code on a personal persistent runner. Prefer an isolated ephemeral runner with no host mounts, production network access or reusable credentials. If only the personal runner exists, keep proposed validation disabled until that isolation is established. A trusted manual dispatch must validate an exact maintainer-reviewed commit; do not use `pull_request_target` to check out and execute a PR head. Minimize token permissions, pin reviewed actions/reusable workflows to immutable SHAs, set timeouts/concurrency, and separate test artifacts from secrets. Release, publishing and infrastructure changes need their own approval. No workflow files are changed by this development overlay.
