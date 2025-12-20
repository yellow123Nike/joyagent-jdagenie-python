import asyncio
import json
import logging
from openai import AsyncOpenAI
from typing import Any, List, Dict, Optional
import tiktoken
from agent_backend.agent.agent_llms.llm_setting_params import LLMParams
from agent_backend.agent.agent_core.agent_context import AgentContext
from agent_backend.agent.agent_schema.message import Message
from agent_backend.agent.agent_util.app_context import ApplicationContextHolder
from agent_backend.agent.agent_util.string_util import text_desensitization
from agent_backend.agent_config.genie_config import GenieConfig
from agent_backend.agent.agent_util.ok_http_util import OkHttpUtil
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import RateLimitError, APIConnectionError, Timeout
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, params: LLMParams):
        self.params = params
        self.is_claude=params.is_claude
        self.client = AsyncOpenAI(
            api_key=params.api_key,
            base_url=params.base_url,
        )

    #格式化消息
    def format_messages(
        self,
        messages: List[Message],
        is_claude: bool,
    ):
        formatted = []
        for msg in messages:
            message_map: Dict[str, Any] = {}
            # ===== multimodal =====
            # 1.处理 base64 图像
            if msg.base64_image:
                multimodal = []
                multimodal.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{msg.base64_image}"
                    }
                })
                multimodal.append({
                    "type": "text",
                    "text": msg.content
                })

                message_map["role"] = msg.role.value
                message_map["content"] = multimodal

            # ===== tool calls =====
            #Claude 把「工具调用」当作一种消息类型（content block），
            #GPT 把「工具调用」当作 message 的一个字段（tool_calls）
            elif msg.tool_calls:
                message_map["role"] = msg.role.value

                if is_claude:
                    claude_calls = []
                    for tc in msg.tool_calls:
                        claude_calls.append({
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.function.name,
                            "input": json.loads(tc.function.arguments),
                        })
                    message_map["content"] = claude_calls
                else:
                    message_map["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in msg.tool_calls
                    ]

            # ===== tool result =====
            elif msg.tool_call_id:
                genie_config: GenieConfig = ApplicationContextHolder.get("genie_config")
                content = text_desensitization(
                    msg.content,
                    genie_config.sensitive_patterns,
                )

                if is_claude:
                    message_map["role"] = "user"
                    message_map["content"] = [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": content,
                    }]
                else:
                    message_map["role"] = msg.role.value
                    message_map["content"] = content
                    message_map["tool_call_id"] = msg.tool_call_id

            # ===== normal text =====
            else:
                message_map["role"] = msg.role.value
                message_map["content"] = msg.content

            formatted.append(message_map)

        return formatted
    
    def count_message_tokens(self, message: Dict[str, Any]) -> int:
        """
        统计单条 message 的 token 数
        """
        try:
            encoding = tiktoken.encoding_for_model(self.params.model_name)
        except KeyError:
            # fallback（非常重要，避免模型名不识别）
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = 0
        # role tokens（OpenAI 固定开销）
        tokens += 4  # 每条 message 的结构开销
        content = message.get("content", "")
        if isinstance(content, list):
            for item in content:
                if item.get("type") == "text":
                    tokens += len(encoding.encode(item.get("text", "")))
                elif item.get("type") == "image_url":
                    tokens += 85
        else:
            tokens += len(encoding.encode(str(content)))

        return tokens    

    #token截断:倒序贪心+user边界对齐
    def truncate_message(
        self,
        context:AgentContext,
        messages: List[Dict[str, Any]],
        max_input_tokens: int
    ):
        if not messages or max_input_tokens < 0:
            return messages

        logger.info(
            "%s before truncate %s",
            context.request_id,
            json.dumps(messages, ensure_ascii=False),
        )

        truncated_messages: List[Dict[str, Any]] = []
        remaining_tokens = max_input_tokens

        system = messages[0]
        if system.get("role") == "system":
            remaining_tokens -= self.count_message_tokens(system)

        # 从后往前取
        for message in reversed(messages):
            message_tokens = self.count_message_tokens(message)
            if remaining_tokens >= message_tokens:
                truncated_messages.insert(0, message)
                remaining_tokens -= message_tokens
            else:
                break

        # 保证第一条非 system 消息是 user
        while truncated_messages:
            first = truncated_messages[0]
            if first.get("role") != "user":
                truncated_messages.pop(0)
            else:
                break

        if system.get("role") == "system":
            truncated_messages.insert(0, system)

        logger.info(
            "%s after truncate %s",
            context.request_id,
            json.dumps(truncated_messages, ensure_ascii=False),
        )

        return truncated_messages

    def _prepare_messages(
        self,
        context: AgentContext,
        messages: List[Message],
        system_msgs: Optional[List[Message]],
    ) -> List[dict]:
        # -------- 1.1 格式化 messages --------
        if system_msgs:
            formatted_system_msgs = self.format_messages(
                system_msgs,
                is_claude=self.is_claude,
            )
            formatted_messages = list(formatted_system_msgs)
            formatted_messages.extend(
                self.format_messages(messages, is_claude=self.is_claude)
            )
        else:
            formatted_messages = self.format_messages(
                messages,
                is_claude=self.is_claude,
            )
        # -------- 1.2 截断输入 --------
        if self.params.max_tokens is not None:
            formatted_messages = self.truncate_message(
                context=context,
                messages=formatted_messages,
                max_input_tokens=self.params.max_tokens,
            )

        return formatted_messages

    async def ask_llm_once(
        self,
        context: AgentContext,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
    ) -> str:
        try:
            formatted_messages = self._prepare_messages(
                context, messages, system_msgs
            )

            params = {"messages": formatted_messages, "stream": False}

            response = await self.call_openai(params)

            if (
                not response
                or not response.choices
                or response.choices[0].message.content is None
            ):
                raise ValueError("Empty or invalid response from LLM")

            return response.choices[0].message.content

        except Exception:
            logger.exception("%s ask_llm_once failed", context.request_id)
            raise

    async def ask_llm_stream(
        self,
        context: AgentContext,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
    ):
        try:
            formatted_messages = self._prepare_messages(
                context, messages, system_msgs
            )

            params = {"messages": formatted_messages, "stream": True}

            async for chunk in self.call_openai_stream(params):
                yield chunk

        except Exception:
            logger.exception("%s ask_llm_stream failed", context.request_id)
            raise


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
    async def call_openai(
        self,
        params
    ):
        response = await  asyncio.wait_for(self.client.chat.completions.create(
            model=self.params.model_name,
            messages=params["messages"],
            temperature=self.params.temperature,
            max_tokens=self.params.max_tokens,
            stream=params["stream"],
        ),timeout=240)

        return response


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
    async def call_openai_stream(
        self,
        params
    ):
        response = await  asyncio.wait_for(self.client.chat.completions.create(
            model=self.params.model_name,
            messages=params["messages"],
            temperature=self.params.temperature,
            max_tokens=self.params.max_tokens,
            stream=params["stream"],
        ),timeout=240)

        async for event in response:
            choice = event.choices[0]
            delta = choice.delta

            if delta and delta.content:
                yield delta.content

