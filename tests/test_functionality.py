from random import randint


def test_init(custom_digest):
    custom_digest()


def test_init_raw(custom_digest):
    custom_digest(raw=True)


def test_compression(custom_digest):
    compression = randint(100, 1000)
    assert compression == custom_digest(compression).compression


def test_weight(digest):
    assert 0 == digest.weight

    digest.insert(1)
    assert 1 == digest.weight

    digest.insert(2, weight=2)
    assert 3 == digest.weight


def test_compression_count(digest):
    assert 0 == digest.compression_count

    for i in range(int(digest.threshold) + 1):
        digest.insert(i)

    assert 1 == digest.compression_count


def test_centroid_count(digest):
    assert 0 == digest.centroid_count

    digest.insert(1)
    assert 1 == digest.centroid_count


def test_quantile(digest):
    for i in range(100):
        digest.insert(i + 1)

    assert 99.5 <= digest.quantile(0.99) < 100.5


def test_percentile(digest):
    for i in range(100):
        digest.insert(i + 1)

    assert 99.5 <= digest.percentile(99) < 100.5


def test_cdf(digest):
    for i in range(100):
        digest.insert(i + 1)

    assert 0.985 <= digest.cdf(99) < 0.995


def test_centroids(digest):
    for i in range(100):
        digest.insert(i)

    centroid_count = 0

    for centroid in digest.centroids():
        assert isinstance(centroid.mean, float)
        assert isinstance(centroid.weight, int)
        assert 0 < centroid.weight
        centroid_count += 1

    assert 0 < centroid_count
    assert centroid_count == digest.centroid_count


def test_merge(custom_digest):
    primary = custom_digest()
    secondary = custom_digest()

    for i in range(1000):
        secondary.insert(i)

    assert 0 == primary.weight
    assert 1000 == secondary.weight

    primary.merge(secondary)
    assert 1000 == primary.weight
