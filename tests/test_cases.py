from random import random, randint, shuffle


def test_case_sequential(digest):
    for i in range(10_000):
        digest.insert(i)

    error = 0

    for i in range(100):
        expected = (i + 1) * 10_000 / 100
        error += abs(digest.quantile((i + 1) / 100) - expected) / expected

    assert 1 / 100 > error / 100
    error = 0

    for i in range(100):
        expected = (i + 1) * 10_000 / 100
        error += abs(digest.percentile(i + 1) - expected) / expected

    assert 1 / 100 > error / 100
    error = 0

    for i in range(10_000):
        error += abs(digest.cdf(i) - i / 10_000)

    assert 1 / 100 > error / 10_000


def test_case_medley(seed, digest):
    candidates = [i % 10_000 for i in range(20_000)]
    shuffle(candidates)

    for i in range(10_000):
        digest.insert(candidates[i])

    error = 0

    for i in range(100):
        expected = (i + 1) * 10_000 / 100
        error += abs(digest.quantile((i + 1) / 100) - expected) / expected

    assert 1 / 100 > error / 100
    error = 0

    for i in range(100):
        expected = (i + 1) * 10_000 / 100
        error += abs(digest.percentile(i + 1) - expected) / expected

    assert 1 / 100 > error / 100
    error = 0

    for i in range(10_000):
        error += abs(digest.cdf(i) - i / 10_000)

    assert 1 / 100 > error / 10_000


def test_case_random(seed, digest):
    for i in range(10_000):
        digest.insert(random())

    error = 0

    for i in range(100):
        expected = (i + 1) / 100
        error += abs(digest.quantile((i + 1) / 100) - expected) / expected

    assert 1 / 50 > error / 100
    error = 0

    for i in range(100):
        expected = (i + 1) / 100
        error += abs(digest.percentile(i + 1) - expected) / expected

    assert 1 / 50 > error / 100
    error = 0

    for i in range(9998):
        expected = (i + 1) / 10_000
        error += abs(digest.cdf(expected) - expected)

    assert 1 / 100 > error / 9998


def test_identical(digest):
    value = randint(1, 10_000)

    for i in range(10_000):
        digest.insert(value)

    error = 0

    for i in range(101):
        error += abs(digest.quantile(i / 100) - value) / value

    assert 1 / 50 > error / 100
    error = 0

    for i in range(101):
        error += abs(digest.percentile(i) - value) / value

    assert 1 / 50 > error / 100
    error = 0

    for i in range(10_000):
        expected = 0 if (i + 1) < value else 1
        error += abs(digest.cdf(i + 1) - expected)

    assert 1 / 100 > error / 10_000
