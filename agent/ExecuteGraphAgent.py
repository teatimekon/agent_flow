from typing import List, Dict, Optional
from dataclasses import dataclass, field
from graph.state import AgentState
from tool.tool_registry import ToolRegistry
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt_cn import task_execute_default_prompt, task_execute_evaluate_prompt, task_execute_summary_prompt

@dataclass
class TaskNode:
    task_id: int
    task_description: str
    task_type: str
    task_should_output: str
    parents: List['TaskNode'] = field(default_factory=list)
    children: List['TaskNode'] = field(default_factory=list)
    next: Optional['TaskNode'] = None
    prev: Optional['TaskNode'] = None
    task_status: str = "pending"
    task_output: str = ""
    retry_count: int = 0
    max_retries: int = 2

    def __str__(self):
        return f"任务id是：{self.task_id},  \
        任务的描述是：{self.task_description},  \
        任务的类型是：{self.task_type},  \
        任务的输出：{self.task_output} \n"

class ExecuteGraphAgent(BaseAgent):
    def __init__(self, state: AgentState, tool_call: bool = False):
        super().__init__(state=state, tool_call=tool_call)
        self.task_nodes: Dict[int, TaskNode] = {}
        self.head: Optional[TaskNode] = None
        self.tail: Optional[TaskNode] = None
        
    def invoke(self):
        plan_task_list = self.state["plan_task_list"]["task_list"]
        self.build_task_graph(plan_task_list)
        question = self.state["question"]
        
        current_node = self.head
        while current_node:
            if self.is_task_ready(current_node):
                logger.info(f"任务 {current_node.task_id} 准备执行。")
                success = self.execute_task_by_type(current_node, question)
                
                if success:
                    current_node = current_node.next
                else:
                    if current_node.retry_count < current_node.max_retries:
                        current_node.retry_count += 1
                        logger.info(f"任务 {current_node.task_id} 执行失败，正在重试（第 {current_node.retry_count} 次）。")
                    else:
                        logger.error(f"任务 {current_node.task_id} 达到最大重试次数，跳过该任务。")
                        self.reset_dependent_tasks(current_node)
                        current_node = current_node.next
            else:
                logger.info(f"任务 {current_node.task_id} 由于未完成的依赖任务而无法执行。")
                # 将当前任务移到链表末尾
                if current_node.next:
                    self.move_to_end(current_node)
                    current_node = current_node.next
                else:
                    break  # 如果已经是最后一个任务，退出循环
        
        self.update_state(
            execute_task_output=[node.task_output for node in self.task_nodes.values() if node.task_type == "总结问题"], 
            llm_caller_times=self.get_llm_caller_times()
        )
        return self.state

    def is_task_ready(self, node: TaskNode) -> bool:
        return all(parent.task_status == "success" for parent in node.parents)

    def get_dependency_output(self, node: TaskNode) -> str:
        return "\n".join([
            f"依赖任务{parent.task_id}的描述是：{parent.task_description}，输出了下面的内容：{parent.task_should_output}：{parent.task_output}"
            for parent in node.parents
        ])

    def build_task_graph(self, plan_task_list: List[Dict]):
        # 创建所有任务节点
        for task in plan_task_list:
            node = TaskNode(
                task_id=task["task_number"],
                task_description=task["task_description"],
                task_type=task["task_type"],
                task_should_output=task["task_should_output"]
            )
            self.task_nodes[node.task_id] = node
        
        # 建立任务之间的依赖关系
        for task in plan_task_list:
            node = self.task_nodes[task["task_number"]]
            for dep_id in task["dependency_task"]:
                if dep_id != -1:
                    parent = self.task_nodes[dep_id]
                    parent.children.append(node) 
                    node.parents.append(parent)
        
        # 构建链表结构
        sorted_nodes = sorted(self.task_nodes.values(), key=lambda x: x.task_id)
        for i in range(len(sorted_nodes)):
            if i > 0:
                sorted_nodes[i].prev = sorted_nodes[i-1]
            if i < len(sorted_nodes) - 1:
                sorted_nodes[i].next = sorted_nodes[i+1]
        
        self.head = sorted_nodes[0]
        self.tail = sorted_nodes[-1]

    def execute_task_by_type(self, node: TaskNode, question: str) -> bool:
        try:
            if node.task_type == "总结问题":
                self.execute_summary_task(node, question)
            elif node.task_type == "评估问题":
                self.execute_evaluate_task(node, question)
            else:
                self.execute_default_task(node, question)
            
            node.task_status = "success"
            return True
        except Exception as e:
            logger.error(f"执行任务 {node.task_id} 时发生错误：{str(e)}")
            node.task_status = "failed"
            return False

    def reset_dependent_tasks(self, failed_node: TaskNode):
        def reset_subtree(node: TaskNode):
            node.task_status = "pending"
            node.retry_count = 0
            for child in node.children:
                reset_subtree(child)

        for child in failed_node.children:
            reset_subtree(child)

    def move_to_end(self, node: TaskNode):
        if node == self.tail:
            return
        
        # 从当前位置移除
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        
        # 移动到末尾
        self.tail.next = node
        node.prev = self.tail
        node.next = None
        self.tail = node

    # 其他方法（execute_summary_task, execute_evaluate_task, execute_default_task）保持不变
