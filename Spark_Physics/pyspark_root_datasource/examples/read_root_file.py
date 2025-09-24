#!/usr/bin/env python3
"""
read_root_file.py

Example: Read a ROOT file (TTrees/NanoAOD-like) via PySpark using the
'pyspark-root-datasource' (uproot + awkward + pyarrow under the hood).

Notes:
- To fetch the 2 GB example file locally, use one of:
    xrdcp root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root .
  or (HTTP copy):
    wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012BC_DoubleMuParked_Muons.root

Usage examples:

  # Local file
  python read_root_file.py --path ./Run2012BC_DoubleMuParked_Muons.root --tree Events --limit 5

  # XRootD (requires Python XRootD installed)
  python read_root_file.py \
    --path root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root \
    --tree Events --limit 5

"""

from pyspark.sql import SparkSession
from pyspark_root_datasource import register
import argparse
import sys


def parse_args():
    p = argparse.ArgumentParser(
        description="Read a ROOT TTree into a Spark DataFrame and show a few rows."
    )
    p.add_argument(
        "--path",
        default="./Run2012BC_DoubleMuParked_Muons.root",
        help="Input ROOT file path or URL (supports local paths and root:// over XRootD).",
    )
    p.add_argument(
        "--tree",
        default="Events",
        help="TTree/RNTuple name to read (default: Events).",
    )
    p.add_argument(
        "--schema",
        default="",
        help=("Optional Spark schema string to prune branches early. "
              "Example: \"nMuon int, Muon_pt array<float>, Muon_eta array<float>\""),
    )
    p.add_argument(
        "--infer-schema",
        action="store_true",
        help="Infer schema from the file (slower and loads metadata for all branches).",
    )
    p.add_argument(
        "--step-size",
        default="1000000",
        help="Partition step size (entries per batch read by uproot). Default: 1000000.",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of rows to show (df.show). Set 0 to skip showing.",
    )
    p.add_argument(
        "--count",
        action="store_true",
        default=True,
        help="Compute df.count() (full scan). On by default.",
    )
    p.add_argument(
        "--repartition",
        type=int,
        default=0,
        help="Optional: Repartition the DataFrame to N partitions (0 = no change).",
    )
    return p.parse_args()


def main():
    args = parse_args()

    spark = (SparkSession.builder
             .appName("Read ROOT via PySpark + uproot")
             .getOrCreate())
    try:
        # Register datasource short name = "root"
        register(spark)

        reader = (spark.read.format("root")
                  .option("tree", args.tree)
                  .option("step_size", str(args.step_size)))

        # Schema: either explicit (recommended) or inferred
        if args.schema:
            reader = reader.schema(args.schema)
        elif args.infer_schema:
            reader = reader.option("inferSchema", "true")

        # Load
        df = reader.load(args.path)

        # Optional repartition for downstream compute balance
        if args.repartition and args.repartition > 0:
            df = df.repartition(args.repartition)

        # Show schema and a small sample
        print(f"\n==> Loaded path: {args.path}")
        print(f"==> Tree: {args.tree}")
        print("==> DataFrame schema:")
        df.printSchema()

        if args.limit and args.limit > 0:
            print(f"\n==> Showing first {args.limit} rows:")
            df.show(args.limit, truncate=False)

        # Count (full scan) only on request
        if args.count:
            cnt = df.count()
            print("\n==> Count:", cnt)

        print("\nOK.")
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
