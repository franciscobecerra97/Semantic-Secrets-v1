"""Step 1: inspect images/labels/prompt; optionally recreate a drawing in isolation."""
import argparse
from audit_common import inspect_dataset

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-id", default="cap-v2-064")
    parser.add_argument("--output", help="New directory under manual_validation/p9-v2/outputs")
    parser.add_argument("--gallery", action="store_true", help="Create an offline gallery of all 96 references")
    parser.add_argument("--recreate", action="store_true", help="Render this one fixture again, keeping the original untouched")
    args = parser.parse_args()
    inspect_dataset(args.output, args.image_id, args.gallery, args.recreate)

if __name__ == "__main__":
    main()
