from dataclasses import dataclass, field
from typing import List, Optional, Any
from agent_backend.agent.agent_tracing.printer import Printer
from agent_backend.agent.agent_tools.tool_collection import ToolCollection

@dataclass
class AgentContext:
    # ========= 基础追踪信息 =========
    request_id: str
    session_id: Optional[str] = None

    # ========= 用户 & 任务语义 =========
    query: Optional[str] = None           # 用户原始问题
    task: Optional[str] = None            # 当前 Agent 子任务
    agent_type: Optional[int] = None      # AgentType 枚举值

    # ========= 流式与输出控制 =========
    printer: Optional[Printer] = None         # Printer 实例（SSE / WS / Console）
    is_stream: bool = False
    stream_message_type: str = "llm"      # 与 Java 对齐：context.getStreamMessageType()

    # ========= 工具与能力 =========
    tool_collection: Optional[ToolCollection] = None # ToolCollection

    # ========= Prompt & 模板 =========
    sop_prompt: Optional[str] = None
    base_prompt: Optional[str] = None
    template_type: Optional[str] = None   # markdown / text / card

    # ========= 文件 & RAG =========
    product_files: List[Any] = field(default_factory=list)
    task_product_files: List[Any] = field(default_factory=list)

    # ========= 环境信息 =========
    date_info: Optional[str] = None
