from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re


@dataclass
class AgentResponse:
    request_id: Optional[str] = None
    message_id: Optional[str] = None
    #是否为当前 request 的最终输出
    is_final: Optional[bool] = None
    message_type: Optional[str] = None
    #角色标识
    digital_employee: Optional[str] = None
    message_time: Optional[str] = None
    #规划思考
    plan_thought: Optional[str] = None
    #结构化执行计划
    plan: Optional["AgentResponse.Plan"] = None

    task: Optional[str] = None
    task_summary: Optional[str] = None

    #为什么选择这个工具
    tool_thought: Optional[str] = None
    tool_result: Optional["AgentResponse.ToolResult"] = None

    result_map: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    finish: Optional[bool] = None
    ext: Optional[Dict[str, str]] = None

    # -----------------------------
    # 内嵌模型：Plan 描述 Agent 在一次任务中的“结构化执行计划”，是“给系统执行 + 给人理解”的中间协议层
    # -----------------------------
    @dataclass
    class Plan:
        title: Optional[str] = None
        stages: List[str] = field(default_factory=list)
        steps: List[str] = field(default_factory=list)
        step_status: List[str] = field(default_factory=list)
        notes: List[str] = field(default_factory=list)

    # -----------------------------
    # 内嵌模型：ToolResult
    # -----------------------------
    @dataclass
    class ToolResult:
        tool_name: Optional[str] = None
        tool_param: Optional[Dict[str, Any]] = None
        tool_result: Optional[str] = None

    # -----------------------------
    # 静态方法：format_steps
    # -----------------------------
    @staticmethod
    def format_steps(plan: "AgentResponse.Plan"):
        """
        等价于 Java 版 formatSteps：
        解析：
        执行顺序1. 阶段名：具体步骤
        """
        new_plan = AgentResponse.Plan(
            title=plan.title,
            steps=[],
            stages=[],
            step_status=[],
            notes=[]
        )

        pattern = re.compile(r"执行顺序(\d+)\.\s?([\w\W]*)\s?[：:](.*)")

        for i, step in enumerate(plan.steps):
            # 保留原有状态与备注
            if plan.step_status:
                new_plan.step_status.append(plan.step_status[i])
            if plan.notes:
                new_plan.notes.append(plan.notes[i])

            match = pattern.search(step)
            if match:
                # group(2) -> stage
                # group(3) -> step
                new_plan.stages.append(match.group(2).strip())
                new_plan.steps.append(match.group(3).strip())
            else:
                new_plan.stages.append("")
                new_plan.steps.append(step)

        return new_plan
