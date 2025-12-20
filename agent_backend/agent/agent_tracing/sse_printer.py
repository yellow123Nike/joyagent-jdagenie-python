from agent_backend.agent.agent_enums.agent_type import AgentType
import json
import logging
import time
import uuid
from typing import Any, Optional, Dict
from agent_backend.agent.agent_tracing.printer import Printer
from agent_model.req.agent_request import AgentRequest
from agent_model.response.agent_response import AgentResponse
logger = logging.getLogger(__name__)

class SSEPrinter(Printer):
    def __init__(self, emitter, request:AgentRequest, agent_type: int):
        self.emitter = emitter
        self.request = request
        self.agent_type = agent_type

    # =============================
    # 核心 send（完整参数）
    # =============================
    def send(
        self,
        message_id: Optional[str],
        message_type: str,
        message: Any,
        digital_employee: Optional[str] = None,
        is_final: Optional[bool] = None,
    ):
        try:
            if message_id is None:
                message_id = str(uuid.uuid4())

            logger.info(
                "%s sse send %s %s %s",
                self.request.request_id,
                message_type,
                message,
                digital_employee,
            )

            finish = message_type == "result"

            result_map: Dict[str, Any] = {"agentType": self.agent_type}

            response = AgentResponse(
                request_id=self.request.request_id,
                message_id=message_id,
                message_type=message_type,
                message_time=str(int(time.time() * 1000)),
                result_map=result_map,
                finish=finish,
                is_final=is_final,
            )

            if digital_employee:
                response.digital_employee = digital_employee

            # =============================
            # messageType 分发逻辑
            # =============================
            if message_type == "tool_thought":
                response.tool_thought = str(message)

            elif message_type == "task":
                # 对齐 Java：去掉“执行顺序x.”
                response.task = str(message).lstrip().replace("执行顺序", "", 1)
                response.task = response.task.split(".", 1)[-1].strip()

            elif message_type == "task_summary":
                if isinstance(message, dict):
                    response.result_map = message
                    response.task_summary = (
                        str(message.get("taskSummary"))
                        if message.get("taskSummary") is not None
                        else None
                    )
                else:
                    logger.error("ssePrinter task_summary format is illegal")

            elif message_type == "plan_thought":
                response.plan_thought = str(message)

            elif message_type == "plan":
                plan = AgentResponse.Plan()
                # 等价 BeanUtils.copyProperties
                for k, v in vars(message).items():
                    setattr(plan, k, v)
                response.plan = AgentResponse.format_steps(plan)

            elif message_type == "tool_result":
                response.tool_result = message

            elif message_type in {
                "browser",
                "code",
                "html",
                "markdown",
                "ppt",
                "file",
                "knowledge",
                "deep_search",
                "data_analysis",
            }:
                parsed = (
                    message
                    if isinstance(message, dict)
                    else json.loads(json.dumps(message, ensure_ascii=False))
                )
                parsed["agentType"] = self.agent_type
                response.result_map = parsed

            elif message_type == "agent_stream":
                response.result = str(message)

            elif message_type == "result":
                if isinstance(message, str):
                    response.result = message
                elif isinstance(message, dict):
                    response.result_map = message
                    response.result = (
                        str(message.get("taskSummary"))
                        if message.get("taskSummary") is not None
                        else None
                    )
                else:
                    parsed = json.loads(json.dumps(message, ensure_ascii=False))
                    response.result_map = parsed
                    response.result = str(parsed.get("taskSummary"))

                response.result_map["agentType"] = self.agent_type

            # 发送 SSE
            self.emitter.send(response)

        except Exception as e:
            logger.error("sse send error", exc_info=e)

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
        self.emitter.complete()

    def update_agent_type(self, agent_type) -> None:
        # 对齐 Java：AgentType.getValue()
        self.agent_type = agent_type.value