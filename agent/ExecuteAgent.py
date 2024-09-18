from typing import List, Dict, Tuple
from dataclasses import dataclass
from graph.state import AgentState
from tool.tool_registry import ToolRegistry
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt_cn import task_execute_default_prompt, task_execute_evaluate_prompt,task_execute_summary_prompt

@dataclass
class Task:
    task_id: int
    task_description: str
    task_type: str
    task_dependency: List[int]
    task_should_output: str
    task_status: str = "pending"
    task_output: str = ""
    def __str__(self):
        return f"任务id是：{self.task_id},  \
        任务的描述是：{self.task_description},  \
        任务的类型是：{self.task_type},  \
        任务的依赖步骤是：{self.task_dependency},  \
        任务的输出：{self.task_output} \n"

class ExecuteAgent(BaseAgent):
    def __init__(self, state: AgentState, tool_call: bool = False):
        super().__init__(state=state, tool_call=tool_call)
        
        
    def invoke(self):
        plan_task_list = self.state["plan_task_list"]["task_list"]
        task_dict, task_list = self.convert_task_dict(plan_task_list)   #一个是根据task_id映射的task，一个是task列表
        question = self.state["question"]
        for task in task_list:
            if self.is_task_ready(task, task_dict):
                logger.info(f"Task {task.task_id} is ready to execute.")
                self.execute_task_by_type(task, task_dict, question)
                 
            else:
                logger.info(f"Task {task.task_id} is not ready to execute due to uncompleted dependencies.")
                
        self.update_state(
            execute_task_output=[task.task_output for task in task_list if task.task_type == "总结问题"], 
            llm_caller_times=self.get_llm_caller_times()
        )
        return self.state

    def is_task_ready(self, task: Task, task_dict: Dict[int, Task]) -> bool:
        return all(task_dict[dep_id].task_status == "success" for dep_id in task.task_dependency if dep_id != -1)

    def get_dependency_output(self, task: Task, task_dict: Dict[int, Task]) -> str:
        return "\n".join(
            f"依赖任务{dep_id}的描述是：{task_dict[dep_id].task_description}，输出了下面的内容：{task_dict[dep_id].task_should_output}：{task_dict[dep_id].task_output}"
            for dep_id in task.task_dependency
            if dep_id != -1
        )

    def convert_task_dict(self, plan_task_list: List[Dict]) -> Tuple[Dict[int, Task], List[Task]]:
        task_dict = {}
        task_list = []
        for task in plan_task_list:
            new_task = Task(
                task["task_number"],
                task["task_description"],
                task["task_type"],
                task["dependency_task"],
                task["task_output"]
            )
            task_dict[task["task_number"]] = new_task
            task_list.append(new_task)
        return task_dict, task_list
    
    def execute_task_by_type(self, task: Task, task_dict: Dict[int, Task], question: str):
        #总结、评估和其他
        if task.task_type == "总结问题":
            self.execute_summary_task(task,task_dict,question)
        elif task.task_type == "评估问题":
            self.execute_evaluate_task(task,task_dict,question)
        else:
            self.execute_default_task(task, task_dict, question)

    def execute_summary_task(self, task: Task,task_dict: Dict[int, Task],question: str):
        # 执行 summary 任务的操作
        task_id = task.task_id
        task_type = task.task_type
        task_description = task.task_description
        
        # 构建prompt
        all_task_result = ""
        for _task in task_dict.values():
            all_task_result += str(_task)
            
        summary_prompt = task_execute_summary_prompt.format(
            question=question,
            all_task_result=all_task_result
        )
        logger.info(f"\033[0;35m execute_prompt:{summary_prompt} \033[0m") 
        
        # 调用大模型
        ai_msg = self.llm.invoke(summary_prompt).content
        task.task_output = ai_msg
        task.task_status = "success"
        logger.info(f"\033[0;34m Summary task_output:{ai_msg} \033[0m")  
        
    def execute_evaluate_task(self, task: Task,task_dict: Dict[int, Task],question: str):
        # 执行 evaluate 任务的操作
        task_id = task.task_id
        task_type = task.task_type
        task_description = task.task_description
        
        summary_task_output = [_task.task_output for _task in task_dict.values() if _task.task_type == "总结问题"]
        
        feedback = ""
        # 构建prompt
        evaluate_prompt = task_execute_evaluate_prompt.format( 
            question=question,
            summary_task_output=str(summary_task_output),
            feedback=feedback
        )
        
        logger.info(f"\033[0;35m execute_prompt:{evaluate_prompt} \033[0m") 
        
        # 调用大模型
        ai_msg = self.llm.invoke(evaluate_prompt).content
        task.task_output = ai_msg
        task.task_status = "success"
        logger.info(f"\033[0;34m Evaluate task_output:{ai_msg} \033[0m")  

    def execute_default_task(self, task: Task, task_dict: Dict[int, Task],question: str):
        # 执行默认任务的操作
        task_id = task.task_id
        task_type = task.task_type
        task_description = task.task_description
        # 获取依赖任务的输出
        dependency_task_output = self.get_dependency_output(task, task_dict)
        
        # 构建prompt
        execute_prompt = task_execute_default_prompt.format(
            question=question,
            task_description=task_description,
            dependency_task_output=dependency_task_output
        )
        
        logger.info(f"\033[0;35m execute_prompt:{execute_prompt} \033[0m") 
        
        # 调用大模型
        ai_msg = self.llm.invoke(execute_prompt)
        task_output = ""
        if ai_msg.tool_calls:   #如果ai_msg有tool_calls，说明需要调用工具
            logger.info(f"\033[0;34m tool_calls:{ai_msg.tool_calls} \033[0m")  
            for tool_call in ai_msg.tool_calls:
                selected_tool = ToolRegistry._tools[tool_call["name"].lower()]
                tool_msg = selected_tool.invoke(tool_call).content
                task_output += tool_msg
        else:   #否则说明走的是大模型直接回答的路线
            task_output = ai_msg.content
            
        task.task_output = task_output
        
        task.task_status = "success"
        logger.info(f"\033[0;33m task_output:{task_output} \033[0m")  
        logger.info(f"\033[1;32;40m Task {task_id} is already executed.\n ai_msg:{ai_msg}\033[0m") 
        