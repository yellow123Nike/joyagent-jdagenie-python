from dataclasses import dataclass, field
from typing import List, Optional

from agent_model.dto.file_information import FileInformation


@dataclass
class AgentRequest:
    # ========= 请求级别 =========
    request_id: Optional[str] = None          # 请求唯一标识
    erp: Optional[str] = None                 # 用户/员工标识
    query: Optional[str] = None               # 用户原始问题
    agent_type: Optional[int] = None          # Agent 类型
    base_prompt: Optional[str] = None         # 基础 Prompt
    sop_prompt: Optional[str] = None          # SOP Prompt
    is_stream: Optional[bool] = None          # 是否流式输出
    messages: List["AgentRequest.Message"] = field(default_factory=list)
    output_style: Optional[str] = None        # 交付物产出格式：html(网页模式）， docs(文档模式）， table(表格模式）

    # =============================
    # 内嵌模型：Message
    # =============================
    @dataclass
    class Message:
        role: Optional[str] = None             # user / assistant / system / tool
        content: Optional[str] = None          # 消息内容
        command_code: Optional[str] = None     # 指令/命令码
        upload_file: List["FileInformation"] = field(default_factory=list)
        files: List["FileInformation"] = field(default_factory=list)
