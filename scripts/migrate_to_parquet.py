#!/usr/bin/env python3
"""
Migrate SQLite database to Parquet format with train/val/test splits.
"""

import argparse
import sqlite3
from pathlib import Path
from typing import Tuple

import pandas as pd


def load_data_from_db(db_path: str = "data/prompts.db") -> pd.DataFrame:
    """Load all data from SQLite database."""
    conn = sqlite3.connect(db_path)

    # Read all data into DataFrame
    df = pd.read_sql_query("SELECT id, text, is_injection FROM prompts", conn)
    conn.close()

    # Convert boolean column
    df["is_injection"] = df["is_injection"].astype(bool)

    print(f"Loaded {len(df)} records from {db_path}")
    print(f"Data shape: {df.shape}")
    print(f"Injection rate: {df['is_injection'].mean():.2%}")

    return df


def split_data(
    df: pd.DataFrame, train_ratio: float = 0.8, val_ratio: float = 0.1
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split data into train, validation, and test sets."""
    # Shuffle the data
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Calculate split sizes
    n_total = len(df_shuffled)
    n_train = int(train_ratio * n_total)
    n_val = int(val_ratio * n_total)

    # Split the data
    train_df = df_shuffled.iloc[:n_train]
    val_df = df_shuffled.iloc[n_train : n_train + n_val]
    test_df = df_shuffled.iloc[n_train + n_val :]

    print("\nSplit statistics:")
    print(f"  Train: {len(train_df)} samples ({len(train_df) / n_total:.1%})")
    print(f"  Validation: {len(val_df)} samples ({len(val_df) / n_total:.1%})")
    print(f"  Test: {len(test_df)} samples ({len(test_df) / n_total:.1%})")

    # Check class distribution
    for name, split_df in [
        ("Train", train_df),
        ("Validation", val_df),
        ("Test", test_df),
    ]:
        injection_rate = split_df["is_injection"].mean()
        print(f"  {name} injection rate: {injection_rate:.2%}")

    return train_df, val_df, test_df


def save_to_parquet(df: pd.DataFrame, filepath: Path) -> None:
    """Save DataFrame to Parquet format."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(filepath, index=False)
    print(f"Saved {len(df)} records to {filepath}")
    print(f"  File size: {filepath.stat().st_size / 1024 / 1024:.2f} MB")


def validate_migration(original_db_path: str, parquet_paths: dict) -> bool:
    """Validate that migration preserved all data."""
    print("\n" + "=" * 60)
    print("Validating migration...")

    # Load original data
    conn = sqlite3.connect(original_db_path)
    original_df = pd.read_sql_query("SELECT id, text, is_injection FROM prompts", conn)
    conn.close()

    # Load only the full dataset for validation (not the splits)
    full_parquet_df = pd.read_parquet(parquet_paths["full"])

    # Check counts
    original_count = len(original_df)
    parquet_count = len(full_parquet_df)

    print(f"Original database records: {original_count}")
    print(f"Parquet full dataset records: {parquet_count}")

    if original_count != parquet_count:
        print(f"❌ Record count mismatch: {original_count} vs {parquet_count}")
        return False

    # Check unique IDs
    original_ids = set(original_df["id"])
    parquet_ids = set(full_parquet_df["id"])

    if original_ids != parquet_ids:
        missing_in_parquet = original_ids - parquet_ids
        extra_in_parquet = parquet_ids - original_ids
        print("❌ ID mismatch:")
        print(f"  Missing in parquet: {len(missing_in_parquet)} IDs")
        print(f"  Extra in parquet: {len(extra_in_parquet)} IDs")
        return False

    # Check data integrity - compare sorted by ID
    original_sorted = original_df.sort_values("id").reset_index(drop=True)
    parquet_sorted = full_parquet_df.sort_values("id").reset_index(drop=True)

    # Compare text column
    if not original_sorted["text"].equals(parquet_sorted["text"]):
        print("❌ Text data mismatch")
        # Find first mismatch
        for i in range(min(len(original_sorted), len(parquet_sorted))):
            if original_sorted.iloc[i]["text"] != parquet_sorted.iloc[i]["text"]:
                print(f"  First mismatch at index {i}:")
                print(f"    Original: {original_sorted.iloc[i]['text'][:50]}...")
                print(f"    Parquet: {parquet_sorted.iloc[i]['text'][:50]}...")
                break
        return False

    # Compare is_injection column
    if not original_sorted["is_injection"].equals(parquet_sorted["is_injection"]):
        print("❌ is_injection data mismatch")
        return False

    print("✅ Migration validation passed!")
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate SQLite database to Parquet format"
    )
    parser.add_argument(
        "--db", type=str, default="data/prompts.db", help="Input SQLite database path"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Output directory for parquet files",
    )
    parser.add_argument(
        "--train-ratio", type=float, default=0.8, help="Training set ratio"
    )
    parser.add_argument(
        "--val-ratio", type=float, default=0.1, help="Validation set ratio"
    )
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip validation step"
    )

    args = parser.parse_args()

    # Convert to Path objects
    db_path = Path(args.db)
    output_dir = Path(args.output_dir)

    if not db_path.exists():
        print(f"Error: Database file not found: {db_path}")
        return 1

    print("=" * 60)
    print("Starting migration from SQLite to Parquet")
    print("=" * 60)

    # Step 1: Load data from SQLite
    print("\nStep 1: Loading data from SQLite database...")
    df = load_data_from_db(str(db_path))

    # Step 2: Split data
    print("\nStep 2: Splitting data...")
    train_df, val_df, test_df = split_data(df, args.train_ratio, args.val_ratio)

    # Step 3: Save to Parquet
    print("\nStep 3: Saving to Parquet format...")

    # Define output paths
    parquet_paths = {
        "full": output_dir / "prompts.parquet",
        "train": output_dir / "train.parquet",
        "val": output_dir / "val.parquet",
        "test": output_dir / "test.parquet",
    }

    # Save full dataset
    save_to_parquet(df, parquet_paths["full"])

    # Save splits
    save_to_parquet(train_df, parquet_paths["train"])
    save_to_parquet(val_df, parquet_paths["val"])
    save_to_parquet(test_df, parquet_paths["test"])

    # Step 4: Validate migration
    if not args.skip_validation:
        if not validate_migration(str(db_path), parquet_paths):
            print("❌ Migration validation failed!")
            return 1

    # Step 5: Create backup of original database
    backup_path = db_path.with_suffix(".db.backup")
    import shutil

    shutil.copy2(db_path, backup_path)
    print(f"\nCreated backup of original database: {backup_path}")

    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    for name, path in parquet_paths.items():
        size_mb = path.stat().st_size / 1024 / 1024
        print(f"  {name:10} -> {path} ({size_mb:.2f} MB)")

    print(f"\nOriginal database backed up to: {backup_path}")
    print("\nNext steps:")
    print("1. Update config/settings.py with new parquet paths")
    print("2. Update detector.py to use load_data_from_parquet()")
    print("3. Update any other scripts that use the database")
    print("4. Test the system with the new parquet files")

    return 0


if __name__ == "__main__":
    exit(main())
