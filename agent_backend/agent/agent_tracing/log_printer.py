import json
import logging
from typing import Any, Optional
from agent_model.req.agent_request import AgentRequest
from agent_backend.agent.agent_tracing.printer import Printer
logger = logging.getLogger(__name__)


class LogPrinter(Printer):
    def __init__(self, request:AgentRequest):
        self.request = request

    # =============================
    # 核心 send
    # =============================
    def send(
        self,
        message_id: Optional[str],
        message_type: str,
        message: Any,
        digital_employee: Optional[str] = None,
        is_final: Optional[bool] = None,
    ):
        # deep_search 特殊序列化
        if message_type == "deep_search":
            try:
                message = json.dumps(message, ensure_ascii=False)
            except TypeError:
                message = str(message)

        logger.info(
            "%s %s %s %s %s %s",
            self.request.request_id,
            message_id,
            message_type,
            message,
            digital_employee,
            is_final,
        )

    # =============================
    # send_simple
    # =============================
    def send_simple(
        self,
        message_type: str,
        message: Any,
        digital_employee: Optional[str] = None,
    ) -> None:
        self.send(
            message_id=None,
            message_type=message_type,
            message=message,
            digital_employee=digital_employee,
            is_final=True,
        )

    # =============================
    # send_partial
    # =============================
    def send_partial(
        self,
        message_id: str,
        message_type: str,
        message: Any,
        is_final: Optional[bool] = None,
    ) -> None:
        self.send(
            message_id=message_id,
            message_type=message_type,
            message=message,
            digital_employee=None,
            is_final=is_final,
        )

    def close(self) -> None:
        pass

    def update_agent_type(self, agent_type) -> None:
        pass