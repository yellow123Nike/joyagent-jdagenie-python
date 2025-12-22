from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """
    工具基接口
    """
    name: str
    description: str

    @abstractmethod
    def to_params(self) -> Dict[str, Any]:
        """
        返回工具参数定义
        等价 Java：
        Map<String, Object> toParams()
        通常是 JSON Schema / 参数约束
        """
        pass

    @abstractmethod
    def execute(self, input: Any) -> Any:
        """
        执行工具逻辑
        等价 Java：
        Object execute(Object input)
        """
        pass
