"""Classical counts diagnostic for QPU validation.

This module computes distribution-level metrics from observed QPU counts. It is
deliberately NOT an approximation of the von Neumann entropy: counts are
projected measurement outcomes that have already destroyed coherence
information, so S_vN (and therefore ETH = dS_vN/dt) cannot be reconstructed from
counts without quantum state tomography -- which is exactly the exponential
explosion we refuse to perform.

What we CAN measure honestly from counts:
  - marked_mass: fraction of the marked state (already used).
  - shannon_entropy: classical disorder of the observed distribution.
  - total_variation_distance: how much probability leaked from the ideal.
  - counts_diagnostic_score: a declared combination, explicitly classical.

These metrics are labelled ``classical_counts_diagnostic_not_quantum_entropy``.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def _normalize(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in counts.items()}


def shannon_entropy_bits(counts: dict[str, int]) -> float:
    """Classical Shannon entropy of the counts distribution (bits)."""
    probs = list(_normalize(counts).values())
    return float(-sum(p * np.log2(p) for p in probs if p > 0)) if probs else 0.0


def total_variation_distance(ideal_counts: dict[str, int], observed_counts: dict[str, int]) -> float:
    """Total variation distance between two count distributions, in [0, 1].

    Equals half the L1 distance of the normalised probability vectors. It
    measures the fraction of probability mass that moved between the ideal and
    the observed outcome. Bounded, symmetric, no support-zero issues (unlike KL).
    """
    ideal_p = _normalize(ideal_counts)
    observed_p = _normalize(observed_counts)
    keys = set(ideal_p) | set(observed_p)
    return float(0.5 * sum(abs(ideal_p.get(k, 0.0) - observed_p.get(k, 0.0)) for k in keys))


def counts_diagnostic(ideal_counts: dict[str, int], observed_counts: dict[str, int],
                      *, marked: str = "11", alpha: float = 0.5, beta: float = 0.5) -> dict[str, Any]:
    """Compute a declared classical diagnostic from counts.

    The score combines the marked-mass gap and the total-variation distance.
    Both are in [0, 1] and both measure classical probability leakage (not
    quantum coherence loss). alpha + beta should equal 1.0 for a normalised
    score in [0, 1].
    """
    ideal_p = _normalize(ideal_counts)
    observed_p = _normalize(observed_counts)
    ideal_mass = ideal_p.get(marked, 0.0)
    observed_mass = observed_p.get(marked, 0.0)
    mass_gap = abs(ideal_mass - observed_mass)
    tvd = total_variation_distance(ideal_counts, observed_counts)
    score = float(np.clip(alpha * mass_gap + beta * tvd, 0.0, 1.0))
    return {
        "marked_state": marked,
        "ideal_marked_mass": float(ideal_mass),
        "observed_marked_mass": float(observed_mass),
        "marked_mass_gap": float(mass_gap),
        "ideal_shannon_entropy_bits": shannon_entropy_bits(ideal_counts),
        "observed_shannon_entropy_bits": shannon_entropy_bits(observed_counts),
        "total_variation_distance": float(tvd),
        "counts_diagnostic_score": score,
        "score_weights": {"mass_gap": alpha, "tvd": beta},
        "scope": "classical_counts_diagnostic_not_quantum_entropy",
        "scope_note": (
            "Shannon entropy and TVD measure classical distribution leakage, "
            "not von Neumann coherence. ETH (dS_vN/dt) cannot be approximated "
            "from counts without quantum state tomography."
        ),
    }
