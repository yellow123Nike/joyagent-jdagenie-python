
# 智能体管理和调度

## agent_core --agent
  Agent 抽象 + 生命周期

## agent_schema --dto
  任务 / 上下文 / 消息 / 结果结构

## agent_enums
  Agent 类型：
  | AgentType         | 数值 | 对应智能体                         | 核心职责说明                                            |
| ----------------- | -: | ----------------------------- | ------------------------------------------------- |
| **COMPREHENSIVE** |  1 | **SummaryAgent（综合智能体）**       | 负责整合多个子任务或多个智能体的输出，形成**最终统一结果**，强调“汇总、归纳、整合、裁决”   |
| **WORKFLOW**      |  2 | **ExecutorAgent（执行智能体）**      | 负责**具体任务执行**，按照既定流程或指令完成某一步工作，不做高层规划              |
| **PLAN_SOLVE**    |  3 | **PlanningAgent（任务规划智能体）**    | 将复杂问题拆解为**可执行的子任务序列**，输出计划或 DAG                   |
| **ROUTER**        |  4 | **RouterAgent（路由/调度智能体）**     | 根据问题类型或上下文，**选择/调度合适的 Agent**                     |
| **REACT**         |  5 | **ReactImplAgent（ReAct 智能体）** | 采用 **Thought → Action → Observation** 循环，边思考边调用工具 |
   
  Agent状态：
  | 状态名          | 值            | 含义说明                        | 典型触发场景               | 后续可转移状态              |
| ------------ | ------------ | --------------------------- | -------------------- | -------------------- |
| **IDLE**     | `"IDLE"`     | 空闲状态，智能体未执行任何任务，处于可接收新请求的状态 | 初始化完成；上一轮任务结束并重置     | `RUNNING`            |
| **RUNNING**  | `"RUNNING"`  | 运行状态，智能体正在执行任务（规划、推理、工具调用等） | 调用 `run()` 或开始处理用户请求 | `FINISHED` / `ERROR` |
| **FINISHED** | `"FINISHED"` | 完成状态，智能体已成功完成当前任务并生成结果      | 正常执行完所有步骤            | `IDLE`（重置后）          |
| **ERROR**    | `"ERROR"`    | 错误状态，执行过程中发生异常或不可恢复错误       | 工具调用失败；推理异常；超时       | `IDLE`（重试） / 终止      |


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