
# 智能体管理和调度

## agent_core --agent
  Agent 抽象 + 生命周期

## agent_schema --dto
  任务 / 上下文 / 消息 / 结果结构

## agent_enums
  Agent 类型 / 状态 / 策略枚举

## agent_errors --exception
  运行期异常体系

## agent_llms
  LLM 适配与调用（原 llm）

## agent_tracing --printer
  推理过程 / 日志 / 可视化（原 printer）

## agent_prompts
  Prompt 模板与组装（原 prompt）

## agent_tools
  Tool 抽象 / 注册 / 执行（原 tool）

## agent_utils
  通用工具
  date_util.py: 获取当前日期
  file_util.py: 整理易被llm理解的文件结构
  ok_http_util.py: 强 / 弱两类 HTTP 调用<post_json()--弱约束调用（失败可接受）><post_json_body()--强约束调用（失败即错误）>,SSE 同步