"""Start here: a text walkthrough. This script runs no models and writes nothing."""
from audit_common import ROOT, HERE

print(f"""
P9-v2 manual audit -- step by step

1. DATA: author_p9.scenario() declares a graph; Pillow draws it. These are
   programmatic drawings, not AI-generated images. The graph also becomes the
   reference label. 96 images exist: 64 development + 32 validation.
2. INSPECT: 01_inspect_dataset.py verifies image hashes and shows reference
   labels, bounding boxes, the exact extraction prompt, and dataset limitations.
3. MODEL: 02_run_inference.py gives ONLY the image and fixed prompt to an already
   pretrained model. No weights are trained. Default is a plan; --execute runs.
   Choices: one image, all 96, the 64 development, or the 32 validation images.
4. FORMAT: JSON parsing and graph validation happen before semantic scoring.
   Raw answers and errors are preserved, even when invalid.
5. SCORE: 03_validate_outputs.py independently reparses saved answers and compares
   valid graphs against references. Invalid output misses all reference facts.
   A valid JSON graph can still describe the image incorrectly.
6. REPLAY: 04_replay_history.py checks saved historical answers and the 31/32
   calculation without running models. It does not redo the unexecuted images.
7. LEARN: 05_teaching_examples.py supplies perfect, wrong-but-valid, malformed,
   fenced, and missing-count examples. These are clearly marked artificial.

The original experiment stopped after one invalid validation image/model.
Manual full-dataset runs finish their selected images to diagnose failures.
They do not replace that historical gate or start the v3 research experiment.

Project: {ROOT}
Read:    {HERE / 'README.md'}
All generated files stay under: {HERE / 'outputs'}
""")
