# tests/test_pyspark_root_datasource.py
import os
import warnings
import pytest
import pyarrow as pa

from pyspark_root_datasource._utils import (
    _parse_bool,
    _parse_int,
    expand_paths,
    cast_unsigned_to_signed,
    select_arrow_columns,
)

# -----------------------
# Unit tests (no Spark/ROOT required)
# -----------------------

@pytest.mark.parametrize(
    "val,default,expected",
    [
        ("true", False, True),
        ("False", True, False),
        ("YES", False, True),
        ("n", True, False),
        ("off", True, False),
        (None, True, True),
        ("unknown", True, True),
        ("", False, False),
    ],
)
def test_parse_bool_param(val, default, expected):
    assert _parse_bool(val, default) is expected


@pytest.mark.parametrize(
    "val,default,expected",
    [
        ("42", 0, 42),
        ("0", 7, 0),
        ("-7", None, -7),
        ("notint", 7, 7),
        (None, None, None),
    ],
)
def test_parse_int_param(val, default, expected):
    assert _parse_int(val, default) == expected


def test_expand_paths_glob_dir_and_ext(tmp_path):
    # Create sample files
    d = tmp_path / "data"
    (d).mkdir(parents=True, exist_ok=True)
    (d / "a.root").write_bytes(b"")
    (d / "b.root").write_bytes(b"")
    (d / "c.txt").write_bytes(b"")
    (d / "sub").mkdir(parents=True, exist_ok=True)
    (d / "sub" / "d.root").write_bytes(b"")

    # Directory expansion with default ext=*.root
    out = expand_paths(str(d), recursive=False, dir_ext="*.root")
    names = {os.path.basename(p) for p in out}
    assert {"a.root", "b.root"}.issubset(names)

    # Directory expansion with ext=".root" (normalize to "*.root")
    out2 = expand_paths(str(d), recursive=False, dir_ext=".root")
    names2 = {os.path.basename(p) for p in out2}
    assert {"a.root", "b.root"}.issubset(names2)

    # Recursive directory expansion
    out3 = expand_paths(str(d), recursive=True, dir_ext="*.root")
    names3 = {os.path.basename(p) for p in out3}
    assert {"a.root", "b.root", "d.root"}.issubset(names3)

    # Glob pattern
    out4 = expand_paths(str(d / "*.root"), recursive=False, dir_ext="*.root")
    names4 = {os.path.basename(p) for p in out4}
    assert names4 == {"a.root", "b.root"}

    # Comma-separated list
    out5 = expand_paths(f"{d/'a.root'},{d/'b.root'}", dir_ext="*.root")
    names5 = {os.path.basename(p) for p in out5}
    assert names5 == {"a.root", "b.root"}

    # Non-local scheme passes through unchanged
    out6 = expand_paths("root://example//path/file.root", dir_ext="*.root")
    assert out6 == ["root://example//path/file.root"]


def test_cast_unsigned_to_signed_scalar_list_struct_map_fixedsizelist():
    # Scalar uint
    a = pa.array([1, 2, 3], type=pa.uint32())

    # list<uint16>
    b = pa.array([[1, 2], [3], []], type=pa.list_(pa.uint16()))

    # struct with nested unsigned
    inner = pa.struct([("ku8", pa.uint8()), ("vi32", pa.int32())])
    c = pa.array([{"ku8": 1, "vi32": -1}, {"ku8": 2, "vi32": 0}, {"ku8": 3, "vi32": 1}], type=inner)

    # map<uint16, list<uint8>>
    map_ty = pa.map_(pa.uint16(), pa.list_(pa.uint8()))
    d = pa.array(
        [
            {1: [1, 2], 2: [3]},
            {7: []},
            {9: [4, 5]},
        ],
        type=map_ty,
    )

    # fixed_size_list<uint16>(3) with SAME ROW COUNT as other columns (3)
    e_vals = pa.array([1, 2, 3, 4, 5, 6, 7, 8, 9], type=pa.uint16())
    e = pa.FixedSizeListArray.from_arrays(e_vals, 3)

    tbl = pa.table({"u32": a, "l_u16": b, "s": c, "m": d, "fsl_u16": e})
    out = cast_unsigned_to_signed(tbl)

    # u32 -> int32
    assert out.schema.field("u32").type == pa.int32()

    # list<uint16> -> list<int16>
    ty_l = out.schema.field("l_u16").type
    assert pa.types.is_list(ty_l) and ty_l.value_type == pa.int16()

    # struct: ku8 -> int8, vi32 unchanged
    s_ty = out.schema.field("s").type
    assert pa.types.is_struct(s_ty)
    assert s_ty[0].name == "ku8" and s_ty[0].type == pa.int8()
    assert s_ty[1].name == "vi32" and s_ty[1].type == pa.int32()

    # map<uint16, list<uint8>> -> map<int16, list<int8>>
    m_ty = out.schema.field("m").type
    assert pa.types.is_map(m_ty)
    assert m_ty.key_type == pa.int16()
    assert pa.types.is_list(m_ty.item_type) and m_ty.item_type.value_type == pa.int8()

    # fixed_size_list<uint16>(3) -> fixed_size_list<int16>(3)
    fsl_ty = out.schema.field("fsl_u16").type
    assert pa.types.is_fixed_size_list(fsl_ty)
    assert fsl_ty.list_size == 3
    assert fsl_ty.value_type == pa.int16()


def test_select_arrow_columns_top_level_and_warn_on_dotted():
    tbl = pa.table({"a": pa.array([1, 2]), "b": pa.array([3, 4])})

    # top-level selection
    out = select_arrow_columns(tbl, ["b"])
    assert out.column_names == ["b"]

    # missing columns are ignored (warning expected)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out2 = select_arrow_columns(tbl, ["b", "z"])
        assert out2.column_names == ["b"]
        assert any("Ignoring missing columns" in str(ww.message) for ww in w)

    # dotted path warns and leaves the table unchanged (no top-level match)
    with warnings.catch_warnings(record=True) as w2:
        warnings.simplefilter("always")
        out3 = select_arrow_columns(tbl, ["a.x"])
        assert out3.column_names == tbl.column_names
        assert any("Nested column pruning is not yet supported" in str(ww.message) for ww in w2)


# -----------------------
# Integration tests (skipped if deps missing)
# -----------------------

try:
    import awkward as ak  # noqa: F401
    import numpy as np  # noqa: F401
    import uproot  # noqa: F401
    from pyspark_root_datasource.datasource import UprootDataSource
    HAVE_DEPS = True
except Exception:
    HAVE_DEPS = False

pytestmark = pytest.mark.skipif(not HAVE_DEPS, reason="needs uproot, awkward, and package import")


def _make_root_with_events(path):
    """
    Build a tiny ROOT file with TTree 'Events' containing:
      - u32 (uint32)
      - l_u16 (list<uint16>)   -- avoid None; use [] for missing
      - fsl_u16 (fixed-size list<uint16>(3))
    """
    import numpy as np
    import awkward as ak
    import uproot

    n = 10
    u32 = np.arange(n, dtype=np.uint32)

    # Use [] instead of None for uproot writer compatibility
    l_u16 = ak.Array([[1, 2], [3], [], [4, 5, 6], [7], [], [8, 9], [10], [], [11]])

    # fixed-size list via RegularArray (n rows, size 3)
    vals = np.arange(n * 3, dtype=np.uint16)
    fsl = ak.Array(vals.reshape(n, 3))  # RegularArray -> Arrow fixed_size_list

    with uproot.recreate(path) as f:
        f["Events"] = {"u32": u32, "l_u16": l_u16, "fsl_u16": fsl}


def test_schema_and_read_minimal_root(tmp_path):
    root_path = tmp_path / "mini.root"
    _make_root_with_events(root_path)

    ds = UprootDataSource(
        {
            "path": str(root_path),
            "tree": "Events",
            "step_size": 4,
            "cast_unsigned": "true",
            "list_to32": "true",
            "extensionarray": "false",
        }
    )

    # schema inference
    st = ds.schema()
    fields = {f.name: f.dataType for f in st.fields}
    assert {"u32", "l_u16", "fsl_u16"}.issubset(set(fields.keys()))

    # partitions
    rdr = ds.reader(st)
    parts = list(rdr.partitions())
    assert len(parts) == 3  # ceil(10 / 4) = 3

    # read all
    batches = []
    for p in parts:
        for rb in rdr.read(p):
            batches.append(rb)
    tbl = pa.Table.from_batches(batches)

    # unsigned cast checks
    assert tbl.schema.field("u32").type == pa.int32()
    assert pa.types.is_list(tbl.schema.field("l_u16").type)
    vt = tbl.schema.field("l_u16").type.value_type
    assert pa.types.is_integer(vt) and not pa.types.is_unsigned_integer(vt)
    fsl_ty = tbl.schema.field("fsl_u16").type
    assert pa.types.is_fixed_size_list(fsl_ty) and fsl_ty.value_type == pa.int16() and fsl_ty.list_size == 3
    assert tbl.num_rows == 10


def test_entry_bounds_and_num_partitions_override(tmp_path):
    root_path = tmp_path / "mini.root"
    _make_root_with_events(root_path)

    # entry_start/stop narrow to 6 rows; num_partitions=2 overrides step_size
    ds = UprootDataSource(
        {
            "path": str(root_path),
            "tree": "Events",
            "step_size": 1000000,
            "num_partitions": 2,
            "entry_start": 2,
            "entry_stop": 8,
        }
    )

    st = ds.schema()
    rdr = ds.reader(st)
    parts = list(rdr.partitions())
    assert len(parts) == 2
    spans = [(p.entry_start, p.entry_stop) for p in parts]
    assert spans == [(2, 5), (5, 8)]  # 6 rows split into 2 roughly equal parts

    # Read and verify row count
    batches = []
    for p in parts:
        batches.extend(list(rdr.read(p)))
    tbl = pa.Table.from_batches(batches)
    assert tbl.num_rows == 6


def test_cast_unsigned_disabled(tmp_path):
    root_path = tmp_path / "mini.root"
    _make_root_with_events(root_path)

    ds = UprootDataSource(
        {
            "path": str(root_path),
            "tree": "Events",
            "cast_unsigned": "false",   # leave uints in Arrow
            "step_size": 10,
        }
    )
    # Spark can't convert uint32 Arrow -> Spark; expect schema() to fail
    with pytest.raises(Exception) as ei:
        _ = ds.schema()
    assert "UNSUPPORTED_DATA_TYPE_FOR_ARROW_CONVERSION" in str(ei.value) or "not supported" in str(ei.value)


def test_error_tree_not_found_shows_keys(tmp_path):
    import uproot
    p = tmp_path / "bad.root"
    with uproot.recreate(p) as f:
        f["OtherTree"] = {"x": [1, 2, 3]}

    from pyspark_root_datasource.datasource import UprootDataSource
    ds = UprootDataSource({"path": str(p), "tree": "Events"})
    with pytest.raises(Exception) as ei:
        _ = ds.schema()
    msg = str(ei.value)
    assert "not found" in msg and "Available keys" in msg

