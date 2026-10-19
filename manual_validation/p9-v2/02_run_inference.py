"""Step 2: frozen P9-v2 extractors, or a separately labelled Moondream 3 comparison."""
import argparse
from pathlib import Path
from audit_common import BACKENDS, SCOPES, make_plan, output_path, run_inference, select_records

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", choices=("both", *BACKENDS, "moondream3"), default="both")
    parser.add_argument("--scope", choices=SCOPES, default="one")
    parser.add_argument("--image-id", default="cap-v2-064", help="Used only with --scope one")
    parser.add_argument("--run-dir", help="New directory under manual_validation/p9-v2/outputs")
    parser.add_argument("--repeat-validation", action="store_true", help="Repeat selected validation images once")
    parser.add_argument("--resume", action="store_true", help="Continue an interrupted run with matching source hashes")
    parser.add_argument("--execute", action="store_true", help="Actually load weights and run inference; omitted = plan only")
    parser.add_argument("--transport", choices=("local", "cloud"), default="local", help="Moondream 3 only; cloud sends selected capability image/prompt to Moondream")
    parser.add_argument("--reasoning", action=argparse.BooleanOptionalAction, default=None, help="Moondream 3 reasoning defaults on; --no-reasoning disables it")
    parser.add_argument("--max-tokens", type=int, default=None, help="Moondream 3 generation setting; default 384, matching the old numeric limit")
    parser.add_argument("--snapshot", help="Prepared local Moondream 3 snapshot directory")
    parser.add_argument("--api-key-env", default="MOONDREAM_API_KEY", help="Cloud credential environment-variable name, never the key itself")
    args = parser.parse_args()
    if args.resume and not args.run_dir:
        parser.error("--resume requires the original --run-dir")
    if args.models != "moondream3" and (args.reasoning is not None or args.max_tokens is not None or args.snapshot or args.transport != "local"):
        parser.error("The new reasoning/transport/snapshot/token options require --models moondream3")
    if args.max_tokens is not None and args.max_tokens < 1:
        parser.error("--max-tokens must be positive")
    experimental = None
    if args.models == "moondream3":
        if args.transport == "cloud" and args.snapshot:
            parser.error("--snapshot is only used with --transport local")
        experimental = {"transport": args.transport, "reasoning": args.reasoning is not False,
                        "max_tokens": args.max_tokens or 384, "snapshot": str(Path(args.snapshot).resolve()) if args.snapshot else None,
                        "api_key_env": args.api_key_env}
    rows = select_records(args.scope, args.image_id)
    models = BACKENDS if args.models == "both" else (args.models,)
    path = output_path(args.run_dir, args.scope)
    plan = make_plan(rows, models, args.repeat_validation)
    print(f"Selected {len(rows)} images; output: {path}")
    for backend, tasks in plan.items():
        location = ("Moondream Cloud (uploads image/prompt)" if args.transport == "cloud" else "local CUDA GPU") if experimental else "CPU"
        print(f"{backend}: {len(tasks)} inference calls on {location}; no automatic early stop")
    if experimental:
        print(f"Separate Moondream 3 comparison: reasoning={experimental['reasoning']}, max_tokens={experimental['max_tokens']}")
    else:
        print("Historical timings: about 158s/image Moondream and 392s/image SmolVLM2, plus loading.")
    if not args.execute:
        print("Plan only. Add --execute to run. No files or model downloads were created.")
        return
    path, success = run_inference(rows, models, path, args.repeat_validation, args.resume, experimental)
    print(f"\nRun directory: {path}\nNext: python 03_validate_outputs.py --run-dir \"{path}\"")
    if not success:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
