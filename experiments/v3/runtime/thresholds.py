"""Outcome-independent component-local score-domain contract."""

from __future__ import annotations

from typing import Any, Mapping


SCORE_CONTRACT: dict[str, dict[str, tuple[str, bool]]] = {
    "v3.1-gdino-siglip2": {
        "entity": ("grounding_dino_postprocessed_score", False),
        "colour": ("siglip2_sigmoid_logit", True),
        "size": ("siglip2_sigmoid_logit", True),
        "material": ("siglip2_sigmoid_logit", True),
        "pattern": ("siglip2_sigmoid_logit", True),
        "unary_action": ("siglip2_sigmoid_logit", True),
        "binary_interaction": ("siglip2_sigmoid_logit", True),
        "scene": ("siglip2_sigmoid_logit", True),
    },
    "v3.1-egtr-siglip2": {
        "entity": ("egtr_object_softmax", False),
        "predicate": ("egtr_relation_sigmoid", False),
        "connectivity": ("egtr_connectivity_sigmoid", False),
        "colour": ("siglip2_sigmoid_logit", True),
        "size": ("siglip2_sigmoid_logit", True),
        "material": ("siglip2_sigmoid_logit", True),
        "pattern": ("siglip2_sigmoid_logit", True),
        "scene": ("siglip2_sigmoid_logit", True),
    },
}


def validate_settings(pipeline_id: str, values: Mapping[str, Any], *, exact_tasks: bool) -> None:
    expected = SCORE_CONTRACT[pipeline_id]
    if exact_tasks and set(values) != set(expected):
        raise ValueError(f"threshold task set mismatch for {pipeline_id}")
    for task, setting in values.items():
        if task not in expected or not isinstance(setting, Mapping):
            raise ValueError(f"unknown threshold setting {pipeline_id}/{task}")
        score_name, needs_margin = expected[task]
        if setting.get("score_name") != score_name or setting.get("score_range") != [0.0, 1.0] or setting.get("threshold_source") != "development":
            raise ValueError(f"score-domain mismatch for {pipeline_id}/{task}")
        threshold = setting.get("threshold")
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
            raise ValueError(f"invalid threshold for {pipeline_id}/{task}")
        if needs_margin:
            margin = setting.get("minimum_top_two_margin")
            if isinstance(margin, bool) or not isinstance(margin, (int, float)) or not 0 <= margin <= 1:
                raise ValueError(f"missing/invalid top-two margin for {pipeline_id}/{task}")
