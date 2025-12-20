import pytest
from agent_backend.agent.agent_llms.llm import LLMClient
from agent_backend.agent.agent_llms.llm_setting_params import LLMParams
from agent_backend.agent.agent_schema.message import Message
from agent_backend.agent.agent_enums.agent_type import RoleType
from agent_backend.agent.agent_core.agent_context import AgentContext

params = LLMParams(
    model_name="Qwen/Qwen3-32B-AWQ",
    api_key="sk-a629905880b04cae83038bdae5c88859",
    base_url="http://192.168.88.235:18006/v1/",
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

@pytest.mark.asyncio
async def test_ask_llm_non_stream():
    llm = LLMClient(params)
    result = await llm.ask_llm_once(
        context=context,
        messages=messages,
        system_msgs=None,
    )
    print(result)

@pytest.mark.asyncio
async def test_ask_llm_stream():
    llm = LLMClient(params)
    async for chunk in llm.ask_llm_stream(
        context=context,
        messages=messages,
        system_msgs=None,
    ):
        print(chunk, end="", flush=True)