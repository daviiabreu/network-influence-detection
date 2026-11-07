from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "ic_study",
        "ic_study.analysis",
        "ic_study.literature",
        "ic_study.metrics",
        "ic_study.models",
        "ic_study.simulation",
        "ic_study.validation",
    ],
)
def test_placeholder_module_is_importable(module_name: str) -> None:
    module = import_module(module_name)

    assert module.__doc__
