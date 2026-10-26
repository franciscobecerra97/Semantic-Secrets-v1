"""Step 5: evaluator examples with artificial answers, without loading any model."""
import argparse
from audit_common import teaching_examples

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="New directory under manual_validation/p9-v2/outputs")
    args = parser.parse_args()
    teaching_examples(args.output)

if __name__ == "__main__":
    main()
