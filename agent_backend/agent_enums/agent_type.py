from enum import Enum
from typing import Set
"""
Agent类型
"""
class AgentType(Enum):
    COMPREHENSIVE = 1
    WORKFLOW = 2
    PLAN_SOLVE = 3
    ROUTER = 4
    REACT = 5

    @property
    def value_code(self) -> int:
        """等价于 Java 的 getValue()"""
        return self.value

    @staticmethod
    def from_code(value: int) -> "AgentType":
        """等价于 Java 的 fromCode(int value)"""
        for agent_type in AgentType:
            if agent_type.value == value:
                return agent_type
        raise ValueError(f"Invalid AgentType code: {value}")

"""
Agent标志:是不是默认agent
"""
class IsDefaultAgent(Enum):
    IS_DEFAULT_AGENT = 1
    NOT_DEFAULT_AGENT = 2

    @property
    def value_code(self) -> int:
        """等价于 Java 的 getValue()"""
        return self.value

"""
响应类型
"""
class ResponseTypeEnum(Enum):
    MARKDOWN = "markdown"
    TEXT = "text"
    CARD = "card"
    
"""
角色类型
"""
class RoleType(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"

    @property
    def value_str(self) -> str:
        """等价于 Java 的 getValue()"""
        return self.value

    @staticmethod
    def is_valid(role: str) -> bool:
        """等价于 Java 的 isValid(String role)"""
        return role in {r.value for r in RoleType}

    @staticmethod
    def from_string(role: str) -> "RoleType":
        """等价于 Java 的 fromString(String role)"""
        for r in RoleType:
            if r.value == role:
                return r
        raise ValueError(f"Invalid role: {role}")