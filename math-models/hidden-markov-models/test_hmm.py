"""Checks hmm.py against every hand-computed number in README.md."""

import numpy as np
import pytest

from hmm import backward, baum_welch, forward, sample, viterbi

PI = np.array([0.6, 0.4])
A = np.array([[0.8, 0.2], [0.3, 0.7]])
B = np.array([[0.1, 0.9], [0.7, 0.3]])   # rows: Active, Cold; cols: no login, login
X = [1, 0, 0]                            # Login, No login, No login


def test_sequence_probability():          # Section 4.5
    _, c = forward(PI, A, B, X)
    assert np.prod(c) == pytest.approx(0.080184)


def test_filtering():                     # Section 4.5
    alpha, _ = forward(PI, A, B, X)
    assert alpha[:, 0] == pytest.approx([0.8182, 0.2583, 0.0970], abs=1e-4)


def test_smoothing():                     # Section 5.4
    alpha, c = forward(PI, A, B, X)
    gamma = alpha * backward(A, B, X, c)
    assert gamma.sum(axis=1) == pytest.approx(np.ones(3))
    assert gamma[:, 0] == pytest.approx([0.6088, 0.1284, 0.0970], abs=1e-4)


def test_viterbi():                       # Section 6.3
    path, p = viterbi(PI, A, B, X)
    assert path == [0, 1, 1]
    assert p == pytest.approx(0.037044)


def test_prediction():                    # Section 8.3
    alpha, _ = forward(PI, A, B, X)
    nxt = alpha[-1] @ A
    assert nxt == pytest.approx([0.3485, 0.6515], abs=1e-4)
    assert nxt @ B[:, 1] == pytest.approx(0.5091, abs=1e-4)


def test_brute_force_matches_forward():   # Exercise 3
    x = [1, 1]
    brute = sum(
        PI[z1] * B[z1, x[0]] * A[z1, z2] * B[z2, x[1]]
        for z1 in range(2) for z2 in range(2)
    )
    _, c = forward(PI, A, B, x)
    assert brute == pytest.approx(0.4788)
    assert np.prod(c) == pytest.approx(brute)


def test_baum_welch_recovers_parameters():  # Section 9.4
    xs, _ = sample(PI, A, B, 5000, rng=42)
    _, A_hat, B_hat, _ = baum_welch(xs, N=2, K=2, seed=1)
    order = np.argsort(B_hat[:, 1])[::-1]    # align labels: Active = higher P(login)
    assert B_hat[order, 1] == pytest.approx([0.9, 0.3], abs=0.08)
    assert np.diag(A_hat[np.ix_(order, order)]) == pytest.approx([0.8, 0.7], abs=0.08)
