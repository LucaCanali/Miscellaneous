#!/usr/bin/env python3
"""
10046_connector.py — Convert Oracle 10046 (SQL trace) WAIT lines to PyLatencyMap records (cumulative)
Author: Luca.Canali@cern.ch  |  Modernized for Python 3

Emits *cumulative* power-of-two bucket counts so LatencyMap.py can compute per-interval deltas.
"""

import sys
import math
import time
import argparse
import re
from typing import Dict, Optional

WAIT_RE = re.compile(
    r"^WAIT\s+#.*?\b(?:nam|name)='(?P<name>[^']+)'.*?\bela=\s*(?P<ela>\d+)\b.*?\btim=\s*(?P<tim>\d+)\b",
    re.IGNORECASE,
)

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Connector: Oracle 10046 trace → PyLatencyMap (cumulative histogram records)"
    )
    p.add_argument("-e", "--event", default="db file sequential read",
                   help='Wait event name to include (default: "db file sequential read")')
    p.add_argument("-i", "--interval", type=float, default=3.0,
                   help="Sampling interval in seconds (default: 3.0)")
    p.add_argument("--case-sensitive", action="store_true",
                   help="Match event name case-sensitively (default: case-insensitive)")
    return p.parse_args(argv)

class RunningHistogram:
    """Cumulative power-of-two histogram with Oracle-style bucketting (floor(log2(µs)) + 1)."""
    def __init__(self) -> None:
        self.totals: Dict[int, int] = {}

    def add_us(self, value_us: int) -> None:
        if value_us <= 0:
            return
        bucket = int(math.log2(value_us)) + 1
        self.totals[bucket] = self.totals.get(bucket, 0) + 1

    def emit_record(self, ts_usecs: int, label: str, out=sys.stdout) -> None:
        print("<begin record>", file=out)
        for b in sorted(self.totals):
            print(f"{2**b},{self.totals[b]}", file=out)
        human_ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts_usecs / 1_000_000))
        print(f"timestamp,microsec,{ts_usecs}, {human_ts}", file=out)
        print(f"label,{label}", file=out)
        print("latencyunit,microsec", file=out)
        print("datasource,oracle", file=out)  # use Oracle intensity convention
        print("<end record>", file=out)
        out.flush()

def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    event_filter = args.event if args.case_sensitive else args.event.lower()
    interval_us = int(args.interval * 1_000_000)

    hist = RunningHistogram()
    window_start: Optional[int] = None

    for raw in sys.stdin:
        line = raw.strip()
        if not line.startswith("WAIT"):
            continue
        m = WAIT_RE.match(line)
        if not m:
            continue

        name = m.group("name")
        ela_us = int(m.group("ela"))
        tim_us = int(m.group("tim"))

        name_cmp = name if args.case_sensitive else name.lower()
        if name_cmp != event_filter:
            continue

        # Align to interval window
        sample_bucket = tim_us - (tim_us % interval_us)
        if window_start is None:
            window_start = sample_bucket

        # New window → emit cumulative so far (no reset!), then advance window
        if sample_bucket > window_start:
            hist.emit_record(window_start, f"10046 trace data for event: {args.event}")
            window_start = sample_bucket
        elif sample_bucket < window_start:
            raise RuntimeError(f"Out-of-order timestamp: {sample_bucket} < {window_start}")

        # Accumulate into cumulative totals
        hist.add_us(ela_us)

    # EOF: emit final snapshot if we ever saw data
    if window_start is not None:
        hist.emit_record(window_start, f"10046 trace data for event: {args.event}")
    else:
        # no data — still emit an empty frame to keep downstream happy
        empty = RunningHistogram()
        ts = int(time.time() * 1_000_000)
        empty.emit_record(ts, f"10046 trace data for event: {args.event}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

