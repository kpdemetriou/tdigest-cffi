/*
 * include/tdigest.c
 *
 * Copyright (c) 2016, Usman Masood <usmanm at fastmail dot fm>
 */

#ifndef TDIGEST_H
#define TDIGEST_H

struct Centroid {
    long long weight;
    double mean;
};

struct Point {
    double value;
    long long weight;
    struct Point *next;
};

struct TDigest {
    unsigned int compression;
    int threshold;
    long long size;

    long long weight;
    double min;
    double max;

    unsigned int point_count;
    struct Point *points;

    unsigned int centroid_count;
    struct Centroid *centroids;

    unsigned int compression_count;
};

extern struct TDigest *tdigest_new(unsigned int compression);
extern void tdigest_add(struct TDigest *digest, double value, long long weight);
extern void tdigest_merge(struct TDigest *digest1, struct TDigest *digest2);
extern double tdigest_cdf(struct TDigest *digest, double value);
extern double tdigest_quantile(struct TDigest *digest, double quantile);
extern void tdigest_compress(struct TDigest *digest);
extern void tdigest_free(struct TDigest *digest);

#endif /* TDIGEST_H */
