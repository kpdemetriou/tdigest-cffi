t-digest CFFI
=============

`t-digest <https://github.com/tdunning/t-digest>`__ is a data structure
for accurate on-line accumulation of rank-based statistics such as
quantiles and trimmed means, designed by `Ted
Dunning <https://github.com/tdunning>`__.

The t-digest construction algorithm uses a variant of 1-dimensional
k-means clustering to produce a data structure that is related to the
Q-digest. This t-digest data structure can be used to estimate quantiles
or compute other rank statistics. The advantage of the t-digest over the
Q-digest is that the t-digest can handle floating point values while the
Q-digest is limited to integers. With small changes, the t-digest can
handle any values from any ordered set that has something akin to a
mean. The accuracy of quantile estimates produced by t-digests can be
orders of magnitude more accurate than those produced by Q-digests in
spite of the fact that t-digests are more compact when stored on disk.

This package provides tested, performant, thread-safe **Python 3** CFFI
bindings to an adapted implementation of t-digest by `Usman
Masood <https://github.com/usmanm>`__ originally written for
`redis-tdigest <https://github.com/usmanm/redis-tdigest>`__.

Installation
============

You can install this package using ``pip`` or the included ``setup.py``
script:

::

   # Using pip
   pip install tdigest-cffi

   # Using setup.py
   python setup.py install

Usage
=====

.. code:: python

   from tdigest import TDigest, RawTDigest

   # Thread-safe instance with default compression factor
   digest = TDigest()

   # Raw instance with default compression factor
   digest = RawTDigest()

   # Thread-safe instance with a custom compression factor
   digest = TDigest(compression=500)

   # Digest compression
   compression = digest.compression

   # Digest weight
   weight = digest.weight

   # Centroid count
   centroid_count = digest.centroid_count

   # Compression count
   compression_count = digest.compression_count

   # Insertion with unit weight
   digest.insert(1000)

   # Insertion with custom weight
   digest.insert(1000, 2)

   # 99th percentile calculation
   quantile = digest.quantile(0.99)
   percentile = digest.percentile(99)

   # Cumulative distribution function
   cdf = digest.cdf(1000)  # P(X <= 1000)

   # Centroid extraction
   for centroid in digest.centroids():
       print(centroid.mean, centroid.weight)

   # Digest merging
   other = TDigest()
   other.insert(42)
   digest.merge(other)

License
=======

.. code:: text

   BSD 3-Clause License

   Copyright (c) 2018, Phil Demetriou
   All rights reserved.

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   * Redistributions of source code must retain the above copyright notice, this
     list of conditions and the following disclaimer.

   * Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.

   * Neither the name of the copyright holder nor the names of its
     contributors may be used to endorse or promote products derived from
     this software without specific prior written permission.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
