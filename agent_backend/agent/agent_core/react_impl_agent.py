import json
from typing import List, Dict, Optional
from agent_backend.agent.agent_core.reactagent import ReActAgent
from agent_backend.agent.agent_prompts.comm_prompt import Digital_Employee_Prompt
from agent_backend.agent.agent_prompts.toolcall_prompt import NEXT_STEP_PROMPT, SYSTEM_PROMPT, React_Max_Steps
from agent_backend.agent.agent_schema.message import Message
from agent_backend.agent.agent_enums.agent_type import RoleType
from agent_backend.agent.agent_enums.agent_state import AgentState
from agent_backend.agent.agent_util.file_util import FileUtil


class ReactImplAgent(ReActAgent):
    """
    Tool-call capable ReAct Agent
    """

    def __init__(self, context,llm):
        super().__init__(
                    name="react",
                    description="an agent that can execute tool calls.",
                    system_prompt="",
                    next_step_prompt="",
                    llm=llm,
                    context=context,
                    max_steps=React_Max_Steps,
                )
        self.available_tools = context.tool_collection
        self.tool_calls: List[dict] = []
        self.max_observe: Optional[int] = None

        # # ---------- 构造 tool prompt ----------
        # tool_prompt = []
        # for tool in context.tool_collection.get_tool_map().values():
        #     tool_prompt.append(
        #         f"工具名：{tool.name} 工具描述：{tool.description}"
        #     )
        # tool_prompt = "\n".join(tool_prompt)

        # ---------- Prompt ----------
        self.system_prompt = SYSTEM_PROMPT.format(
            basePrompt=context.base_prompt, 
            query=context.query,
            date=context.date_info
        )

        self.next_step_prompt = NEXT_STEP_PROMPT

        # ---------- Snapshot(快照-保存原始版本) ----------
        self.system_prompt_snapshot = self.system_prompt
        self.next_step_prompt_snapshot = self.next_step_prompt

        # ---------- Runtime ----------
        self.digital_employee_prompt=Digital_Employee_Prompt

    # ======================================================================
    # step =一次 think + act
    # ======================================================================
    async def step(self) -> str:
        should_continue = await self.think()
        if not should_continue:
            self.state = AgentState.FINISHED
            return self.memory.get_last_message().content

        return await self.act()

    # ======================================================================
    # THINK
    # ======================================================================
    async def think(self) -> bool:
        """
        只负责：
        - prompt 构建
        - LLM tool planning
        - memory 写 assistant/tool_call
        """

        try:
            # ---------- 注入 files ----------
            files_str = FileUtil.format_file_info(
                self.context.product_files, filter_internal_file=True
            )

            self.system_prompt = self.system_prompt_snapshot.replace(
                "{{files}}", files_str
            )
            self.next_step_prompt = self.next_step_prompt_snapshot.replace(
                "{{files}}", files_str
            )

            # ---------- 确保 user message ----------
            last_msg = self.memory.get_last_message()
            if last_msg is not None and last_msg.role != RoleType.USER:
                self.update_memory(
                    RoleType.USER,
                    self.next_step_prompt
                )

            self.context.stream_message_type = "tool_thought"

            # ---------- ask tool ----------
            response = await self.llm.ask_tool(
                context=self.context,
                messages=self.memory.messages,
                system_msgs=Message.system_message(self.system_prompt),
                tools=self.available_tools,
                tool_choice="auto"
            )

            self.tool_calls = response.tool_calls or []

            # ---------- 输出 thought ----------
            if not self.context.is_stream and response.content:
                print(f"tool_thought:{response.content}")

            # ---------- assistant message ----------
            if self.tool_calls and self.llm.function_call_type != "struct_parse":
                msg = Message.from_tool_calls(
                    response.content,
                    self.tool_calls
                )
            else:
                msg = Message.assistant_message(response.content)

            self.memory.add_message(msg)

            return True

        except Exception as e:
            self.update_memory(
                RoleType.ASSISTANT,
                f"Error encountered while processing: {e}"
            )
            self.state = AgentState.FINISHED
            return False

    # ======================================================================
    # ACT
    # ======================================================================
    async def act(self) -> str:
        """
        - 执行工具
        - 写 tool message
        """

        if not self.tool_calls:
            self.state = AgentState.FINISHED
            return self.memory.get_last_message().content

        tool_results = await self.execute_tools(self.tool_calls)

        results = []

        for call in self.tool_calls:
            tool_id = call.id
            func = call.function
            tool_name = func.name
            args = json.loads(func.arguments or "{}")

            result = tool_results.get(tool_id, "")

            # ---------- 打印 tool result ----------
            if tool_name not in {
                "code_interpreter",
                "report_tool",
                "file_tool",
                "knowledge_tool",
                "deep_search",
                "data_analysis",
            }:
                if self.context.printer:
                    self.context.printer.send(
                        message_type="tool_result",
                        message={
                            "toolName": tool_name,
                            "toolParam": args,
                            "toolResult": result,
                        },
                    )

            if self.max_observe:
                result = result[: self.max_observe]

            # ---------- 写 memory ----------
            if self.llm.function_call_type == "struct_parse":
                self.memory.last_message.content += (
                    "\n工具执行结果为:\n" + result
                )
            else:
                self.update_memory(
                    RoleType.TOOL,
                    result,
                    None,
                    tool_id,
                )

            results.append(result)

        return "\n\n".join(results)