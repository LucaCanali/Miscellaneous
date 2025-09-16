#!/usr/bin/env python3

"""
LatencyMap.py — CLI heat maps for latency histograms
Version: 1.3 (Sep 2025)
Author: Luca.Canali@cern.ch
License: Apache v2.0 (see LICENSE)

Overview
  Render two scrolling terminal heat maps from streaming latency histograms:
    • Frequency  — events/sec per latency bucket (IOPS-like)
    • Intensity  — time waited per sec (unit/sec; left-axis labels shown in ms)

Input format (unchanged)
  Stream **tagged** records to stdin; buckets are base-2 upper bounds with **cumulative counts**.
    <begin record>
    timestamp,microsec,<epoch_usecs>,<human_readable_ts>
    latencyunit,<millisec|microsec|nanosec>
    label,<free text>
    datasource,<bpf|systemtap|dtrace|oracle>
    <power_of_two_value>,<cumulative_count>
    ...
    <end record>

  Notes:
    - 'latencyunit' applies to bucket values; Y-axis labels are always rendered in **ms**.
    - Counts must be cumulative per bucket; the tool computes per-interval deltas → rates.
    - Intensity approximation depends on 'datasource':
        oracle    ≈ 0.75 * bucket_value * waits
        bpf       ≈ 1.50 * bucket_value * waits
        systemtap ≈ 1.50 * bucket_value * waits
        dtrace    ≈ 1.50 * bucket_value * waits

CLI (see --help)
  --num_records INT       Number of columns (time window). Default: 90
  --min_bucket INT        Lower bucket exponent (log2). -1 = autotune
  --max_bucket INT        Upper bucket exponent (log2). 64 = autotune
  --frequency_maxval F    Fix frequency color scale max; -1 = auto
  --intensity_maxval F    Fix intensity color scale max; -1 = auto
  --screen_delay FLOAT    Delay between frames (sec). Default: 0.1
  --debug_level INT       Verbosity 0..5. Default: 0

Examples
  # From a live source
  data_source | latencymap --num_records=120

  # Module invocation
  data_source | python -m LatencyMap -n 120

  # Replay sample data
  cat SampleData/example_latency_data.txt | latencymap --screen_delay=0.2

Requirements
  Python 3.x and a terminal with ANSI color support.
"""

from __future__ import annotations
import sys
import argparse
import math
import time
from typing import Dict, List

# ----------------------------- Parameters & CLI ----------------------------- #

class GlobalParameters:
    """
    Global parameters parsed from CLI, with sensible defaults
    """
    def __init__(self) -> None:
        # Chart/window width (time axis)
        self.num_latency_records: int = 90

        # Buckets are log2(power-of-two value in the given latency unit).
        # -1 means autotune min; 64 was used as a sentinel for autotune max.
        self.min_latency_bkt: int = -1  # lower bucket (log2)
        self.max_latency_bkt: int = 64  # upper bucket (log2), 64 => autotune

        # Auto scaling for colors unless overridden (>0 to fix scale)
        self.frequency_maxval: float = -1
        self.intensity_maxval: float = -1

        self.debug_level: int = 0
        self.print_legend: bool = True
        self.frequency_map: bool = True
        self.intensity_map: bool = True

        # Delay between frames (useful when replaying traces)
        self.screen_delay: float = 0.1

        # Unit of incoming bucket values (impacts labels & autotune min)
        # Valid: 'millisec', 'microsec', 'nanosec'
        self.latency_unit: str = 'millisec'

        # Tags/string constants (unchanged)
        self.begin_tag: str = '<begin record>'
        self.end_tag: str = '<end record>'
        self.latencyunit_tag: str = 'latencyunit'
        self.label_tag: str = 'label'
        self.label_data_source: str = 'datasource'
        self.default_data_source: str = 'bpf'  # bpf, systemtap, dtrace, oracle

    def parse_cli(self, argv: list[str] | None = None) -> None:
        parser = argparse.ArgumentParser(
            prog="LatencyMap.py",
            description="Plot CLI heatmaps (frequency & intensity) from latency histograms."
        )
        parser.add_argument("--num_records", "-n", type=int, default=self.num_latency_records,
                            help="Number of time intervals displayed (default: 90).")
        parser.add_argument("--min_bucket", type=int, default=self.min_latency_bkt,
                            help="Lower bucket exponent (log2). -1 = autotune (default).")
        parser.add_argument("--max_bucket", type=int, default=self.max_latency_bkt,
                            help="Upper bucket exponent (log2). 64 = autotune (default).")
        parser.add_argument("--frequency_maxval", type=float, default=self.frequency_maxval,
                            help="Max color scale for frequency map; -1 = auto (default).")
        parser.add_argument("--intensity_maxval", type=float, default=self.intensity_maxval,
                            help="Max color scale for intensity map; -1 = auto (default).")
        parser.add_argument("--screen_delay", type=float, default=self.screen_delay,
                            help="Delay (sec) between screens (default: 0.1).")
        parser.add_argument("--debug_level", "-d", type=int, default=self.debug_level,
                            help="Debug level 0..5 (default: 0).")

        # Parse provided argv or default to sys.argv[1:]
        args = parser.parse_args(argv)

        self.num_latency_records = args.num_records
        self.min_latency_bkt = args.min_bucket
        self.max_latency_bkt = args.max_bucket
        self.frequency_maxval = -1 if args.frequency_maxval is None else args.frequency_maxval
        self.intensity_maxval = -1 if args.intensity_maxval is None else args.intensity_maxval
        self.screen_delay = args.screen_delay
        self.debug_level = args.debug_level

    def usage_banner(self) -> None:
        print("LatencyMap.py v1.3 - Luca.Canali@cern.ch")
        print("CLI heatmaps for latency histograms (frequency & intensity).")

g_params = GlobalParameters()  # Initialized in __main__

# --------------------------- Data types & helpers --------------------------- #

class LatencyRecord:
    """
    One sampling record of latency data.
    Holds frequency & intensity histograms (buckets in log2 indices).
    """
    def __init__(self) -> None:
        # Raw data: exponent-> cumulative count at timestamp. Special keys: 'timestamp'
        self.data: Dict[int | str, int] = {}

        # Pre-allocate with a generous upper bound; safe even after autotune shrinks the range.
        self.frequency_histogram: List[float] = [0.0 for _ in range(0, 65)]
        self.intensity_histogram: List[float] = [0.0 for _ in range(0, 65)]

        self.delta_time: int = 0  # microseconds between this and previous record
        self.max_frequency: float = 0.0
        self.sum_frequency: float = 0.0
        self.max_intensity: float = 0.0
        self.sum_intensity: float = 0.0
        self.date: str = ''
        self.label: str = ''
        self.data_source: str = g_params.default_data_source

    # ---------------------- Input parsing & record IO ---------------------- #

    @staticmethod
    def _read_non_empty_line_lower_stripped() -> str:
        while True:
            line = sys.stdin.readline()
            if not line:
                print("\nReached EOF from data source, exiting.")
                sys.exit(0)
            line = line.strip()
            if line:
                return line.lower()

    def go_to_begin_record_tag(self) -> None:
        while True:
            if self._read_non_empty_line_lower_stripped() == g_params.begin_tag:
                return

    def read_record(self) -> None:
        while True:
            line = self._read_non_empty_line_lower_stripped()
            split_line = [x.strip() for x in line.split(",")]

            # End-of-record
            if len(split_line) == 1 and split_line[0] == g_params.end_tag:
                return

            # Header / meta lines
            if len(split_line) == 4 and split_line[0] == 'timestamp' and split_line[1] == 'microsec':
                self.data['timestamp'] = int(split_line[2])
                self.date = split_line[3]
                continue

            if len(split_line) == 2 and split_line[0] == g_params.label_tag:
                self.label = split_line[1]
                continue

            if len(split_line) == 2 and split_line[0] == g_params.label_data_source:
                self.data_source = split_line[1]
                continue

            if len(split_line) == 2 and split_line[0] == g_params.latencyunit_tag:
                unit = split_line[1]
                if unit not in ('millisec', 'microsec', 'nanosec'):
                    raise ValueError(f"Cannot understand latency unit in line: {line!r}")
                g_params.latency_unit = unit
                continue

            # Data lines: <power_of_two_value>,<count>
            if len(split_line) != 2:
                raise ValueError(f"Cannot process record line: {line!r}")

            try:
                power_of_two_val = int(split_line[0])
                count = int(split_line[1])
                bucket = math.log(power_of_two_val, 2.0)
            except Exception as exc:
                raise ValueError(f"Cannot parse data line: {line!r} ({exc})") from exc

            if abs(int(bucket) - bucket) > 1e-6:
                raise ValueError(f"Bucket value must be a power of 2: {line!r}")
            bucket = int(bucket)

            # Keep cumulative count for this exponent bucket
            self.data[bucket] = self.data.get(bucket, 0) + count

    # ----------------------- Computations & autotune ----------------------- #

    @staticmethod
    def _autotune_latency_buckets() -> None:
        """
        Compute min/max buckets for the heatmap window on first record.
        - For microsecond inputs (typical), default min is 2^7 µs (128 µs).
        - Display still uses milliseconds for the left axis labels.
        """
        if g_params.min_latency_bkt == -1:
            g_params.min_latency_bkt = {
                'millisec': 0,   # 1 ms
                'microsec': 7,   # 128 µs (v1.3 default)
                'nanosec': 17,   # 131,072 ns (~0.131 ms)
            }[g_params.latency_unit]

        if g_params.max_latency_bkt == 64:
            # ~12 buckets vertically by default (min .. min+11)
            g_params.max_latency_bkt = g_params.min_latency_bkt + 11

    def compute_deltas(self, previous: 'LatencyRecord') -> None:
        # timestamp delta (usec); convert to seconds for rates
        self.delta_time = self.data.get('timestamp', 0) - previous.data.get('timestamp', 0)
        time_factor = self.delta_time / 1e6 if self.delta_time > 0 else 1.0

        for bucket in list(self.data.keys()):
            if bucket == 'timestamp':
                continue

            write_bucket = bucket
            if bucket > g_params.max_latency_bkt:
                write_bucket = g_params.max_latency_bkt
            if bucket < g_params.min_latency_bkt:
                write_bucket = g_params.min_latency_bkt

            delta_count = self.data.get(bucket, 0) - previous.data.get(bucket, 0)
            # Frequency: events per second
            self.frequency_histogram[write_bucket] += (delta_count / time_factor)

            # Intensity: approximate time waited per second
            # Oracle histograms bucket differently vs BPF/SystemTap/DTrace (factor-of-2 difference).
            # Oracle: ~ 3/4 * bucket_value * waits; ST/DTrace: ~ 3/2 * bucket_value * waits
            if self.data_source == 'oracle':
                self.intensity_histogram[write_bucket] += (0.75 * delta_count * (2 ** bucket)) / time_factor
            elif self.data_source in ('bpf', 'systemtap', 'dtrace'):
                self.intensity_histogram[write_bucket] += (1.5 * delta_count * (2 ** bucket)) / time_factor
            else:
                raise ValueError("Invalid datasource. Use one of: bpf, systemtap, dtrace, oracle.")

        self.max_frequency = max(self.frequency_histogram[g_params.min_latency_bkt:g_params.max_latency_bkt + 1])
        self.sum_frequency = sum(self.frequency_histogram[g_params.min_latency_bkt:g_params.max_latency_bkt + 1])
        self.max_intensity = max(self.intensity_histogram[g_params.min_latency_bkt:g_params.max_latency_bkt + 1])
        self.sum_intensity = sum(self.intensity_histogram[g_params.min_latency_bkt:g_params.max_latency_bkt + 1])


class ArrayOfLatencyRecords:
    """
    Holds the scrolling window (time axis) of LatencyRecord objects.
    """
    BLUE_PALETTE = {0: 15, 1: 51, 2: 45, 3: 39, 4: 33, 5: 27, 6: 21}    # white→deep blue bg
    RED_PALETTE = {0: 15, 1: 226, 2: 220, 3: 214, 4: 208, 5: 202, 6: 196}  # white→red bg
    ESC_RESET = "\x1b[0m"

    def __init__(self) -> None:
        self.sample_number: int = 0
        # IMPORTANT: create distinct empty records (no shared reference)
        self.data: List[LatencyRecord] = [LatencyRecord() for _ in range(0, g_params.num_latency_records + 1)]

    # ------------------------------- Debug -------------------------------- #

    def print_frequency_histograms_debug(self) -> None:
        print('\nFrequency histograms:')
        for record in self.data:
            print(record.frequency_histogram, record.delta_time)

    def print_intensity_histograms_debug(self) -> None:
        print('\nIntensity histograms:')
        for record in self.data:
            print(record.intensity_histogram, record.delta_time)

    # ------------------------------ Charting ------------------------------ #

    def add_new_record(self, record: LatencyRecord) -> None:
        # Scroll window: discard oldest, append newest
        self.data = self.data[1:] + [record]
        self.sample_number += 1

    @staticmethod
    def _bg_color(token: int, palette: str) -> str:
        if palette == 'blue':
            c = ArrayOfLatencyRecords.BLUE_PALETTE[token]
        elif palette == 'red':
            c = ArrayOfLatencyRecords.RED_PALETTE[token]
        else:
            raise ValueError("palette must be 'blue' or 'red'")
        return f"\x1b[48;5;{c}m"

    @staticmethod
    def _fmt_value(v: float) -> str:
        if v < 0:
            return "0"
        if v <= 9:
            return f"{v:.1g}"
        if v < 1_000_000:
            return str(int(round(v)))
        return f"{v:.2g}"

    @staticmethod
    def _bucket_ms_label(bucket_exp: int) -> str:
        """
        Render the bucket upper bound as milliseconds for the left axis.
        - Always display in ms.
        - For <1ms: show with leading dot, e.g., .512
        - For >=1ms: show integer without leading dot: 1, 2, 4, 8, ...
        - Top line uses >prev, bottom uses <current (collapsed).
        """
        # Convert the bucket exponent (in given unit) to microseconds first
        # then to milliseconds for display.
        if g_params.latency_unit == 'millisec':
            usec = (2 ** bucket_exp) * 1000.0
        elif g_params.latency_unit == 'microsec':
            usec = float(2 ** bucket_exp)
        else:  # 'nanosec'
            usec = (2 ** bucket_exp) / 1000.0

        ms = usec / 1000.0
        if ms < 1.0:
            # Round to 3 decimals in base-2 friendly steps (.512, .256, ...)
            # The input steps already are powers of two ⇒ a simple format works
            s = f"{ms:.3f}".lstrip("0")
            return s
        else:
            # For 1, 2, 4, 8, ... show as integer without trailing .0
            # (safe because steps are exact powers of two)
            return str(int(round(ms)))

    def _print_header(self) -> None:
        if g_params.debug_level < 2:
            # Clear screen & home cursor
            print("\x1b[0m\x1b[2J\x1b[H", end="")
        print("LatencyMap.py v1.3 - Luca.Canali@cern.ch")

    def _print_footer(self) -> None:
        total_intensity = sum(r.sum_intensity for r in self.data)
        total_frequency = sum(r.sum_frequency for r in self.data)
        last = self.data[-1]

        total_avg = (total_intensity / total_frequency) if total_frequency > 0 else 0.0
        latest_avg = (last.sum_intensity / last.sum_frequency) if last.sum_frequency > 0 else 0.0

        # Note: display average in the configured latency unit string (kept from v1.2 behavior)
        print(f"Average latency: {self._fmt_value(total_avg)} {g_params.latency_unit}. "
              f"Average latency of latest values: {self._fmt_value(latest_avg)} {g_params.latency_unit}")

        print(f"Sample num: {self.sample_number}. "
              f"Delta time: {round(last.delta_time/1e6, 1)} sec. "
              f"Date: {last.date.upper()}")
        if last.label:
            print(f"Label: {last.label}")

    def _print_heat_map(self, chart_type: str) -> None:
        assert chart_type in ('Frequency', 'Intensity')
        if chart_type == 'Frequency':
            params_maxval = g_params.frequency_maxval
            palette = 'blue'
            chart_maxval = max(r.max_frequency for r in self.data)
            title = 'Frequency Heatmap: events per sec'
            unit = '(N#/sec)'
        else:
            params_maxval = g_params.intensity_maxval
            palette = 'red'
            chart_maxval = max(r.max_intensity for r in self.data)
            title = 'Intensity Heatmap: time waited per sec'
            unit = f"({g_params.latency_unit}/sec)"

        # Header line
        left_axis_title = "Latency bucket"
        line = left_axis_title.ljust(max(16, g_params.num_latency_records // 2 - 10))
        line += title
        line = line.ljust(g_params.num_latency_records + 2)
        line += "Latest values"
        if g_params.print_legend:
            line += "    Legend"
        print(line)

        line = "(millisec)".ljust(max(16, g_params.num_latency_records - len(unit) + 14))
        line += unit
        print(line)

        # Determine color scale
        max_val = chart_maxval if params_maxval == -1 else params_maxval

        # Main map
        row_idx = -1
        for bucket in range(g_params.max_latency_bkt, g_params.min_latency_bkt - 1, -1):
            row_idx += 1

            # Left axis label
            if bucket == g_params.max_latency_bkt:
                label = ">" + self._bucket_ms_label(bucket - 1)
            elif bucket == g_params.min_latency_bkt:
                label = "<" + self._bucket_ms_label(bucket)
            else:
                label = self._bucket_ms_label(bucket)
            line = label.rjust(6, ' ') + ' '

            # Heat row: oldest→newest (left→right). Newest column is the RIGHT-most.
            data_point = 0.0
            for record in self.data:
                if chart_type == 'Frequency':
                    data_point = record.frequency_histogram[bucket]
                else:
                    data_point = record.intensity_histogram[bucket]

                if data_point == 0:
                    token = 0
                elif data_point >= max_val:
                    token = 6
                else:
                    token = int(data_point * 6 / max_val) + 1

                if g_params.debug_level >= 2:
                    line += f"{token}:{data_point}, "
                else:
                    line += self._bg_color(token, palette) + ' '  # colored block

            # Latest value (right margin)
            line += self.ESC_RESET + self._fmt_value(data_point).rjust(7, '.')

            # Legend on the far right
            if g_params.print_legend:
                if row_idx <= 6:
                    line += '    ' + self._bg_color(row_idx, palette) + ' ' + self.ESC_RESET + ' '
                    display_val = 0 if row_idx == 0 else int(max_val * (row_idx - 1) / 6)
                    line += ('0' if row_idx == 0 else '>' + self._fmt_value(display_val))
                elif row_idx == 7:
                    line += '    ' + 'Max: ' + self._fmt_value(chart_maxval)
                elif row_idx == (g_params.max_latency_bkt - g_params.min_latency_bkt):
                    line += '    ' + 'Max(Sum):'
            print(line)

        # Footer line under the heatmap
        last = self.data[-1]
        line = '      '
        if chart_type == 'Frequency':
            line += 'x=time, y=latency bucket (ms), color=wait frequency (IOPS)'
            line = line.ljust(g_params.num_latency_records + 3)
            line += 'Sum:' + self._fmt_value(last.sum_frequency).rjust(7, '.')
            max_sum = max(r.sum_frequency for r in self.data)
            line += '    ' + self._fmt_value(max_sum)
        else:
            line += 'x=time, y=latency bucket (ms), color=time waited'
            line = line.ljust(g_params.num_latency_records + 3)
            line += 'Sum:' + self._fmt_value(last.sum_intensity).rjust(7, '.')
            max_sum = max(r.sum_intensity for r in self.data)
            line += '    ' + self._fmt_value(max_sum)
        print(line + '\n')

    # ------------------------------- Public -------------------------------- #

    def render(self) -> None:
        self._print_header()
        if g_params.frequency_map:
            self._print_heat_map('Frequency')
        if g_params.intensity_map:
            self._print_heat_map('Intensity')
        self._print_footer()


# --------------------------------- Main ------------------------------------ #

def main(argv: list[str] | None = None) -> int:
    # Parse CLI first so -h/--help works via console script entry point
    g_params.parse_cli(argv)
    # Show banner after successful parse (won't print on -h because argparse exits first)
    g_params.usage_banner()
    chart = ArrayOfLatencyRecords()
    first = True
    previous = LatencyRecord()  # dummy previous for first delta computation

    while True:
        rec = LatencyRecord()
        rec.go_to_begin_record_tag()
        try:
            rec.read_record()
        except Exception as err:
            sys.stderr.write(f"ERROR: {err}\n")
            return 1

        if g_params.debug_level >= 2:
            print("\nLatest data record:")
            print(rec.data)

        if first:
            LatencyRecord._autotune_latency_buckets()
            first = False
        else:
            rec.compute_deltas(previous)

        chart.add_new_record(rec)
        previous = rec

        chart.render()
        time.sleep(g_params.screen_delay)

        if g_params.debug_level >= 3:
            chart.print_frequency_histograms_debug()
        if g_params.debug_level >= 4:
            chart.print_intensity_histograms_debug()


if __name__ == '__main__':
    sys.exit(main())
