import typing as T
import time
from dataclasses import dataclass


@dataclass
class SyntheticData:
    input: str
    output: str
    context: str
    task: str

    def __hash__(self) -> int:
        return hash((self.input, self.task))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SyntheticData):
            return NotImplemented
        return self.prompt == other.prompt

    def to_dict(self) -> dict:
        return {
            "input": self.input,
            "output": self.output,
            "context": self.context,
            "task": self.task,
        }