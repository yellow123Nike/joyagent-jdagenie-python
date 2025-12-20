from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional
from enum import Enum, auto
from dataclasses import dataclass, field


# ===== enums =====

class AgentState(Enum):
    IDLE = auto()
    FINISHED = auto()
    ERROR = auto()


class RoleType(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"


# ===== DTO =====

@dataclass
class Message:
    role: RoleType
    content: str
    base64_image: Optional[str] = None
    tool_name: Optional[str] = None

    @staticmethod
    def user(content: str, base64_image: Optional[str] = None) -> "Message":
        return Message(RoleType.USER, content, base64_image)

    @staticmethod
    def system(content: str, base64_image: Optional[str] = None) -> "Message":
        return Message(RoleType.SYSTEM, content, base64_image)

    @staticmethod
    def assistant(content: str, base64_image: Optional[str] = None) -> "Message":
        return Message(RoleType.ASSISTANT, content, base64_image)

    @staticmethod
    def tool(content: str, tool_name: str, base64_image: Optional[str] = None) -> "Message":
        return Message(RoleType.TOOL, content, base64_image, tool_name)


@dataclass
class Memory:
    messages: List[Message] = field(default_factory=list)

    def add_message(self, message: Message):
        self.messages.append(message)


# ===== Tool =====

class ToolCollection:
    def __init__(self):
        self._tools: Dict[str, Any] = {}

    def register(self, name: str, func):
        self._tools[name] = func

    async def execute(self, name: str, args: Any) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found")
        tool = self._tools[name]
        if asyncio.iscoroutinefunction(tool):
            return await tool(args)
        return tool(args)


# ===== LLM / Context placeholders =====

class LLM:
    async def generate(self, messages: List[Message]) -> str:
        raise NotImplementedError


@dataclass
class AgentContext:
    request_id: str


# ===== BaseAgent =====

class BaseAgent:
    """
    Python equivalent of com.jd.genie.agent.agent.BaseAgent
    """

    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        system_prompt: str = "",
        next_step_prompt: str = "",
        llm: Optional[LLM] = None,
        context: Optional[AgentContext] = None,
        max_steps: int = 10,
        duplicate_threshold: int = 2,
    ):
        # core
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.next_step_prompt = next_step_prompt
        self.digital_employee_prompt: Optional[str] = None

        self.available_tools = ToolCollection()
        self.memory = Memory()
        self.llm = llm
        self.context = context

        # execution control
        self.state = AgentState.IDLE
        self.max_steps = max_steps
        self.current_step = 0
        self.duplicate_threshold = duplicate_threshold

        # printer（可选）
        self.printer = None

    # ===== abstract step =====
    async def step(self) -> str:
        """
        子类必须实现单步逻辑
        """
        raise NotImplementedError

    # ===== main loop =====
    async def run(self, query: str) -> str:
        self.state = AgentState.IDLE
        self.current_step = 0

        if query:
            self.update_memory(RoleType.USER, query)

        results: List[str] = []

        try:
            while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
                self.current_step += 1
                req_id = self.context.request_id if self.context else "-"
                print(f"{req_id} {self.name} Executing step {self.current_step}/{self.max_steps}")

                step_result = await self.step()
                results.append(step_result)

            if self.current_step >= self.max_steps:
                self.current_step = 0
                self.state = AgentState.IDLE
                results.append(f"Terminated: Reached max steps ({self.max_steps})")

        except Exception:
            self.state = AgentState.ERROR
            raise

        return results[-1] if results else "No steps executed"

    # ===== memory =====
    def update_memory(
        self,
        role: RoleType,
        content: str,
        base64_image: Optional[str] = None,
        *args,
    ):
        if role == RoleType.USER:
            msg = Message.user(content, base64_image)
        elif role == RoleType.SYSTEM:
            msg = Message.system(content, base64_image)
        elif role == RoleType.ASSISTANT:
            msg = Message.assistant(content, base64_image)
        elif role == RoleType.TOOL:
            msg = Message.tool(content, args[0], base64_image)
        else:
            raise ValueError(f"Unsupported role type: {role}")

        self.memory.add_message(msg)

    # ===== tool execution =====
    async def execute_tool(self, command: Dict[str, Any]) -> str:
        try:
            func = command.get("function")
            if not func or "name" not in func:
                return "Error: Invalid function call format"

            name = func["name"]
            args = json.loads(func.get("arguments", "{}"))

            result = await self.available_tools.execute(name, args)
            req_id = self.context.request_id if self.context else "-"
            print(f"{req_id} execute tool: {name} {args} result {result}")

            return str(result) if result is not None else ""

        except Exception as e:
            req_id = self.context.request_id if self.context else "-"
            print(f"{req_id} execute tool {name} failed: {e}")
            return f"Tool {name} Error."

    async def execute_tools(self, commands: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        并发执行多个工具调用（等价 Java CountDownLatch）
        """
        async def _run(cmd):
            return cmd["id"], await self.execute_tool(cmd)

        tasks = [_run(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks)

        return {tool_id: output for tool_id, output in results}
