# Bounded VLM observations and canonical graph proposal v1

This is an isolated, offline design prototype for the author's 2026-10-22
proposal. It does not replace the active P9-v3 compiler or modify historical
experiments, freezes, vocabulary, gates, or results. Its JSON files are synthetic
examples, not observations of an image. No VLM inference or API experiment was
run to validate this prompt. Passing compiler tests is engineering evidence,
not extraction accuracy or an authentication result.

## Recommended division of work

1. The VLM describes bounded, directly visible observations.
2. Python validates the schema, resolves approved vocabulary aliases, and
   constructs a canonical graph.
3. A separate, frozen policy decides which facts are mandatory or tolerant.
4. A construction-specific protection mechanism handles authentication.

Only steps 1's proposed prompt and step 2's reference implementation are supplied
here. A graph fingerprint is a diagnostic equality identifier, not an enrolled
credential, password hash, privacy mechanism, or proof of entropy.

## Files

| File | Purpose |
| --- | --- |
| `extraction_prompt.txt` | Short shared prompt for a Moondream3/SmolVLM2 pilot |
| `vocabulary.json` | Versioned, field-specific canonical tokens and approved aliases |
| `canonicalize.py` | Strict parser, validator, canonical graph labeling, fingerprint CLI |
| `example.json` | Synthetic cat/sofa/book observation |
| `example_synonyms.json` | Equivalent observation with different IDs, order, and aliases |
| `test_canonicalize.py` | Synthetic compiler invariants and failure cases |

## Observation schema

```json
{
  "objects": [
    {"id": "o1", "label": "cat", "color": "red"},
    {"id": "o2", "label": "sofa", "color": "blue"},
    {"id": "o3", "label": "book", "color": "yellow"}
  ],
  "facts": [
    {"subject": "o1", "predicate": "sleeping", "object": null},
    {"subject": "o1", "predicate": "on", "object": "o2"},
    {"subject": "o3", "predicate": "on", "object": "o2"}
  ],
  "scene": "bedroom"
}
```

The bounded design has at most five distinct object instances, one color per
object (at most five color observations), five facts TOTAL, and one scene. The
combined fact limit is stricter than allowing five actions plus five relations.
That is a deliberate starting budget for a small-model pilot. Increase it only
in a new version if development evidence supports doing so.

`sleeping` is unary; it needs no second object. `on` is a separate binary fact.
`holding`, `reading`, `wearing`, and `riding` require a target object in this
version. There are no separate attribute, action, relation, or scene IDs to
generate or join. Objects have local IDs because the same object class can occur
more than once. IDs do not encode position or enter the final representation
unchanged. A single scene label applies to the whole image.

One small deviation from excluding all position is recommended: retain coarse
support/containment predicates `on` and `inside` because they distinguish the
concept. Coordinates and left/right geometry are excluded. If every positional
relationship is excluded, the system can retain cat + sofa + sleeping, but loses
the explicit information that the cat is on that sofa.

Unknown color/scene uses JSON `null`, not an invented label. Person color is
always null so that clothing color or demographics do not become person
attributes. Colors describe an object's own dominant visible surface. A hat or
umbrella may be a separately represented colored object. Multiple colors are
not forced into a single guess.

The cap defines a selected description, not a complete inventory. Node count
preserves the number of represented instances, not necessarily every instance
visible in a crowded image. Selection and salience can vary across VLM runs;
simple scenes within the cap are preferable for the initial pilot.

## Vocabulary policy

The starting vocabulary has 21 object classes, 11 colors, six unary predicates,
seven binary predicates, and nine scene labels. It is a proposed domain, not a
claim that it covers arbitrary images. The prompt requests canonical labels;
Python also accepts explicitly approved aliases that a model may return.

| Observation | Canonical handling |
| --- | --- |
| `couch` | `sofa` |
| `napping`, `asleep` | `sleeping` |
| `man`, `woman`, `human` | `person` class; demographics intentionally excluded |
| `men`, `people` | `person` class only; never infer or alter instance counts from this word |
| `grey` | `gray` |
| `notebook` | `notebook`, distinct from `book` |
| `felim`, `feline` | Unsupported; no automatic spelling or category guess |
| `staying` | Unsupported; does not specify an action or support relationship |
| `living_room` vs `bedroom` | Different scenes |
| `indoor` vs `bedroom` | Different descriptions; broad vs specific is not identity |
| `carrying` vs `holding` | No automatic equivalence |
| `under(A,B)` vs `on(B,A)` | No equivalence: being underneath does not establish contact/support |

Alias rules are field-specific; a color cannot become an object label. Unicode
NFKC, case folding, trimming, and whitespace/hyphen normalization occur before
lookup. Inflections are listed explicitly; there is no indiscriminate suffix
removal, stemming, nearest-word correction, or nearest-vector replacement.

The inverse `contains(A,B) = inside(B,A)` is explicitly allowed for postprocessing.
`touching` is treated as symmetric; directed predicates such as `holding` and
`on` are not. No transitive closure or inferred facts are added.

WordNet can propose candidate synonyms during development because it represents
word senses and semantic relations. A human/project decision should select the
relevant sense and approve the final lookup table. Embeddings can similarly help
find candidates to review; semantic similarity is not an equivalence guarantee.
Do not introduce a second VLM/LLM rewrite into the deterministic compiler.

If the project chooses a broader abstraction, do it uniformly and prospectively.
For example, mapping every known indoor room to `indoor` could remove room-type
differences, but also removes discriminating information. It must not relabel a
living room as a bedroom. Any collapse of book/notebook must use a deliberately
defined superclass, rather than claim the two labels are synonyms.

## Canonicalization algorithm

1. Strictly parse JSON. Reject duplicate keys, invalid JSON, nonstandard numeric
   constants, unknown/extra keys, and input exceeding 32 KiB. There is no JSON or
   semantic repair. A decoder that guarantees schema-valid JSON, if supported,
   still does not guarantee true image observations.
2. Validate all object IDs, references, predicate arities, vocabulary entries,
   and caps. Fail on over-limit input rather than silently selecting a subset.
   Fail on an empty object list; no common empty-graph fingerprint is issued.
3. Normalize approved aliases, apply explicit inverse/symmetry rules, and remove
   exact duplicate facts. Preserve distinct object instances and disconnected
   objects. Do not merge nodes just because their labels/colors match.
4. Consider every renaming of the at-most-five object IDs to `n1` ... `n5`.
   Under each renaming, rewrite every reference, order the object list by the new
   IDs, normalize symmetric endpoints, and sort the facts. Choose the
   lexicographically smallest serialized graph. At most 5! = 120 candidates
   makes this exhaustive graph canonicalization practical for this bound.
5. Serialize the graph with a fixed compact JSON encoder. The graph includes
   scheme version, vocabulary version, and vocabulary content SHA-256. Changing
   mappings changes the fingerprint even if a version label was not updated.
6. Compute `SHA256(b"semantic-graph-fingerprint/v1\0" + canonical_utf8_bytes)`
   for diagnostic equality comparisons. Failure results contain no fingerprint.

The implementation's encoder is specified only for this restricted graph and
is not a general RFC 8785 implementation. For a broader, cross-language data
format, use an RFC 8785/JCS library after graph labeling. Sorting JSON object
keys alone never resolves arbitrary graph IDs or unordered arrays.

The deterministic guarantee is: if two accepted observations describe isomorphic
graphs under these exact frozen alias/arity/inverse/symmetry rules, the compiler
emits identical canonical JSON and fingerprints. It does not guarantee that two
VLM runs or independent images will describe the same graph. Missing objects,
different colors, different actions, and different scenes remain differences.

`null` is part of the graph and is not a wildcard. A later policy may explicitly
treat selected secondary facts tolerantly, but missing mandatory anchors must
reject. Do not interpret hash distance as semantic distance.

## Matrix view

Your original row layouts change column order between examples. Keep one typed
layout if a matrix is useful for display. A six-column display projection is
`[subject_label, subject_color, predicate, target_label, target_color, scene]`:

```json
[
  ["cat", "red", "sleeping", null, null, "bedroom"],
  ["cat", "red", "on", "sofa", "blue", "bedroom"],
  ["book", "yellow", "on", "sofa", "blue", "bedroom"]
]
```

These are strings, not numerical embedding vectors. This projection loses
instance identity when labels repeat and omits objects without facts. The
complete canonical node/edge graph is authoritative, not the display matrix.
An embedding average or an untyped bag of labels also loses role bindings.

## Run in Python

Python 3.10+ and the standard library are sufficient. From the repository root:

```powershell
python manual_validation/semantic_graph_proposal_v1/canonicalize.py manual_validation/semantic_graph_proposal_v1/example.json
python manual_validation/semantic_graph_proposal_v1/canonicalize.py manual_validation/semantic_graph_proposal_v1/example_synonyms.json
python -m unittest discover -s manual_validation/semantic_graph_proposal_v1 -v
```

The two example inputs produce identical `graph`, `canonical_json`, and
`fingerprint_sha256` values. CLI exit status is zero for success and two for
failure. Tests were run on Python 3.12.13: 30 passed. They cover aliases, complete
three-node ordering combinations, equal-label nodes with distinct roles,
all 120 five-node object orderings, disconnected nodes, multiplicity, color
bindings, directed/symmetric/inverse predicates, scene disagreements, version
content changes, and malformed input.

To integrate into an existing Python extraction script when this folder is on
the Python import path:

```python
from pathlib import Path
from canonicalize import Canonicalizer

experiment = Path("manual_validation/semantic_graph_proposal_v1")
prompt = (experiment / "extraction_prompt.txt").read_text(encoding="utf-8")
# Send image + prompt through the existing, separately configured VLM adapter.
# raw_answer must be ONLY the generated JSON text, excluding input/prompt tokens.
result = Canonicalizer(experiment / "vocabulary.json").canonicalize(raw_answer)
```

No API adapter is included and no model was called. Preserve the unmodified raw
answer and inference provenance separately from the canonical graph. Failure
details are for offline experiment diagnostics, not messages to an
authentication client.

## Model pilot and evaluation proposal

Use the same prompt, vocabulary, preprocessing, and image inputs for both
specified models. Pin the exact Moondream3 model/checkpoint and exact SmolVLM2
checkpoint or Space revision; a changing default/demo is not a fixed model.
Moondream's Query documentation explicitly describes JSON prompting. The
SmolVLM2-2.2B-Instruct model card demonstrates image/text chat templates and
`do_sample=False` generation. These support a pilot, not a schema-accuracy claim.

Where the actual backend exposes generation controls, start with greedy decoding
and enough output tokens for a complete bounded graph (512-768 is a starting
budget to measure, not an asserted requirement). Do not invent parameters that
a hosted endpoint does not accept. Greedy decoding reduces one source of
variation but does not establish repeatability across hardware/model/backend
changes. If supported, constrained JSON decoding helps syntax; semantic truth
and reference/arity constraints still need evaluation.

Do not pass generating prompts, expected labels, or references to the VLM. Keep
reference labeling independent of predictions. Use permitted development inputs
to select rules and freeze all choices before separate held-out evaluation.
In the existing project this proposal alone does not declare a dataset freeze
or start P9-v3B.

Measure these separately, by model and controlled/naturalistic stratum:

- JSON validity, schema acceptance, non-empty rate, and each failure code over
  all attempts; do not silently exclude failures.
- Object, attribute, predicate, and scene precision/recall; object identity and
  role binding must be included in graph comparison.
- Complete graph fidelity against independently authored references.
- Same-image repeat exact canonical agreement, counting failures separately.
- Exact agreement for independent same-concept image pairs.
- Targeted separation for color changes, person/object role swaps, predicate
  changes, multiplicity changes, scene changes, and book/notebook alternatives.
- Latency, truncation, raw output length, and complete-pipeline resource cost.

Report intervals and denominators. A simpler prompt may improve schema success
but must be measured for both omitted facts and false merges. If needed, compare
one-call extraction with a versioned two-call alternative (objects first, facts
over fixed IDs second) on development data. The two-call alternative adds cost
and can propagate object mistakes; it is not automatically superior.

Finally, the exact canonical fingerprint is useful for measuring stability.
Approximate authentication, if pursued, remains a separate policy/predicate
problem. More aggressive normalization enlarges the accepted semantic region
and can make targeted guesses easier. A short bounded representation does not
by itself establish adequate authentication security or privacy.

## Primary sources consulted

- Moondream Query: https://docs.moondream.ai/skills/query/
- SmolVLM2-2.2B-Instruct model card: https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct
- RFC 8785, JSON Canonicalization Scheme: https://www.rfc-editor.org/rfc/rfc8785
- Princeton WordNet, concepts/senses and semantic relations: https://wordnet.princeton.edu/
