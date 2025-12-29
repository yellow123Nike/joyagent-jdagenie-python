import json
from typing import List, Optional

from agent_backend.agent.agent_core.agent_context import AgentContext
from agent_backend.agent.agent_core.reactagent import ReActAgent
from agent_backend.agent.agent_prompts.planning_prompt import (
    SYSTEM_PROMPT,
    NEXT_STEP_PROMPT
)
from agent_backend.agent.agent_schema.message import Message
from agent_backend.agent.agent_enums.agent_type import RoleType
from agent_backend.agent.agent_enums.agent_state import AgentState
from agent_backend.agent.agent_schema.tool.tool_call import ToolCall
from agent_backend.agent.agent_util.file_util import FileUtil

# 你需要提供/替换为真实的 PlanningTool
from agent_backend.agent.agent_tools.common.planning_tool import PlanningTool

PLANNING_MAX_STEPS=40
class PlanningImplAgent(ReActAgent):
    """
    - 先用 PlanningTool 生成/更新 plan
    - 如 plan 已生成，输出下一步任务（task）
    """

    def __init__(self, context: AgentContext, llm,is_close_update: bool = False, max_steps: int = PLANNING_MAX_STEPS):
        super().__init__(
            name="planning",
            description="An agent that creates and manages plans to solve tasks",
            system_prompt="",
            next_step_prompt="",
            llm=llm,
            context=context,
            max_steps=max_steps,
        )

        self.tool_calls: List[ToolCall] = []
        self.max_observe: Optional[int] = None
        #关闭动态更新 Plan 的开关 =1
        self.is_close_update: bool = is_close_update
        # PlanningTool
        self.planning_tool = PlanningTool(agent_context=context)
        self.available_tools.add_tool(self.planning_tool)
        # # ---------- 构造 tool prompt ----------
        # tool_prompt = []
        # for tool in context.tool_collection.get_tool_map().values():
        #     tool_prompt.append(
        #         f"工具名：{tool.name} 工具描述：{tool.description}"
        #     )
        # tool_prompt = "\n".join(tool_prompt)

        self.system_prompt = SYSTEM_PROMPT.format(
            sopPrompt=context.sop_prompt, 
            date=context.date_info
        )
        self.next_step_prompt = NEXT_STEP_PROMPT

        # ---------- Snapshot(快照-保存原始版本) ----------
        self.system_prompt_snapshot = self.system_prompt
        self.next_step_prompt_snapshot = self.next_step_prompt

     
    # ======================================================================
    # step =一次 think + act
    # ======================================================================
    async def step(self):
        should_continue = await self.think()
        if not should_continue:
            self.state = AgentState.FINISHED
            return self.memory.get_last_message().content
        return await self.act()

    # ======================================================================
    # THINK
    # ======================================================================
    async def think(self):
        """
        只负责：
        - prompt 构建（files 注入）
        - LLM tool planning（可能触发 PlanningTool）
        - memory 写 assistant/tool_call
        """
        try:
            # ---------- 注入 files ----------
            files_str = FileUtil.format_file_info(
                self.context.product_files, filter_internal_file=True
            )
            self.system_prompt = self.system_prompt_snapshot.replace("{{files}}", files_str)
            self.next_step_prompt = self.next_step_prompt_snapshot.replace("{{files}}", files_str)

            # ---------- 关闭动态更新 Plan：若已有 plan，直接推进一步 ----------
            if self.is_close_update and self.planning_tool.plan is not None:
                self.planning_tool.step_plan()
                return True

            # ---------- 确保 user message ----------
            last_msg = self.memory.get_last_message()
            if last_msg is not None and last_msg.role != RoleType.USER:
                self.update_memory(
                    RoleType.USER, 
                    self.next_step_prompt)

            self.context.stream_message_type = "plan_thought"

            # ---------- ask tool ----------
            response = await self.llm.ask_tool(
                context=self.context,
                messages=self.memory.messages,
                system_msgs=Message.system_message(self.system_prompt),
                tools=self.available_tools,
                tool_choice="auto",
            )

            self.tool_calls = response.tool_calls or []

            # ---------- 输出 thought ----------
            if not self.context.is_stream and response.content:
                if self.context.printer:
                    self.context.printer.send("plan_thought", response.content)
                else:
                    print(f"plan_thought:{response.content}")

            # ---------- assistant message ----------
            if self.tool_calls and self.llm.function_call_type != "struct_parse":
                msg = Message.from_tool_calls(response.content, self.tool_calls)
            else:
                msg = Message.assistant_message(response.content)

            self.memory.add_message(msg)
            return True

        except Exception as e:
            self.update_memory(RoleType.ASSISTANT, f"Error encountered while processing: {e}")
            self.state = AgentState.FINISHED
            return False

    # ======================================================================
    # ACT
    # ======================================================================
    async def act(self) -> str:
        """
        - 执行工具
        - 写 tool message
        - 如果形成 plan：返回下一步 task 或 finish
        """
        # ---------- 关闭动态更新 Plan：若已有 plan，直接输出 next task ----------
        if self.is_close_update and self.planning_tool.plan is not None:
            return self.get_next_task()

        results: List[str] = []

        for call in self.tool_calls:
            tool_id = call.id
            func = call.function
            tool_name = func.name
            args = json.loads(func.arguments or "{}")
            result = await self.execute_tool(call) 
            if self.max_observe:
                result = result[: self.max_observe] 
            results.append(result)
            if self.llm.function_call_type == "struct_parse":
                self.memory.last_message.content += "\n 工具执行结果为:\n" + result
            else:
                self.update_memory(RoleType.TOOL, result, None, tool_id)


        # 工具执行后，如果形成了 plan：输出 next task / finish
        if self.planning_tool.plan is not None:
            if self.is_close_update:
                self.planning_tool.step_plan()
            return self.get_next_task()

        return "\n\n".join(results)

    # ======================================================================
    # Next task
    # ======================================================================
    def get_next_task(self) -> str:
        if self.planning_tool.plan is None:
            return ""

        # 你需要保证 plan.step_status / plan.current_step 与 PlanningTool 输出字段一致
        plan = self.planning_tool.plan
        step_status = getattr(plan, "step_status", None) or getattr(plan, "stepStatus", None) or []
        current_step = getattr(plan, "current_step", None) or getattr(plan, "currentStep", None) or ""

        all_complete = True
        for status in step_status:
            if status != "completed":
                all_complete = False
                break

        if all_complete:
            self.state = AgentState.FINISHED
            if self.context.printer:
                self.context.printer.send("plan", plan)
            else:
                print(f"plan:{plan}")
            return "finish"

        if current_step:
            self.state = AgentState.FINISHED
            if self.context.printer:
                self.context.printer.send("plan", plan)
                for step in str(current_step).split("<sep>"):
                    step = step.strip()
                    if step:
                        self.context.printer.send("task", step)
            else:
                print(f"plan:{plan}")
                for step in str(current_step).split("<sep>"):
                    step = step.strip()
                    if step:
                        print(f"task:{step}")
            return str(current_step)

        return ""

    # ======================================================================
    # run hook 
    # ======================================================================
    def run(self, request: str) -> str:
        if self.planning_tool.plan is None:
            plan_pre_prompt = "分析问题并制定计划:"
            request = f"{plan_pre_prompt}{request}"
        return super().run(request)
