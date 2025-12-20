import asyncio
from openai import AsyncOpenAI
from typing import List, Dict
from agent_backend.agent.agent_llms.llm import LLMParams,TokenCounter
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import RateLimitError, APIConnectionError, Timeout
from agent_backend.agent.agent_core.agent_context import AgentContext
class LLMClient:
    def __init__(self, params: LLMParams):
        self.params = params
        self.client = AsyncOpenAI(
            api_key=params.api_key,
            base_url=params.base_url,
        )

    #messages 构建
    def build_messages(
        self,
        user_prompt: str,
        system_prompt: str | None = None,
        history_messages: List[Dict] | None = None,
    ) -> List[Dict]:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if history_messages:
            messages.extend(history_messages)

        messages.append({"role": "user", "content": user_prompt})
        return messages

    #token截断:倒序贪心+user边界对齐
    def truncate_messages_java_style(
        self,
        messages: List[Dict],
        max_input_tokens: int,
        token_counter: TokenCounter,
    ) -> List[Dict]:
        if not messages or max_input_tokens < 0:
            return messages
        truncated: List[Dict] = []
        remaining_tokens = max_input_tokens
        # 1. 处理 system
        system = messages[0] if messages[0].get("role") == "system" else None
        if system:
            system_tokens = token_counter.count_message_tokens(system)
            remaining_tokens -= system_tokens
        # 2. 从尾部向前贪心截取
        for msg in reversed(messages):
            msg_tokens = token_counter.count_message_tokens(msg)
            if remaining_tokens >= msg_tokens:
                truncated.insert(0, msg)
                remaining_tokens -= msg_tokens
            else:
                break
        # 3. user 对齐：删除开头非 user
        while truncated:
            if truncated[0].get("role") != "user":
                truncated.pop(0)
            else:
                break
        # 4. system 放回最前
        if system:
            truncated.insert(0, system)

        return truncated    
    
    @retry(
        stop=stop_after_attempt(3),                 # 最多重试 3 次
        wait=wait_exponential(multiplier=1, min=2, max=10),  # 指数退避
        retry=retry_if_exception_type(
            (
                RateLimitError,
                APIConnectionError,
                Timeout,
                asyncio.TimeoutError,
            )
        ),
        reraise=True,   # 最终失败时抛出原异常
    )
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        history_messages: List[Dict] | None = None,
    ) -> str:
        #1.messages组装
        messages = self.build_messages(prompt, system_prompt, history_messages)
        #2.messages截断机制
        messages = self.truncate_messages_java_style(messages)

        response = await  asyncio.wait_for(self.client.chat.completions.create(
            model=self.params.model_name,
            messages=messages,
            temperature=self.params.temperature,
            max_tokens=self.params.max_tokens,
            stream=False,
        ),timeout=240)

        return response.choices[0].message.content

