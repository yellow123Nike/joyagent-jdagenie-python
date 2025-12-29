import asyncio
import pytest
from agent_backend.agent.agent_core.agent_context import AgentContext
from agent_backend.agent.agent_core.planning_agent import PlanningImplAgent
from agent_backend.agent.agent_enums.agent_state import AgentState
from agent_backend.agent.agent_llms.llm import LLMClient
from agent_backend.agent.agent_llms.llm_setting_params import LLMParams
from agent_backend.agent.agent_tracing.stdout_printer import StdoutPrinter
from agent_backend.agent_model.req.agent_request import AgentRequest

params = LLMParams(
    model_name="Qwen/Qwen3-32B-AWQ",
    api_key="sk-",
    base_url="http://192.168.88.235:18006/v1/",
    temperature=0.7,
    max_tokens=8024,
    is_claude=False,
)


@pytest.mark.asyncio
async def test_planning_agent_create_and_next_task():
    # ---------- context ----------
    printer = StdoutPrinter(request=AgentRequest(request_id="test-planning"))
    context = AgentContext(
        request_id="test-planning",
        sop_prompt="你是一个 planning agent，负责将复杂任务拆解为可执行步骤。",
        date_info="2025-01-01",
        printer=printer,
    )

    # ---------- agent ----------
    agent = PlanningImplAgent(
        context=context,
        llm=LLMClient(params),
        is_close_update=False,   # 关键：关闭动态更新
    )
    query = (
        "请帮我完成以下任务：\n"
        "我要写一篇关于『强化学习在大模型中的应用』的短文。\n"
        "要求：\n"
        "1. 先列一个写作计划；\n"
        "2. 再逐步完成每个部分；\n"
        "3. 每一步只做当前任务，不要一次性完成。\n"
    )

    # ---------- run ----------

    result = await agent.run(query)

    print("\n----- AGENT RETURN -----")
    print(result)

asyncio.run(test_planning_agent_create_and_next_task())