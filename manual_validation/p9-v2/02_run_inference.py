"""Step 2: run the two frozen P9-v2 extractors on CPU."""
import argparse
from audit_common import BACKENDS, SCOPES, make_plan, output_path, run_inference, select_records

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", choices=("both", *BACKENDS), default="both")
    parser.add_argument("--scope", choices=SCOPES, default="one")
    parser.add_argument("--image-id", default="cap-v2-064", help="Used only with --scope one")
    parser.add_argument("--run-dir", help="New directory under manual_validation/p9-v2/outputs")
    parser.add_argument("--repeat-validation", action="store_true", help="Repeat selected validation images once")
    parser.add_argument("--resume", action="store_true", help="Continue an interrupted run with matching source hashes")
    parser.add_argument("--execute", action="store_true", help="Actually load weights and run inference; omitted = plan only")
    args = parser.parse_args()
    if args.resume and not args.run_dir:
        parser.error("--resume requires the original --run-dir")
    rows = select_records(args.scope, args.image_id)
    models = BACKENDS if args.models == "both" else (args.models,)
    path = output_path(args.run_dir, args.scope)
    plan = make_plan(rows, models, args.repeat_validation)
    print(f"Selected {len(rows)} images; output: {path}")
    for backend, tasks in plan.items():
        print(f"{backend}: {len(tasks)} inference calls on CPU; no automatic early stop")
    print("Historical timings: about 158s/image Moondream and 392s/image SmolVLM2, plus loading.")
    if not args.execute:
        print("Plan only. Add --execute to run. No files or model downloads were created.")
        return
    path, success = run_inference(rows, models, path, args.repeat_validation, args.resume)
    print(f"\nRun directory: {path}\nNext: python 03_validate_outputs.py --run-dir \"{path}\"")
    if not success:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
