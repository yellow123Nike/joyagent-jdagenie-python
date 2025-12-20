import tiktoken
from typing import Optional,Dict, Any
from pydantic import BaseModel, Field

class LLMParams(BaseModel):
    """LLM的可配置参数"""
    # 模型基础配置
    model_name: str = Field(description="模型名称")
    api_key: str = Field(description="APIkey")
    base_url: str = Field(description="API URL")
    # 模型生成行为配置
    temperature: Optional[float] = Field(
        default=0.7, description="生成随机性:(0:确定性输出,0.7:平衡随机性,2:高度随机)")
    max_tokens: Optional[int] = Field(
        default=8096, description="限制生成的最大 token数")
    # 输出配置
    n: Optional[int] = Field(
        default=1, description="生成多个候选回复(默认 1,增加会提高成本)")
    stream: Optional[bool] = Field(
        default=False, description="是否流式传输结果（实时逐字返回，适用于聊天界面)")


class TokenCounter:
    """
    OpenAI 风格 token 计数器
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # fallback（非常重要，避免模型名不识别）
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_message_tokens(self, message: Dict[str, Any]) -> int:
        """
        统计单条 message 的 token 数
        """
        tokens = 0
        # role tokens（OpenAI 固定开销）
        tokens += 4  # 每条 message 的结构开销
        content = message.get("content", "")
        if isinstance(content, list):
            for item in content:
                if item.get("type") == "text":
                    tokens += len(self.encoding.encode(item.get("text", "")))
                elif item.get("type") == "image_url":
                    tokens += 85
        else:
            tokens += len(self.encoding.encode(str(content)))

        return tokens