import pandas as pd

from features import BINARY_FEATURES, FEATURES, TARGET
from make_dataset import BOUNDS, SOURCE, expand


def test_expand_produces_valid_rows():
    source = pd.read_csv(SOURCE)
    out = expand(source, rows=1000, seed=0)

    assert len(out) == 1000
    assert list(out.columns) == FEATURES + [TARGET, "source_id"]
    assert out.isna().sum().sum() == 0
    for col in BINARY_FEATURES + [TARGET]:
        assert set(out[col].unique()) <= {0, 1}
    for col, (low, high, _) in BOUNDS.items():
        assert out[col].between(low, high).all(), col
    assert out["source_id"].between(0, len(source) - 1).all()


def test_expand_is_deterministic():
    source = pd.read_csv(SOURCE)
    pd.testing.assert_frame_equal(expand(source, 500, seed=7), expand(source, 500, seed=7))
