from dataclasses import dataclass, field
from typing import Any, Callable, List, Dict, Optional

from agent_backend.agent.agent_core.agent_context import AgentContext
from agent_backend.agent.agent_schema.plan import Plan
from agent_backend.agent.agent_tools.base_tool import BaseTool

@dataclass
class PlanningTool(BaseTool):
    """
    计划工具类
    """
    agent_context: Optional[AgentContext] = None
    plan: Optional[Plan] = None
    command_handlers: Dict[str, Callable[[Dict[str, Any]], str]] = field(
        default_factory=dict
    )

    def __post_init__(self):
        self.description=self.get_description()
        self.name = self.get_name()
        self.command_handlers = {
            "create": self.create_plan,
            "update": self.update_plan,
            "mark_step": self.mark_step,
            "finish": self.finish_plan,
        }

    # ---------- Tool 基本信息 ----------
    def get_name(self):
        return "planning"

    def get_description(self):
        desc = """
            这是一个计划工具，可让代理创建和管理用于解决复杂任务的计划。
            该工具提供创建计划、更新计划步骤和跟踪进度的功能。
            创建计划时，需要创建出有依赖关系的计划，
            计划列表格式如下：
            [执行顺序+编号、任务短标题：任务的细节描述]，
            样式示例如下：[
                执行顺序1. 任务短标题: 任务描述xxx ..., 
                执行顺序2. 任务短标题：任务描述xxx ..., 
                执行顺序3. 任务短标题：任务描述xxx ... ]"""
        return desc

    # ---------- 参数 Schema ----------

    def to_params(self) :
        out={
            "type":"object",
            "properties":{
                "step_status":{
                    "description":"每一个子任务的状态. 当command是 mark_step 时使用.",
                    "type":"string",
                    "enum":["not_started","in_progress","completed","blocked"]
                    },
                "step_notes":{
                    "description":"每一个子任务的的备注，当command 是 mark_step 时，是备选参数。",
                    "type":"string"},
                "step_index":{
                    "description":"当command 是 mark_step 时，是必填参数.",
                    "type":"integer"},
                "title":{
                    "description":"任务的标题，当command是create时，是必填参数，如果是update 则是选填参数。",
                    "type":"string"},
                "steps":{
                    "description":"入参是任务列表. 当创建任务时，command是create，此时这个参数是必填参数。任务列表的的格式如下：[\"执行顺序 + 编号、执行任务简称：执行任务的细节描述\"]。不同的子任务之间不能重复、也不能交叠，可以收集多个方面的信息，收集信息、查询数据等此类多次工具调用，是可以并行的任务。具体的格式示例如下：- 任务列表示例1: [\"执行顺序1. 执行任务简称（不超过6个字）：执行任务的细节描述（不超过50个字）\", \"执行顺序2. xxx（不超过6个字）：xxx（不超过50个字）, ...\"]；",
                    "type":"array",
                    "items":{
                        "type":"string"
                        }
                    },
                "command":{
                    "description":"需要执行的命令，取值范围是: create",
                    "type":"string",
                    "enum":["create"]}
                },
            "required":["command"]
            }
        if out:
            return out
        return self._get_parameters()

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": self._get_properties(),
            "required": ["command"],
        }

    def _get_properties(self) -> Dict[str, Any]:
        return {
            "command": self._get_command_property(),
            "title": self._get_title_property(),
            "steps": self._get_steps_property(),
            "step_index": self._get_step_index_property(),
            "step_status": self._get_step_status_property(),
            "step_notes": self._get_step_notes_property(),
        }

    def _get_command_property(self) -> Dict[str, Any]:
        return {
            "type": "string",
            "enum": ["create", "update", "mark_step", "finish"],
            "description": (
                "The command to execute. Available commands: "
                "create, update, mark_step, finish"
            ),
        }

    def _get_title_property(self) -> Dict[str, Any]:
        return {
            "type": "string",
            "description": (
                "Title for the plan. Required for create command, "
                "optional for update command."
            ),
        }

    def _get_steps_property(self) -> Dict[str, Any]:
        return {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "List of plan steps. Required for create command, "
                "optional for update command."
            ),
        }

    def _get_step_index_property(self) -> Dict[str, Any]:
        return {
            "type": "integer",
            "description": (
                "Index of the step to update (0-based). "
                "Required for mark_step command."
            ),
        }

    def _get_step_status_property(self) -> Dict[str, Any]:
        return {
            "type": "string",
            "enum": ["not_started", "in_progress", "completed", "blocked"],
            "description": (
                "Status to set for a step. Used with mark_step command."
            ),
        }

    def _get_step_notes_property(self) -> Dict[str, Any]:
        return {
            "type": "string",
            "description": (
                "Additional notes for a step. Optional for mark_step command."
            ),
        }

    # ---------- 执行入口 ----------

    async def execute(self, input: Any):
        if not isinstance(input, dict):
            raise ValueError("Input must be a Map")

        command = input.get("command")
        if not command:
            raise ValueError("Command is required")

        handler = self.command_handlers.get(command)
        if not handler:
            raise ValueError(f"Unknown command: {command}")

        return handler(input)

    # ---------- Command 实现 ----------

    def create_plan(self, params: Dict[str, Any]) -> str:
        title = params.get("title")
        steps = params.get("steps")

        if title is None or steps is None:
            raise ValueError("title, and steps are required for create command")

        if self.plan is not None:
            raise RuntimeError(
                "A plan already exists. Delete the current plan first."
            )

        self.plan = Plan.create(title, steps)
        return "我已创建plan"

    def update_plan(self, params: Dict[str, Any]) -> str:
        if self.plan is None:
            raise RuntimeError("No plan exists. Create a plan first.")

        title = params.get("title")
        steps = params.get("steps")
        self.plan.update(title, steps)

        return "我已更新plan"

    def mark_step(self, params: Dict[str, Any]) -> str:
        if self.plan is None:
            raise RuntimeError("No plan exists. Create a plan first.")

        step_index = params.get("step_index")
        step_status = params.get("step_status")
        step_notes = params.get("step_notes")

        if step_index is None:
            raise ValueError("step_index is required for mark_step command")

        self.plan.update_step_status(step_index, step_status, step_notes)
        return f"我已标记plan {step_index} 为 {step_status}"

    def finish_plan(self, params: Dict[str, Any]) -> str:
        if self.plan is None:
            self.plan = Plan()
        else:
            for idx in range(len(self.plan.steps)):
                self.plan.update_step_status(idx, "completed", "")

        return "我已更新plan为完成状态"

    # ---------- 其他方法 ----------

    def step_plan(self) -> None:
        if self.plan:
            self.plan.step_plan()

    def get_format_plan(self) -> str:
        if self.plan is None:
            return "目前还没有Plan"
        return self.plan.format()