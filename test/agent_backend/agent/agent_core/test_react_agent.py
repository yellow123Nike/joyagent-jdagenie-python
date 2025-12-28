
import ast
import asyncio
import math

import pytest
from agent_backend.agent.agent_core.agent_context import AgentContext
from agent_backend.agent.agent_core.react_impl_agent import ReactImplAgent
from agent_backend.agent.agent_enums.agent_type import RoleType
from agent_backend.agent.agent_llms.llm import LLMClient
from agent_backend.agent.agent_llms.llm_setting_params import LLMParams
from agent_backend.agent.agent_schema.message import Message
import ast
import math

from agent_backend.agent.agent_tools.base_tool import BaseTool
from agent_backend.agent.agent_tools.tool_collection import ToolCollection
from agent_backend.agent.agent_tracing.stdout_printer import StdoutPrinter
from agent_backend.agent_model.req.agent_request import AgentRequest


class PythonCalcTool(BaseTool):
    """
    使用 Python 安全执行简单数学表达式的工具
    """

    name = "python_calc"
    description = (
        "Execute a Python math expression safely. "
        "Useful for complex calculations or multi-step math."
    )

    # =========================
    # tool schema（function calling）
    # =========================
    def to_params(self):
        return {
            "type": "object",
            "properties": {
                "expr": {
                    "type": "string",
                    "description": (
                        "A Python math expression, e.g. "
                        "'sum(i*i for i in range(1, 101)) + 123'"
                    ),
                }
            },
            "required": ["expr"],
        }

    # =========================
    # tool execution
    # =========================
    async def execute(self, tool_input: dict) -> str:
        expr = tool_input.get("expr")
        if not expr:
            return "Error: expr is required"

        try:
            allowed_names = {
                "math": math,
                "sum": sum,
                "range": range,
                "pow": pow,
            }

            tree = ast.parse(expr, mode="eval")
            code = compile(tree, "<expr>", "eval")

            result = eval(code, {"__builtins__": {}}, allowed_names)
            return str(result)

        except Exception as e:
            return f"Error evaluating expression: {e}"


params = LLMParams(
    model_name="Qwen/Qwen3-32B-AWQ",
    api_key="sk-",
    base_url="http://0.0.0.0:18006/v1/",
    temperature=0.7,
    max_tokens=8024,
    is_claude=False,
)

@pytest.mark.asyncio
async def test_react_impl_agent():
    tools = ToolCollection()
    tools.add_tool(PythonCalcTool())
    io_printer=StdoutPrinter(request=AgentRequest(request_id="test-fc"))
    context = AgentContext(
        request_id="test-fc", 
        base_prompt=(
            "你是一个 ReAct 智能体。\n"
            "当计算步骤较多或中间结果需要复用时，"
            "应优先使用工具完成计算，而不是心算。"
        ),
        date_info="2025-01-01",
        printer=io_printer,
        )
    context.tool_collection = tools
    agent = ReactImplAgent(context,LLMClient(params))
    query = (
        "请你完成以下任务：\n"
        "1. 先计算 1 到 100 的平方和；\n"
        "2. 再计算这个结果与 123 相加；\n"
        "3. 再将新的结果除以 7；\n"
        "4. 返回最终结果。\n\n"
        "要求：\n"
        "- 当计算较复杂时，优先使用工具；\n"
        "- 不要直接心算；\n"
        "- 最终只给出结果。"
    )
    final_answer = await agent.run(query)
    print("\n===== FINAL ANSWER =====")
    print(final_answer)
    print("\n===== Message =====")
    print(agent.memory.messages)

asyncio.run(test_react_impl_agent())