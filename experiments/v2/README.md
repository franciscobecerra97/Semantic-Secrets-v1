# v2 preregistered experiment boundary

P8 created the design record and machine-readable preregistration. P9 subsequently executed the frozen capability screen and ended with a negative Gate V2-A result. It did not access sealed v1 families or implement cryptography.

The authoritative files are:

- `docs/formal_specification_v2.md` for graph, policy, predicate, data, baselines, uncertainty, and gate semantics;
- `experiments/v2/config/semantic_graph_v2.json` for the closed machine-readable graph vocabulary and malformed-input rules;
- `experiments/v2/config/preregistration_v2.json` for executable constants and selection limits;
- `docs/p8_novelty_review_v2.md` for Gate V2-N and narrowed claims.

Execution order is binding:

1. P9A capability fixtures and extractor screen;
2. P9B independent reconstruction only for surviving extractor(s);
3. Gate V2-A;
4. P10 policy/baseline comparison and Gate V2-B;
5. P11 attacks and Gate V2-C.

Current disposition: step 1 failed for both frozen extractors by exact schema-validity futility (`31/32 = 0.96875 < 0.98`). Step 2 was consequently forbidden, Gate V2-A failed, and P10/P11 are blocked. The evidence and bounded interpretation are in `docs/p9_capability_screen_v2.md`.

Smoke results can detect broken plumbing but cannot alter candidates, metrics, thresholds, data roles, or gates. Any outcome-affecting amendment creates a new version before the affected output is viewed.
