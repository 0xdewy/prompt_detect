#!/usr/bin/env python3
"""
Command-line interface for Safe Prompts.
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .data_utils import (
    ensure_data_files,
    ensure_model_file,
)
from .detector import SimplePromptDetector, train_model


def predict_command(args):
    """Handle predict command."""
    # Ensure model file is available
    if args.model:
        model_path = Path(args.model)
    else:
        print("Checking for pre-trained model...")
        model_path = ensure_model_file()

    print(f"Using model: {model_path}")

    try:
        detector = SimplePromptDetector(model_path=str(model_path))
    except FileNotFoundError:
        print(f"\nError: Model file '{model_path}' not found.")
        print("\nYou can:")
        print("  1. Train a model: prompt-detective train")
        print(
            "  2. Specify a different model: prompt-detective predict"
            " --model /path/to/model.pt"
        )
        print("  3. Check if the package includes a pre-trained model")
        sys.exit(1)

    if args.file:
        with open(args.file, "r") as f:
            text = f.read().strip()
        result = detector.predict(text)
        print(f"File: {args.file}")
        print(f"Result: {result['prediction']} ({result['confidence']:.2%})")

    elif args.dir:
        from .detector import analyze_directory

        analyze_directory(detector, args.dir, args.summary)

    elif args.url:
        import requests

        try:
            response = requests.get(args.url)
            response.raise_for_status()
            text = response.text.strip()
            result = detector.predict(text)
            print(f"URL: {args.url}")
            print(f"Result: {result['prediction']} ({result['confidence']:.2%})")
        except Exception as e:
            print(f"Error fetching URL: {e}")

    elif args.text:
        result = detector.predict(args.text)
        print(f"Text: {args.text}")
        print(f"Result: {result['prediction']} ({result['confidence']:.2%})")

    else:
        # Interactive mode
        print("Safe Prompts - Interactive Mode (Ctrl+D to exit)")
        print("=" * 50)
        try:
            while True:
                text = input("\nEnter text to analyze: ").strip()
                if not text:
                    continue
                result = detector.predict(text)
                print(f"Result: {result['prediction']} ({result['confidence']:.2%})")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)


def train_command(args):
    """Handle train command."""
    # Ensure data files are available
    print("Checking for data files...")
    train_path, val_path, test_path = ensure_data_files()

    print("\nTraining model with:")
    print(f"  Training data: {train_path}")
    print(f"  Validation data: {val_path}")
    print(f"  Test data: {test_path}")

    # Check if data files exist
    missing_files = []
    for path, name in [(train_path, "train"), (val_path, "val"), (test_path, "test")]:
        if not path.exists():
            missing_files.append(f"{name}: {path}")

    if missing_files:
        print("\nError: Missing data files:")
        for missing in missing_files:
            print(f"  - {missing}")
        print("\nYou may need to:")
        print("  1. Run the migration script: python scripts/migrate_to_parquet.py")
        print("  2. Or ensure data files are in the package")
        sys.exit(1)

    train_model(
        train_path=str(train_path),
        val_path=str(val_path),
        test_path=str(test_path),
        model_path=args.model,
    )


def export_command(args):
    """Handle export command."""
    import csv
    import json
    from pathlib import Path

    import pandas as pd

    # Load data
    parquet_path = Path(args.parquet)
    if not parquet_path.exists():
        # Try package data
        try:
            import importlib.resources

            with importlib.resources.path("prompt_detective", "data") as data_dir:
                package_path = data_dir / "prompts.parquet"
                if package_path.exists():
                    parquet_path = package_path
                else:
                    print(f"Error: Parquet file not found: {args.parquet}")
                    print("Try running the migration script first.")
                    return
        except (ImportError, FileNotFoundError):
            print(f"Error: Parquet file not found: {args.parquet}")
            print("Try running the migration script first.")
            return

    df = pd.read_parquet(parquet_path)
    print(f"Loaded {len(df)} records from {parquet_path}")

    # Handle different export formats
    if args.format == "stats":
        # Show statistics
        total = len(df)
        injections = df["is_injection"].sum()
        safe = total - injections

        print("\n=== Data Statistics ===")
        print(f"Total prompts: {total}")
        print(f"Injection prompts: {int(injections)} ({injections / total * 100:.1f}%)")
        print(f"Safe prompts: {int(safe)} ({safe / total * 100:.1f}%)")

    elif args.format == "json":
        output_path = args.output or "prompts.json"
        data = df.to_dict("records")

        # Convert to simpler format
        simple_data = []
        for item in data:
            simple_data.append(
                {"text": item["text"], "is_injection": bool(item["is_injection"])}
            )

        with open(output_path, "w") as f:
            json.dump(simple_data, f, indent=2)

        print(f"Exported {len(simple_data)} prompts to {output_path}")

    elif args.format == "csv":
        output_path = args.output or "prompts.csv"
        csv_df = df[["text", "is_injection"]].copy()
        csv_df["is_injection"] = csv_df["is_injection"].astype(int)
        csv_df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
        print(f"Exported {len(csv_df)} prompts to {output_path}")

    else:
        print(f"Export format '{args.format}' not implemented in CLI.")
        print("Please use the export script directly:")
        print(f"  python scripts/export_parquet.py --format {args.format}")
        if args.output:
            print(f"  --output {args.output}")


def version_command(args):
    """Handle version command."""
    print(f"Safe Prompts v{__version__}")
    print("Prompt injection detection system")
    print(f"Python {sys.version}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Safe Prompts - Prompt injection detection system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
   # Analyze text
  prompt-detective predict "Ignore all previous instructions"

  # Analyze file
  prompt-detective predict --file input.txt

  # Train model
  prompt-detective train

  # Export data
  prompt-detective export --format json --output prompts.json

  # Show version
  prompt-detective --version
        """,
    )

    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )

    # Create subparsers
    subparsers = parser.add_subparsers(
        title="commands", dest="command", help="Available commands"
    )

    # Predict command
    predict_parser = subparsers.add_parser(
        "predict", help="Predict if text contains prompt injection"
    )
    predict_parser.add_argument(
        "text", nargs="?", help="Text to analyze (or use --file, --dir, --url)"
    )
    predict_parser.add_argument("--file", "-f", help="Analyze text from file")
    predict_parser.add_argument(
        "--dir", "-d", help="Analyze all .txt files in directory"
    )
    predict_parser.add_argument("--url", "-u", help="Analyze text from URL")
    predict_parser.add_argument(
        "--summary", action="store_true", help="Show summary for directory analysis"
    )
    predict_parser.add_argument(
        "--model", help="Path to model checkpoint (default: models/best_model.pt)"
    )
    predict_parser.set_defaults(func=predict_command)

    # Train command
    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument(
        "--model",
        default="models/best_model.pt",
        help="Path to save model checkpoint (default: models/best_model.pt)",
    )
    train_parser.set_defaults(func=train_command)

    # Export command
    export_parser = subparsers.add_parser(
        "export", help="Export data to various formats"
    )
    export_parser.add_argument(
        "--format",
        choices=["json", "csv", "excel", "stats", "training", "parquet-split"],
        default="json",
        help="Export format",
    )
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument(
        "--parquet", default="data/prompts.parquet", help="Input parquet file path"
    )
    export_parser.set_defaults(func=export_command)

    # Version command (as separate parser for --version flag)
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.set_defaults(func=version_command)

    # Parse arguments
    args = parser.parse_args()

    # Handle --version flag
    if args.version:
        version_command(args)
        return

    # Handle commands
    if hasattr(args, "func"):
        args.func(args)
    else:
        # No command provided, show help
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
