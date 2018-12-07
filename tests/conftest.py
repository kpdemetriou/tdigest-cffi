import random
import pytest
import tdigest


@pytest.fixture(scope="function")
def seed():
    random.seed(0)


@pytest.fixture(scope="function")
def digest():
    return tdigest.TDigest()


@pytest.fixture(scope="session")
def custom_digest():
    def custom_digest_(compression=tdigest.DEFAULT_COMPRESSION, raw=False):
        return (tdigest.RawTDigest if raw else tdigest.TDigest)(compression)

    return custom_digest_
