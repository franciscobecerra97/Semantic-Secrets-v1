"""Step 3: revalidate saved predictions and compare them with reference facts."""
import argparse
from audit_common import validate_run

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--scope", choices=("all", "development", "validation"), default="all",
                        help="Filter planned images in this run; cannot invent missing splits")
    args = parser.parse_args()
    validate_run(args.run_dir, args.scope)

if __name__ == "__main__":
    main()
