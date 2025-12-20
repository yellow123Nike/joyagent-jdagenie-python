from agent_backend.agent.agent_llms.llm_setting_params import LLMParams
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)


def _load_json_map(value: str, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception as e:
        logger.error("Failed to parse json config: %s", value, exc_info=e)
        return default


@dataclass
class GenieConfig:
    # ========= Planner / Executor / React Prompts =========
    planner_system_prompt_map: Dict[str, str] = field(default_factory=dict)
    planner_next_step_prompt_map: Dict[str, str] = field(default_factory=dict)

    executor_system_prompt_map: Dict[str, str] = field(default_factory=dict)
    executor_next_step_prompt_map: Dict[str, str] = field(default_factory=dict)
    executor_sop_prompt_map: Dict[str, str] = field(default_factory=dict)

    react_system_prompt_map: Dict[str, str] = field(default_factory=dict)
    react_next_step_prompt_map: Dict[str, str] = field(default_factory=dict)

    # ========= Model Names =========
    planner_model_name: str = "gpt-4o-0806"
    executor_model_name: str = "gpt-4o-0806"
    react_model_name: str = "gpt-4o-0806"

    # ========= Tool Descriptions =========
    plan_tool_desc: str = ""
    code_agent_desc: str = ""
    report_tool_desc: str = ""
    file_tool_desc: str = ""
    deep_search_tool_desc: str = ""
    data_analysis_tool_desc: str = ""

    # ========= Tool Params =========
    plan_tool_params: Dict[str, Any] = field(default_factory=dict)
    code_agent_params: Dict[str, Any] = field(default_factory=dict)
    report_tool_params: Dict[str, Any] = field(default_factory=dict)
    file_tool_params: Dict[str, Any] = field(default_factory=dict)
    deep_search_tool_params: Dict[str, Any] = field(default_factory=dict)
    data_analysis_tool_params: Dict[str, Any] = field(default_factory=dict)

    # ========= Truncate / Limits =========
    file_tool_content_truncate_len: int = 5000
    deep_search_tool_file_desc_truncate_len: int = 500
    deep_search_tool_message_truncate_len: int = 500

    # ========= Prompt Controls =========
    plan_pre_prompt: str = "分析问题并制定计划："
    task_pre_prompt: str = "参考对话历史回答，"
    clear_tool_message: str = "1"
    planning_close_update: str = "1"
    deep_search_page_count: str = "5"

    # ========= Multi Agent =========
    multi_agent_tool_list_map: Dict[str, str] = field(default_factory=dict)

    # ========= LLM Settings =========
    llm_settings_map: Dict[str, LLMParams] = field(default_factory=dict)

    # ========= Step Limits =========
    planner_max_steps: int = 40
    executor_max_steps: int = 40
    react_max_steps: int = 40

    max_observe: str = "10000"

    # ========= URLs =========
    code_interpreter_url: str = ""
    deep_search_url: str = ""
    mcp_client_url: str = ""
    mcp_server_url_arr: List[str] = field(default_factory=list)
    auto_bots_knowledge_url: str = ""
    data_analysis_url: str = ""

    # ========= Summary / Output =========
    summary_system_prompt: str = ""
    digital_employee_prompt: str = ""
    message_size_limit: int = 1000

    sensitive_patterns: Dict[str, str] = field(default_factory=dict)
    output_style_prompts: Dict[str, str] = field(default_factory=dict)
    message_interval: Dict[str, str] = field(default_factory=dict)

    struct_parse_tool_system_prompt: str = ""

    sse_client_read_timeout: int = 1800
    sse_client_connect_timeout: int = 1800

    genie_sop_prompt: str = ""
    genie_base_prompt: str = ""

    task_complete_desc: str = "当前task完成，请将当前task标记为 completed"

    # =====================================================
    # 加载入口（对齐 Spring @Value）
    # =====================================================
    @classmethod
    def load_from_env(cls):
        cfg = cls()

        # -------- Prompt Maps --------
        cfg.planner_system_prompt_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_PLANNER_SYSTEM_PROMPT", ""), {}
        )
        cfg.planner_next_step_prompt_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_PLANNER_NEXT_STEP_PROMPT", ""), {}
        )

        cfg.executor_system_prompt_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_EXECUTOR_SYSTEM_PROMPT", ""), {}
        )
        cfg.executor_next_step_prompt_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_EXECUTOR_NEXT_STEP_PROMPT", ""), {}
        )
        cfg.executor_sop_prompt_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_EXECUTOR_SOP_PROMPT", ""), {}
        )

        cfg.react_system_prompt_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_REACT_SYSTEM_PROMPT", ""), {}
        )
        cfg.react_next_step_prompt_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_REACT_NEXT_STEP_PROMPT", ""), {}
        )

        # -------- Tool Params --------
        cfg.plan_tool_params = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_TOOL_PLAN_TOOL_PARAMS", ""), {}
        )
        cfg.code_agent_params = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_TOOL_CODE_AGENT_PARAMS", ""), {}
        )
        cfg.report_tool_params = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_TOOL_REPORT_TOOL_PARAMS", ""), {}
        )
        cfg.file_tool_params = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_TOOL_FILE_TOOL_PARAMS", ""), {}
        )
        cfg.deep_search_tool_params = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_TOOL_DEEP_SEARCH_PARAMS", ""), {}
        )
        cfg.data_analysis_tool_params = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_TOOL_DATA_ANALYSIS_TOOL_PARAMS", ""), {}
        )

        # -------- Multi Agent --------
        cfg.multi_agent_tool_list_map = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_TOOL_LIST", ""), {}
        )

        # -------- LLM Settings --------
        cfg.llm_settings_map = _load_json_map(
            os.getenv("LLM_SETTINGS", ""), {}
        )

        # -------- Sensitive / Output --------
        cfg.sensitive_patterns = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_SENSITIVE_PATTERNS", ""), {}
        )
        cfg.output_style_prompts = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_OUTPUT_STYLE_PROMPTS", ""), {}
        )
        cfg.message_interval = _load_json_map(
            os.getenv("AUTOBOTS_AUTOAGENT_MESSAGE_INTERVAL", ""), {}
        )

        return cfg
