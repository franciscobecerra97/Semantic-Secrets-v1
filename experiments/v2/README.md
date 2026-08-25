# v2 preregistered experiment boundary

P8 created only this design record and the machine-readable preregistration. It did not acquire models or data, generate images, access the sealed v1 families, run a v2 experiment, or implement cryptography.

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

Smoke results can detect broken plumbing but cannot alter candidates, metrics, thresholds, data roles, or gates. Any outcome-affecting amendment creates a new version before the affected output is viewed.
