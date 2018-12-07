import pytest


def test_invalid_init_compression_type(custom_digest):
    with pytest.raises(TypeError):
        custom_digest(None)


def test_invalid_init_compression_value(custom_digest):
    with pytest.raises(ValueError):
        custom_digest(-1)


def test_invalid_insert_value_type(digest):
    with pytest.raises(TypeError):
        digest.insert(None)


def test_invalid_insert_weight_type(digest):
    with pytest.raises(TypeError):
        digest.insert(1.0, weight=None)


def test_invalid_insert_weight_value(digest):
    with pytest.raises(ValueError):
        digest.insert(1.0, weight=0)


def test_invalid_percentile_value_type(digest):
    with pytest.raises(TypeError):
        digest.percentile(None)


def test_invalid_quantile_value_higher(digest):
    with pytest.raises(ValueError):
        digest.quantile(1.0000001)


def test_invalid_quantile_value_lower(digest):
    with pytest.raises(ValueError):
        digest.quantile(-0.0000001)


def test_invalid_percentile_value_higher(digest):
    with pytest.raises(ValueError):
        digest.percentile(100.0000001)


def test_invalid_percentile_value_lower(digest):
    with pytest.raises(ValueError):
        digest.percentile(-0.0000001)


def test_invalid_cdf_value_type(digest):
    with pytest.raises(TypeError):
        digest.cdf(None)


def test_invalid_merge_other_type(digest):
    with pytest.raises(TypeError):
        digest.merge(None)
