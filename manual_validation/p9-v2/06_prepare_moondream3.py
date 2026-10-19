"""Optional local Moondream 3 snapshot preparation. Default is a no-download plan."""
import argparse
from moondream3_audit import MODEL_ID, MODEL_REVISION, TOKENIZER_ID, TOKENIZER_REVISION, prepare_snapshot

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="New snapshot directory under manual_validation/p9-v2/outputs")
    parser.add_argument("--download", action="store_true", help="Download ~18.5 GB of weights plus code/tokenizer; no inference")
    args = parser.parse_args()
    print(f"Model: {MODEL_ID}@{MODEL_REVISION}\nTokenizer: {TOKENIZER_ID}@{TOKENIZER_REVISION}")
    print("Local loading uses CUDA, bfloat16 and upstream FlexAttention compilation.")
    if args.download:
        print(f"Prepared snapshot: {prepare_snapshot(args.output)}")
    else:
        print("Plan only. No files, downloads or model execution. Use --download only for the local GPU route.")

if __name__ == "__main__":
    main()
