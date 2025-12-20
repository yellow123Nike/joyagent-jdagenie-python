from abc import ABC, abstractmethod
from typing import Any, Optional
from agent_backend.agent.agent_enums.agent_type import AgentType

class Printer(ABC):
    """
    Printer 抽象接口
    对齐 Java com.jd.genie.agent.Printer
    """

    @abstractmethod
    def send(
        self,
        message_id: str,
        message_type: str,
        message: Any,
        digital_employee: Optional[str] = None,
        is_final: Optional[bool] = None,
    ):
        """
        发送完整参数版本（最核心）
        """
        pass

    @abstractmethod
    def send_simple(
        self,
        message_type: str,
        message: Any,
        digital_employee: Optional[str] = None,
    ) -> None:
        """
        对齐：
        send(String messageType, Object message)
        send(String messageType, Object message, String digitalEmployee)
        """
        pass

    @abstractmethod
    def send_partial(
        self,
        message_id: str,
        message_type: str,
        message: Any,
        is_final: Optional[bool] = None,
    ) -> None:
        """
        对齐：
        send(String messageId, String messageType, Object message, Boolean isFinal)
        """
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def update_agent_type(self, agent_type: AgentType) -> None:
        """
        对齐：
        void updateAgentType(AgentType agentType)
        """
        pass
