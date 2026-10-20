"""From-scratch discrete-observation HMM in NumPy.

Companion code for README.md in this folder. Section numbers in the
docstrings refer to that guide.

Conventions
-----------
pi : (N,)    initial state distribution, pi[i] = P(z_1 = i)
A  : (N, N)  transition matrix, A[i, j] = P(z_t = j | z_{t-1} = i)
B  : (N, K)  emission matrix,   B[j, k] = P(x_t = k | z_t = j)
x  : (T,)    observations encoded as integers 0, ..., K-1
"""

import numpy as np


def forward(pi, A, B, x):
    """Scaled forward algorithm (Section 4.7).

    Returns
    -------
    alpha : (T, N) filtered posteriors, alpha[t] = P(z_t | x_{1:t})
    c     : (T,)   scaling factors, c[t] = P(x_t | x_{1:t-1});
            log P(x) = np.log(c).sum()
    """
    T, N = len(x), len(pi)
    alpha = np.zeros((T, N))
    c = np.zeros(T)
    alpha[0] = pi * B[:, x[0]]                       # pi_j * b_j(x_1)
    c[0] = alpha[0].sum()
    alpha[0] /= c[0]
    for t in range(1, T):
        alpha[t] = (alpha[t - 1] @ A) * B[:, x[t]]   # predict (alpha A), then update (* b)
        c[t] = alpha[t].sum()
        alpha[t] /= c[t]
    return alpha, c


def backward(A, B, x, c):
    """Scaled backward algorithm (Section 5.1), sharing forward's scaling factors.

    With this scaling, gamma = alpha * beta exactly (Section 9.2).
    """
    T, N = len(x), A.shape[0]
    beta = np.zeros((T, N))
    beta[-1] = 1.0
    for t in range(T - 2, -1, -1):
        beta[t] = (A @ (B[:, x[t + 1]] * beta[t + 1])) / c[t + 1]
    return beta


def viterbi(pi, A, B, x):
    """Log-space Viterbi (Chapter 6).

    Returns the most likely state path and its joint probability P(x, z*).
    """
    T, N = len(x), len(pi)
    with np.errstate(divide="ignore"):               # log(0) = -inf is fine here
        log_a, log_b, log_pi = np.log(A), np.log(B), np.log(pi)
    delta = log_pi + log_b[:, x[0]]
    psi = np.zeros((T, N), dtype=int)
    for t in range(1, T):
        scores = delta[:, None] + log_a              # scores[i, j]: move from i to j
        psi[t] = scores.argmax(axis=0)               # backpointers
        delta = scores.max(axis=0) + log_b[:, x[t]]
    path = [int(delta.argmax())]
    for t in range(T - 1, 0, -1):
        path.append(int(psi[t, path[-1]]))
    return path[::-1], float(np.exp(delta.max()))


def baum_welch(x, N, K, n_iter=200, tol=1e-8, seed=0):
    """Baum-Welch / EM for a single sequence (Chapter 7).

    Returns (pi, A, B, log_likelihood).
    """
    rng = np.random.default_rng(seed)
    pi = rng.dirichlet(np.ones(N))
    A = rng.dirichlet(np.ones(N), size=N)
    B = rng.dirichlet(np.ones(K), size=N)
    x = np.asarray(x)
    prev = -np.inf
    ll = prev
    for _ in range(n_iter):
        # E-step
        alpha, c = forward(pi, A, B, x)
        beta = backward(A, B, x, c)
        ll = np.log(c).sum()
        gamma = alpha * beta                                          # (T, N)
        xi = (alpha[:-1, :, None] * A[None]                           # (T-1, N, N)
              * (B[:, x[1:]].T * beta[1:])[:, None, :]) / c[1:, None, None]
        # M-step: ratios of expected counts
        pi = gamma[0]
        A = xi.sum(0) / gamma[:-1].sum(0)[:, None]
        B = np.stack([gamma[x == k].sum(0) for k in range(K)], axis=1) / gamma.sum(0)[:, None]
        if ll - prev < tol:
            break
        prev = ll
    return pi, A, B, ll


def sample(pi, A, B, T, rng=None):
    """Draw (observations, states) of length T from the generative process (Section 3.1).

    Reference solution for the sampler exercise in Section 9.4.
    """
    rng = np.random.default_rng(rng)
    xs = np.zeros(T, dtype=int)
    zs = np.zeros(T, dtype=int)
    z = rng.choice(len(pi), p=pi)
    for t in range(T):
        zs[t] = z
        xs[t] = rng.choice(B.shape[1], p=B[z])
        z = rng.choice(len(pi), p=A[z])
    return xs, zs


if __name__ == "__main__":
    pi = np.array([0.6, 0.4])
    A = np.array([[0.8, 0.2], [0.3, 0.7]])
    B = np.array([[0.1, 0.9], [0.7, 0.3]])   # rows: Active, Cold; cols: no login, login
    x = [1, 0, 0]                            # Login, No login, No login

    alpha, c = forward(pi, A, B, x)
    beta = backward(A, B, x, c)
    print("P(x)            ", round(float(np.prod(c)), 6))
    print("filtered Active ", alpha[:, 0].round(3))
    print("smoothed Active ", (alpha * beta)[:, 0].round(3))
    print("viterbi         ", viterbi(pi, A, B, x))
    print("day-4 state dist", (alpha[-1] @ A).round(3))

    xs, _ = sample(pi, A, B, 5000, rng=42)
    pi_hat, A_hat, B_hat, ll = baum_welch(xs, N=2, K=2, seed=1)
    print("learned A\n", A_hat.round(3))
    print("learned B\n", B_hat.round(3))
