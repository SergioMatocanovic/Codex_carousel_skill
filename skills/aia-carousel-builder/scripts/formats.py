"""Supported Instagram carousel canvas formats."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanvasFormat:
    key: str
    width: int
    height: int
    label: str
    ratio: str


FORMATS: dict[str, CanvasFormat] = {
    "vertical-principal": CanvasFormat(
        key="vertical-principal",
        width=1080,
        height=1440,
        label="Vertical Principal",
        ratio="3:4",
    ),
    "vertical-classic": CanvasFormat(
        key="vertical-classic",
        width=1080,
        height=1350,
        label="Vertical Classic",
        ratio="4:5",
    ),
    "square": CanvasFormat(
        key="square",
        width=1080,
        height=1080,
        label="Square",
        ratio="1:1",
    ),
}


def format_choices() -> tuple[str, ...]:
    return tuple(FORMATS)


def get_format(key: str) -> CanvasFormat:
    return FORMATS[key]
