import json
from dataclasses import asdict, dataclass
from typing import List, Literal

Dynamics = Literal["soft", "medium", "loud"]
Density = Literal["sparse", "normal", "dense"]

@dataclass(frozen=True)
class LLMInput:
    key: str
    pitch_classes: List[str]
    frequencies: List[float]
    dynamics: Dynamics
    density: Density

@dataclass(frozen=True)
class LLMOutput:
    base_hue: float
    hue_offset: float
    saturation: float
    brightness: float

def validate_output(output: LLMOutput) -> None:
    if not (0 <= output.base_hue <= 360):
        raise ValueError("Base hue must be between 0 and 360")
    if not (-180 <= output.hue_offset <= 180):
        raise ValueError("Hue offset must be between -180 and 180")
    if not (0 <= output.saturation <= 1.0):
        raise ValueError("Saturation must be between 0 and 1.0")
    if not (0 <= output.brightness <= 1.0):
        raise ValueError("Brightness must be between 0 and 1.0")

def output_to_json(output: LLMOutput) -> str:
    return json.dumps(asdict(output), ensure_ascii=False)