# joyagent-jdagenie-python
对joyagent-jdagenie架构的学习与改造

# 智能体管理和调度 --genie-backend
  --学习genie-backend
  1.智能体管理和调度：多智能体协作引擎、异步任务处理机制、配置管理和环境隔离
  2.多层次、多模式的协同思考机制：Multi-level：在“工作流”和“具体任务”两个层级进行规划和分解，确保宏观目标与微观执行的一致性。Multi-pattern：融合了 “规划-执行” 与 “React” 两种主流智能体模式，既能做复杂项目规划，也能灵活处理即时交互
  --python代码实现
  PlanningAgent: 任务规划智能体，负责将复杂任务拆解为子任务
  ReactImplAgent: ReAct模式智能体，采用思考-行动-观察循环
  ExecutorAgent: 任务执行智能体，专门执行具体的工作任务
  SummaryAgent: 结果总结智能体，整合多个任务结果

# 部署
conda create -n jd_agent python=3.11
conda activate jd_agent