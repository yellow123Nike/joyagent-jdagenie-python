import asyncio
import pytest
from agent_backend.agent.agent_llms.llm import FunctionCallType, LLMClient
from agent_backend.agent.agent_llms.llm_setting_params import LLMParams
from agent_backend.agent.agent_schema.message import Message
from agent_backend.agent.agent_enums.agent_type import RoleType
from agent_backend.agent.agent_core.agent_context import AgentContext
from agent_backend.agent.agent_schema.tool.tool_choise import ToolChoice
from agent_backend.agent.agent_tools.base_tool import BaseTool
from agent_backend.agent.agent_tools.tool_collection import ToolCollection

params = LLMParams(
    # model_name="Qwen/Qwen3-32B-AWQ",
    # api_key="sk-",
    # base_url="http://v1/",
    model_name="Qwen/Qwen3-32B-AWQ",
    api_key="sk-",
    base_url="http:///v1/",
    temperature=0.7,
    max_tokens=8024,
    is_claude=False,
)
messages = [
    Message(
        role=RoleType.USER,
        content="Hello",
    )
]
context = AgentContext(request_id="test-req-id")

# @pytest.mark.asyncio
# async def test_ask_llm_non_stream():
#     llm = LLMClient(params)
#     result = await llm.ask_llm_once(
#         context=context,
#         messages=messages,
#         system_msgs=None,
#     )
#     print(result)

# @pytest.mark.asyncio
# async def test_ask_llm_stream():
#     llm = LLMClient(params)
#     async for chunk in llm.ask_llm_stream(
#         context=context,
#         messages=messages,
#         system_msgs=None,
#     ):
#         print(chunk, end="", flush=True)
        

class DummyAddTool(BaseTool):
    name = "add"
    description = "Add two numbers"

    def to_params(self):
        return {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        }

    def execute(self, tool_input):
        return tool_input["a"] + tool_input["b"]


@pytest.mark.asyncio
async def test_ask_tool_function_call():
    tools = ToolCollection()
    tools.add_tool(DummyAddTool())
    context = AgentContext(request_id="test-fc")
    messages = [Message(role=RoleType.USER, content="Add 1 and 2")]
    system_msgs=Message(role=RoleType.SYSTEM, content="AI助手")
    llm = LLMClient(params)
    # ===== Act =====
    result = await llm.ask_tool(
        context=context,
        messages=messages,
        tools=tools,
        tool_choice=ToolChoice.NONE,
        system_msgs=system_msgs,
        function_call_type=FunctionCallType.STRUCT_PARSE,
    )
    print(result)

asyncio.run(test_ask_tool_function_call())