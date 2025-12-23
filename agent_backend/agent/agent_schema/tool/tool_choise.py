from enum import Enum


class ToolChoice(Enum):
    """
    none:明确禁止模型调用任何工具
    auto:由模型自行判断是否需要调用工具  vLLM 默认不支持 auto，除非显式开启 --enable-auto-tool-choice --tool-call-parser
    required:强制模型必须调用工具（至少一次）
    """
    
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
