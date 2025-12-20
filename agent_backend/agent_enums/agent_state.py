from enum import Enum

"""
agent 状态枚举
"""
class AgentState(Enum):
    IDLE = "IDLE"         # 空闲状态
    RUNNING = "RUNNING"   # 运行状态
    FINISHED = "FINISHED" # 完成状态
    ERROR = "ERROR"       # 错误状态
"""
业务状态
"""
class AutoBotsResultStatus(Enum):
    LOADING = "loading"
    NO = "no"
    RUNNING = "running"
    ERROR = "error"
    FINISHED = "finished"