from dataclasses import dataclass
from .models import Status
import json

@dataclass
class PlannedTask:
    id: str
    title: str
    description: str
    dependencies: list[str]
    status: Status = Status.QUEUED

class Tasks:

    def __init__(self, json_response):
        self.tasks: list[PlannedTask] = self.init_taks(json_response)

    def __iter__(self):
        return iter(self.tasks)

    def __len__(self):
        return len(self.tasks)

    def init_taks(self, json_response: str) -> list[PlannedTask]:
        parsed_tasks = self.parse_tasks(json_response)
        sorted_tasks = self.topological_sort(parsed_tasks)
        return sorted_tasks

    def parse_tasks(self, json_response: str) -> list[PlannedTask]:
        try:
            cleaned_response = json_response.replace("```json", "").replace("```", "").strip()
            start = cleaned_response.find("[")
            end = cleaned_response.rfind("]")
            if start != -1 and end != -1:
                cleaned_response = cleaned_response[start:end+1]
                
            data = json.loads(cleaned_response)
            tasks = []
            for item in data:
                task = PlannedTask(
                    id=item.get("id", str(item.get("step", "unknown"))),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    dependencies=item.get("dependencies", []),
                )
                tasks.append(task)
            return tasks
        except Exception as e:
            print(f"Failed to parse json : {e}")
            return []

    def topological_sort(self, tasks: list[PlannedTask]) -> list[PlannedTask]:
        sorted_tasks = []
        remaining = tasks.copy()
        
        max_iterations = len(tasks) * 2
        iterations = 0
        
        while remaining and iterations < max_iterations:
            iterations += 1
            progress = False
            for task in remaining:
                if all(dep in [t.id for t in sorted_tasks] for dep in task.dependencies):
                    sorted_tasks.append(task)
                    remaining.remove(task)
                    progress = True
                    break
            
            if not progress:
                sorted_tasks.extend(remaining)
                break
                
        return sorted_tasks

    def dependencies_met(self, task: PlannedTask) -> bool:
        task_ids = {t.id for t in self.tasks}
        return all(dep in task_ids for dep in task.dependencies)

    def render_tasks(self) -> str:
        plan_desc = "\n**Plan généré :**\n"
        for t in self.tasks:
            plan_desc += f"- {t.id}: {t.description}\n"
        plan_desc += "\n"
        return plan_desc
