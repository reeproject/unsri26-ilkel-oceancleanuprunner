from dataclasses import dataclass


@dataclass
class Entity:
    lane: int
    x: float
    kind: str
    variant: int = 0


@dataclass
class Bubble:
    x: float
    y: float
    radius: int
    speed: float
    drift: float
    phase: float
