import json
import re
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from agent_backend.agent.agent_core.baseagent import BaseAgent
from agent_backend.agent.agent_schema.message import Message

class ReActAgent(BaseAgent, ABC):
    """
    ReAct Agent
    基于 ReAct（Think → Act）模式的智能代理
    """

    @abstractmethod
    async def think(self) -> bool:
        """
        思考阶段：判断是否需要执行行动
        """
        raise NotImplementedError

    @abstractmethod
    async def act(self) -> str:
        """
        行动阶段：执行具体操作（工具 / LLM）
        """
        raise NotImplementedError

    async def step(self) -> str:
        should_act = await self.think()
        if not should_act:
            return "Thinking complete - no action needed"
        return await self.act()

    async def generate_digital_employee(self, task: str):
        # 1. 参数检查
        if not task:
            return

        try:
            # 2. 构建系统 Prompt
            formatted_prompt = self._format_system_prompt(task)
            user_message = Message.user_message(formatted_prompt)

            # 3. 调用 LLM
            llm_response = await self.llm.ask_llm_once(
                context=self.context,
                messages=[user_message],
                system_msgs=[], 
            )

            print(
                f"requestId: {self.context.request_id} "
                f"task:{task} "
                f"generateDigitalEmployee: {llm_response}"
            )

            # 4. 解析 JSON
            json_obj = self._parse_digital_employee(llm_response)
            if json_obj:
                print(
                    f"requestId:{self.context.request_id} "
                    f"generateDigitalEmployee parsed: {json_obj}"
                )
                self.context.tool_collection.update_digital_employee(json_obj)
                self.context.tool_collection.set_current_task(task)

                # 更新可用工具
                self.available_tools = self.context.tool_collection
            else:
                print(
                    f"requestId: {self.context.request_id} "
                    f"generateDigitalEmployee failed"
                )

        except Exception as e:
            print(
                f"requestId: {self.context.request_id} "
                f"in generateDigitalEmployee failed: {e}"
            )

    def _parse_digital_employee(self, response: str):
        """
        支持：
         * 格式一：
         *      ```json
         *      {
         *          "file_tool": "市场洞察专员"
         *      }
         *      ```
         * 格式二：
         *      {
         *          "file_tool": "市场洞察专员"
         *      }
        """
        if not response:
            return None

        json_string = response

        match = re.search(r"```\\s*json([\\s\\S]+?)```", response)
        if match:
            json_string = match.group(1).strip()

        try:
            return json.loads(json_string)
        except Exception as e:
            print(
                f"requestId: {self.context.request_id} "
                f"parseDigitalEmployee error: {e}"
            )
            return None

    def _format_system_prompt(self, task: str) -> str:
            digital_employee_prompt = self.digital_employee_prompt
            if not digital_employee_prompt:
                raise RuntimeError("Digital employee prompt is not configured")

            tool_desc = []
            for tool in self.context.tool_collection.tool_map.values():
                tool_desc.append(
                    f"工具名：{tool.name} 工具描述：{tool.description}"
                )

            return (
                digital_employee_prompt
                .replace("{{task}}", task)
                .replace("{{ToolsDesc}}", "\n".join(tool_desc))
                .replace("{{query}}", self.context.query)
            )