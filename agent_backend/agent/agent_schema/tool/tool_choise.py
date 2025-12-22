from enum import Enum


class ToolChoice(Enum):
    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"

    @classmethod
    def is_valid(cls, value: "ToolChoice") -> bool:
        return value is not None and value.value in {
            "none", "auto", "required"
        }

    @classmethod
    def from_string(cls, value: str) -> "ToolChoice":
        try:
            return ToolChoice(value)
        except ValueError:
            raise ValueError(f"Invalid tool choice: {value}")
