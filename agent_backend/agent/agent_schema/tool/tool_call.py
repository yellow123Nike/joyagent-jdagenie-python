from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolCall:
    """
    工具调用类
    对齐 Java: ToolCall
    """
    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional["ToolCall.Function"] = None

    @dataclass
    class Function:
        """
        函数信息类
        """
        name: Optional[str] = None
        arguments: Optional[str] = None
