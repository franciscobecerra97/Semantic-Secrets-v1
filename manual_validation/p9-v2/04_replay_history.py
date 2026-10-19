"""Step 4: reproduce saved-answer validation and historical gate arithmetic; no inference."""
import argparse
from audit_common import output_path, replay_history

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="New directory under manual_validation/p9-v2/outputs")
    args = parser.parse_args()
    print(f"Saved-answer replay: {replay_history(output_path(args.output, 'historical-replay'))}")

if __name__ == "__main__":
    main()
