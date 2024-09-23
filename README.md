# AgentFlow

## 项目简介

这是一个基于大型语言模型(LLM)的AI助手项目。它能够执行任务规划、任务执行和结果评估等功能,并支持多种工具的集成使用。

## 主要特性

- 基于 langchain 和 langgraph 实现的最新功能框架！
- 支持langchain自定义工具格式的集成使用
- 工具使用更方便！通过  ToolRegistry 实时注册工具，即插即用
- 支持langgraph 的agent 节点流

## 核心组件

- ` config`: 配置文件，config.yaml配置大模型的选择和密钥
- `agent`: 包含自定义的 agent， 例如 PlannerAgent，ExecuteAgent，EvaluateAgent
- `llm`: LLM调用封装,支持JSON严格输出
- `tool`: 工具注册和管理


## 使用方法

1. python 版本`3.10.14`，安装依赖:
   ```
   pip install -r requirements.txt
   ```

2. 在`config/config.yaml`中配置LLM后端和API密钥

3. 测试运行工作流(示例):
   ```
   python test_workflow.py
   ```

## 配置文件

- `config/prompt_cn.py`: 中文提示词配置
- `requirements.txt`: 项目依赖列表
- `config/config.yaml`: 配置文件
