
# 智能体管理和调度

## agent_core --agent
  Agent 抽象 + 生命周期

### ReAct-Agent
  react三段式思想：多轮循环(思考<Thought>--行动<Action>--观察<Observation>)--明确Finish
  react以搜索为例的行为链路：搜索主体--发现信息不足--细化搜索--聚焦指标--Finish

  prompt约定式react：ReAct结构存在于Prompt文本中(用自然语言告诉模型：你应该按 Thought / Action / Observation 来做事)。
  显式状态机式ReAct：Thought / Action / Observation的每个过程都是一个可判定、可执行的状态，控制权留在系统侧。
    --Think:纯决策，只产生意图与计划。通过system_prompt约束的整体任务策略下运行，通过next_step_prompt驱动模型判断是否需要继续调用工具
    --act:执行工具，只负责按照 Think 阶段给出的计划调用工具并记录观察结果；由系统基于结构化信号（如 tool_calls 是否为空）统一判断任务是否结束。
  
  任务什么时候结束：1.step约束(两者都有)，2.自动停(prompt约定式是祈祷模型听话,显式状态机式是让模型只判断是否需要调用工具，系统再来确实是否执行还是结束，明确 Finish 是系统判定，不是模型判定)

test_react_impl_agent()的react过程：
| 序号 | Role      | 内容摘要                                       | Tool 调用        | Tool 返回             |
| -- | --------- | ------------------------------------------ | -------------- | ------------------- |
| 1  | USER      | 提出四步计算任务：①1–100 平方和②+123③÷7④只给结果；要求复杂计算用工具 | 否              | —                   |
| 2  | ASSISTANT | 内部思考：说明将使用工具计算平方和、加法与除法                    | 是（python_calc） | —                   |
| 3  | TOOL      | 执行 `sum(i*i for i in range(1,101)) + 123`  | —              | `338473`            |
| 4  | USER      | 要求根据当前状态判断是否完成任务，给出思考并继续                   | 否              | —                   |
| 5  | ASSISTANT | 思考：任务未完成，需将 338473 ÷ 7，决定再次调用工具            | 是（python_calc） | —                   |
| 6  | TOOL      | 执行 `338473 / 7`                            | —              | `48353.28571428572` |
| 7  | USER      | 再次要求判断任务是否完成并给出下一步                         | 否              | —                   |
| 8  | ASSISTANT | 思考：四个步骤均已完成，给出最终结果并结束任务                    | 否              | 最终结果                |


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