"""Consolidated, human-reviewable English Freetalking semantic overrides."""

import ft_overrides_a
import ft_overrides_b
import ft_overrides_c
import ft_overrides_d


def _merge(name: str) -> dict:
    merged = {}
    for module in (ft_overrides_a, ft_overrides_b, ft_overrides_c, ft_overrides_d):
        rows = getattr(module, name)
        overlap = set(merged) & set(rows)
        if overlap:
            raise RuntimeError(f"duplicate {name} FT ids: {sorted(overlap)}")
        merged.update(rows)
    return merged


QUESTION_OVERRIDES = _merge("QUESTION_OVERRIDES")
TOPIC_OVERRIDES = _merge("TOPIC_OVERRIDES")
