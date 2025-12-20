from dataclasses import dataclass
from typing import Optional


@dataclass
class McpToolInfo:
    mcp_server_url: Optional[str] = None   # MCP Server 地址
    name: Optional[str] = None             # 工具名称
    desc: Optional[str] = None             # 工具描述
    parameters: Optional[str] = None       # 参数定义（通常是 JSON Schema / 描述串）
