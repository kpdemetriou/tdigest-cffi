/*
 * src/tdigest.c
 *
 * Implementation of the t-digest data structure used to compute accurate percentiles.
 *
 * It is based on the MergingDigest implementation found at:
 *   https://github.com/tdunning/t-digest/blob/master/src/main/java/com/tdunning/math/stats/MergingDigest.java
 *
 * Copyright (c) 2016, Usman Masood <usmanm at fastmail dot fm>
 */

#define _USE_MATH_DEFINES

#include "math.h"
#include <float.h>
#include <stdlib.h>
#include <string.h>

#include "tdigest.h"

#define INTERPOLATE(x, x0, x1) (((x) - (x0)) / ((x1) - (x0)))
#define INTEGRATED_LOCATION(compression, q) ((compression) * (asin(2 * (q) - 1) + M_PI / 2) / M_PI)
#define FLOAT_EQ(f1, f2) (fabs((f1) - (f2)) <= FLT_EPSILON)

#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))

struct MergeArgs {
    struct TDigest *digest;
    struct Centroid *centroids;
    int idx;
    double weight_so_far;
    double k1;
    double min;
    double max;
};

struct TDigest *tdigest_new(unsigned int compression) {
    struct TDigest *digest = calloc(1, sizeof(struct TDigest));

    digest->compression = compression;
    digest->size = ceil(compression * M_PI / 2) + 1;
    digest->threshold = 7.5 + 0.37 * compression - 2e-4 * pow(compression, 2);
    digest->min = INFINITY;

    return digest;
}

static int centroid_cmp(const void *a, const void *b) {
    struct Centroid *c1 = (struct Centroid *) a;
    struct Centroid *c2 = (struct Centroid *) b;

    if (c1->mean < c2->mean)
        return -1;
    if (c1->mean > c2->mean)
        return 1;

    return 0;
}

static void merge_centroid(struct MergeArgs *args, struct Centroid *merge) {
    double k2;
    struct Centroid *c = &args->centroids[args->idx];

    args->weight_so_far += merge->weight;
    k2 = INTEGRATED_LOCATION(args->digest->compression,
            args->weight_so_far / args->digest->weight);

    if (k2 - args->k1 > 1 && c->weight > 0) {
        args->idx++;
        args->k1 = INTEGRATED_LOCATION(args->digest->compression,
                (args->weight_so_far - merge->weight) / args->digest->weight);
    }

    c = &args->centroids[args->idx];
    c->weight += merge->weight;
    c->mean += (merge->mean - c->mean) * merge->weight / c->weight;

    if (merge->weight > 0) {
        args->min = MIN(merge->mean, args->min);
        args->max = MAX(merge->mean, args->max);
    }
}

void tdigest_compress(struct TDigest *digest) {
    struct Centroid *unmerged_centroids;
    long long unmerged_weight = 0;
    unsigned int unmerged_count = digest->point_count;
    unsigned int old_centroid_count = digest->centroid_count;
    unsigned int i, j;
    struct MergeArgs args;

    if (!digest->point_count)
        return;

    unmerged_centroids = malloc(sizeof(struct Centroid) * digest->point_count);

    for (i = 0; i < unmerged_count; i++) {
        struct Point *p = digest->points;
        struct Centroid *c = &unmerged_centroids[i];

        c->mean = p->value;
        c->weight = p->weight;

        unmerged_weight += c->weight;

        digest->points = p->next;
        free(p);
    }

    digest->point_count = 0;
    digest->weight += unmerged_weight;

    qsort(unmerged_centroids, unmerged_count, sizeof(struct Centroid), centroid_cmp);
    memset(&args, 0, sizeof(struct MergeArgs));

    args.centroids = malloc(sizeof(struct Centroid) * digest->size);
    memset(args.centroids, 0, sizeof(struct Centroid) * digest->size);

    args.digest = digest;
    args.min = INFINITY;

    i = 0;
    j = 0;
    while (i < unmerged_count && j < digest->centroid_count) {
        struct Centroid *a = &unmerged_centroids[i];
        struct Centroid *b = &digest->centroids[j];

        if (a->mean <= b->mean) {
            merge_centroid(&args, a);
            i++;
        } else {
            merge_centroid(&args, b);
            j++;
        }
    }

    while (i < unmerged_count)
        merge_centroid(&args, &unmerged_centroids[i++]);

    free(unmerged_centroids);

    while (j < digest->centroid_count)
        merge_centroid(&args, &digest->centroids[j++]);

    if (digest->weight > 0) {
        digest->min = MIN(digest->min, args.min);

        if (args.centroids[args.idx].weight <= 0)
            args.idx--;

        digest->centroid_count = args.idx + 1;
        digest->max = MAX(digest->max, args.max);
    }

    if (digest->centroid_count > old_centroid_count) {
        digest->centroids = realloc(digest->centroids,
                sizeof(struct Centroid) * digest->centroid_count);
    }

    memcpy(digest->centroids, args.centroids, sizeof(struct Centroid) * digest->centroid_count);
    free(args.centroids);

    digest->compression_count++;
}

void tdigest_add(struct TDigest *digest, double value, long long weight) {
    if (weight == 0)
        return;

    struct Point *p = malloc(sizeof(struct Point));

    p->value = value;
    p->weight = weight;
    p->next = digest->points;

    digest->points = p;
    digest->point_count++;

    if ((double) digest->point_count > digest->threshold)
        tdigest_compress(digest);
}

double tdigest_cdf(struct TDigest *digest, double value) {
    if (digest == NULL)
        return 0;

    unsigned int i;
    double left, right;
    long long weight_so_far;
    struct Centroid *a, *b, tmp;

    tdigest_compress(digest);

    if (digest->centroid_count == 0)
        return NAN;

    if (value < digest->min)
        return 0;
    if (value > digest->max)
        return 1;

    if (digest->centroid_count == 1) {
        if (FLOAT_EQ(digest->max, digest->min))
            return 0.5;

        return INTERPOLATE(value, digest->min, digest->max);
    }

    weight_so_far = 0;
    a = b = &tmp;
    b->mean = digest->min;
    b->weight = 0;
    right = 0;

    for (i = 0; i < digest->centroid_count; i++) {
        struct Centroid *c = &digest->centroids[i];

        left = b->mean - (a->mean + right);
        a = b;
        b = c;
        right = (b->mean - a->mean) * a->weight / (a->weight + b->weight);

        if (value < a->mean + right) {
            double cdf = weight_so_far + a->weight * INTERPOLATE(value, a->mean - left, a->mean + right);
            cdf /= digest->weight;
            return MAX(cdf, 0.0);
        }

        weight_so_far += a->weight;
    }

    left = b->mean - (a->mean + right);
    a = b;
    right = digest->max - a->mean;

    if (value < a->mean + right)
        return (weight_so_far
                + a->weight * INTERPOLATE(value, a->mean - left, a->mean + right))
                / digest->weight;

    return 1;
}

double tdigest_quantile(struct TDigest *digest, double quantile) {
    if (digest == NULL)
        return 0;

    unsigned int i;
    double left, right, idx;
    long long weight_so_far;
    struct Centroid *a, *b, tmp;

    tdigest_compress(digest);

    if (digest->centroid_count == 0)
        return NAN;

    if (digest->centroid_count == 1)
        return digest->centroids[0].mean;

    if (FLOAT_EQ(quantile, 0.0))
        return digest->min;

    if (FLOAT_EQ(quantile, 1.0))
        return digest->max;

    idx = quantile * digest->weight;

    weight_so_far = 0;
    b = &tmp;
    b->mean = digest->min;
    b->weight = 0;
    right = digest->min;

    for (i = 0; i < digest->centroid_count; i++) {
        struct Centroid *c = &digest->centroids[i];
        a = b;
        left = right;

        b = c;
        right = (b->weight * a->mean + a->weight * b->mean)
                / (a->weight + b->weight);

        if (idx < weight_so_far + a->weight) {
            double p = (idx - weight_so_far) / a->weight;
            return left * (1 - p) + right * p;
        }

        weight_so_far += a->weight;
    }

    left = right;
    a = b;
    right = digest->max;

    if (idx < weight_so_far + a->weight) {
        double p = (idx - weight_so_far) / a->weight;
        return left * (1 - p) + right * p;
    }

    return digest->max;
}

void tdigest_merge(struct TDigest *digest1, struct TDigest *digest2) {
    unsigned int i = digest2->point_count;
    struct Point *p = digest2->points;

    while (i) {
        tdigest_add(digest1, p->value, p->weight);
        p = p->next;
        i--;
    }

    for (i = 0; i < digest2->centroid_count; i++) {
        tdigest_add(digest1, digest2->centroids[i].mean, digest2->centroids[i].weight);
    }
}

void tdigest_free(struct TDigest *digest) {
    while (digest->points) {
        struct Point *p = digest->points;
        digest->points = digest->points->next;
        free(p);
    }

    if (digest->centroids)
        free(digest->centroids);

    free(digest);
}
