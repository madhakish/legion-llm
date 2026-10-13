#!/usr/bin/env python3
"""Print review-oriented RSpec candidates; never load Ruby or execute tests.

Python 3.9+, standard library only. This is a conservative path map, not coverage
analysis or a sandbox. A candidate suite may still have application side effects.
"""
import argparse
import json
from pathlib import Path

CONFIG = {'entry': 'lib/legion/llm.rb',
 'groups': [('lib/legion/llm/router',
             ['spec/legion/llm/router_spec.rb',
              'spec/legion/llm/router/**/*_spec.rb',
              'spec/legion/llm/escalation_integration_spec.rb'],
             'Freeze time and provider health; exercise privacy constraints and escalation '
             'exhaustion without model calls.'),
            ('lib/legion/llm/inference',
             ['spec/legion/llm/inference/**/*_spec.rb', 'spec/legion/llm/integration_spec.rb'],
             'Test direct/daemon dispatch, typed errors, streaming chunk order and cancellation '
             'with fake responses.'),
            ('lib/legion/llm/call',
             ['spec/legion/llm/provider*_spec.rb',
              'spec/legion/llm/embeddings*_spec.rb',
              'spec/legion/llm/structured_output_spec.rb',
              'spec/legion/llm/daemon_client_spec.rb',
              'spec/legion/llm/codex_config_loader_spec.rb',
              'spec/legion/llm/native_dispatch_spec.rb',
              'spec/legion/llm/errors_spec.rb'],
             'Stub provider HTTP, auth loaders and retries; do not read user auth files or call '
             'providers.'),
            ('lib/legion/llm/api',
             ['spec/legion/llm/routes*_spec.rb'],
             'Use request doubles/Rack helpers; assert OpenAI/Anthropic response contracts without '
             'a live daemon.'),
            ('lib/legion/llm/fleet',
             ['spec/legion/llm/fleet/**/*_spec.rb'],
             'Use transport doubles; test timeout and correlation IDs without AMQP.')],
 'example': 'lib/legion/llm/router/rule.rb'}


def within(root, path):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def plan(root, paths):
    root = Path(root).resolve()
    if not (root / CONFIG["entry"]).is_file():
        raise ValueError("not the expected repository root")
    specs, risks, unmatched, missing = set(), set(), [], set()
    for raw in paths:
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts or not within(root, root / path):
            raise ValueError("changed paths must remain inside the repository")
        name = path.as_posix()
        candidates = set()
        if name.startswith("spec/") and name.endswith("_spec.rb"):
            candidates.add(name)
        if name.startswith("lib/") and name.endswith(".rb"):
            stem = path.stem
            candidates.update(p.relative_to(root).as_posix()
                              for p in (root / "spec").rglob(stem + "_spec.rb"))
        for prefix, patterns, risk in CONFIG["groups"]:
            if name.startswith(prefix):
                risks.add(risk)
                for pattern in patterns:
                    matched = list(root.glob(pattern))
                    if not matched:
                        missing.add(pattern)
                    candidates.update(p.relative_to(root).as_posix() for p in matched)
        valid = {p for p in candidates if (root / p).is_file()
                 and within(root, root / p) and not (root / p).is_symlink()}
        specs.update(valid)
        if not valid:
            unmatched.append(name)
    return {"spec_candidates": sorted(specs), "review_notes": sorted(risks),
            "unmapped_paths": sorted(set(unmatched)), "stale_patterns": sorted(missing),
            "full_suite_still_required": True, "executed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="repository-relative changed paths")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = plan(root, args.paths)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
