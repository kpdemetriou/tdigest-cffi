from collections import namedtuple
from readerwriterlock.rwlock import RWLockWrite
from ._tdigest import lib as _lib

DEFAULT_COMPRESSION = 400

Centroid = namedtuple("Centroid", ("weight", "mean"))


class RawTDigest:
    def __init__(self, compression=DEFAULT_COMPRESSION):
        if not isinstance(compression, int):
            raise TypeError("'compression' must be of type 'int'")

        if compression <= 0:
            raise ValueError("'compression' must larger than 0")

        self._struct = _lib.tdigest_new(compression)

    def __del__(self):
        if hasattr(self, "_struct"):
            _lib.tdigest_free(self._struct)

    def _compress(self):
        _lib.tdigest_compress(self._struct)

    @property
    def compression(self):
        return self._struct.compression

    @property
    def threshold(self):
        return self._struct.threshold

    @property
    def size(self):
        return self._struct.size

    @property
    def weight(self):
        if self._struct.point_count:
            self._compress()

        return self._struct.weight

    @property
    def centroid_count(self):
        if self._struct.point_count:
            self._compress()

        return self._struct.centroid_count

    @property
    def compression_count(self):
        return self._struct.compression_count

    def insert(self, value, weight=1):
        if not isinstance(value, (float, int)):
            raise TypeError("'value' must be of type 'float' or 'int'")

        if not isinstance(weight, int):
            raise TypeError("'weight' must be of type 'int'")

        if weight <= 0:
            raise ValueError("'weight' must larger than 0")

        _lib.tdigest_add(self._struct, value, weight)

    def quantile(self, value):
        if not isinstance(value, float):
            raise TypeError("'value' must be of type 'float'")

        if value < 0.0 or value > 1.0:
            raise ValueError("'value' must be between 0.00 and 1.00")

        return _lib.tdigest_quantile(self._struct, value)

    def percentile(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("'value' must be of type 'float' or 'int'")

        if value < 0 or value > 100:
            raise ValueError("'value' must be between 0 and 100")

        return _lib.tdigest_quantile(self._struct, value / 100)

    def cdf(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("'value' must be of type 'float' or 'int'")

        return _lib.tdigest_cdf(self._struct, value)

    def centroids(self):
        for i in range(self.centroid_count):
            centroid = self._struct.centroids[i]
            yield Centroid(centroid.weight, centroid.mean)

    def merge(self, other):
        if not isinstance(other, (TDigest, RawTDigest)):
            raise TypeError("'value' must be of type 'TDigest' or 'RawTDigest'")

        _lib.tdigest_merge(self._struct, other._struct)


class TDigest(RawTDigest):
    def __init__(self, compression=DEFAULT_COMPRESSION):
        super().__init__(compression)
        self._lock = RWLockWrite()

    @property
    def compression(self):
        with self._lock.gen_rlock():
            return super().compression

    @property
    def threshold(self):
        with self._lock.gen_rlock():
            return super().threshold

    @property
    def size(self):
        with self._lock.gen_rlock():
            return super().size

    @property
    def weight(self):
        with self._lock.gen_wlock():
            return super().weight

    @property
    def centroid_count(self):
        with self._lock.gen_wlock():
            return super().centroid_count

    @property
    def compression_count(self):
        with self._lock.gen_rlock():
            return super().compression_count

    def insert(self, value, weight=1):
        with self._lock.gen_wlock():
            return super().insert(value, weight)

    def quantile(self, value):
        with self._lock.gen_wlock():
            return super().quantile(value)

    def percentile(self, value):
        with self._lock.gen_wlock():
            return super().percentile(value)

    def cdf(self, value):
        with self._lock.gen_wlock():
            return super().cdf(value)

    def centroids(self):
        with self._lock.gen_wlock():
            return super().centroids()

    def merge(self, other):
        with self._lock.gen_wlock():
            return super().merge(other)
