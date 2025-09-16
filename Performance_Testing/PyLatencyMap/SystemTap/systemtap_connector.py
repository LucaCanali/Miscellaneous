#!/usr/bin/env python3
"""
systemtap_connector.py — Normalize SystemTap @hist_log output for PyLatencyMap
Author: Luca.Canali@cern.ch (original, 2013)

Purpose
  Read SystemTap histogram output (e.g. @hist_log from block I/O probes) from stdin and
  convert lines into the "<power_of_two_value>,<count>" pairs expected by PyLatencyMap.
  Record/frame tags and metadata lines are passed through unchanged.

Usage
  stap -v SystemTap/blockio_rq_latency.stp \
  | python3 SystemTap/systemtap_connector.py \
  | python3 LatencyMap.py

Notes
  - This connector assumes the SystemTap script already prints records delimited by:
      <begin record> ... <end record>
    and includes metadata lines like:
      timestamp,microsec,....
      latencyunit,microsec
      label,....
      datasource,systemtap
  - Lines like "value | ***** count" from @hist_log are normalized to "value,count".
  - Lines with "~" (histogram blanks), headers ("value"), and debug identifiers are ignored.
  - Zero/negative buckets are dropped as a workaround for some VM/clock artifacts.
"""

from __future__ import annotations
import re
import sys


def normalize_hist_line(line: str) -> str | None:
    """
    Convert a SystemTap @hist_log line to "value,count".
    Example:
      "   64 |@@@@@@  15"  -> "64,15"
      "  128 |@@@     7"   -> "128,7"
    Returns None if the line should be skipped.
    """
    s = line.strip()
    if not s:
        return None
    # Skip @hist_log blanks and headers
    if s.startswith("~") or "value" in s:
        return None
    # Remove spaces, bars, and '@' bar marks: "64|@@@@10" -> "64,10"
    s = s.replace(" ", "").replace("@", "").replace("|", ",")
    # Some scripts prefix histogram with identifiers like "myhistogram[...]"
    if "myhistogram" in s:
        return None
    # After normalization we expect "<num>,<num>"
    if not re.match(r"^-?\d+,-?\d+$", s):
        return None
    # Filter zero/negative latency buckets (workaround for stap/dtrace on some VMs)
    if s.startswith("-") or s.startswith("0,"):
        return None
    return s


def main() -> int:
    try:
        for raw in sys.stdin:
            line = raw.rstrip("\n")

            if not line:
                continue

            # Pass-through record structure and known metadata lines as-is
            if line.startswith("<begin record>"):
                print("<begin record>")
                continue
            if line.startswith("<end record>"):
                print("<end record>")
                sys.stdout.flush()
                continue
            if line.startswith(("timestamp", "datasource", "label", "latencyunit")):
                print(line)
                continue

            # Try to normalize a histogram line
            norm = normalize_hist_line(line)
            if norm is None:
                continue
            print(norm)

    except BrokenPipeError:
        # Downstream closed the pipe (e.g., viewer exited) — exit quietly
        try:
            sys.stdout.close()
        finally:
            return 0

    except KeyboardInterrupt:
        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
