from dataclasses import dataclass
from .models import Status
import json


@dataclass
class PlannedTask:
    step_id: str
    title: str
    description: str
    dependencies: list[str]
    status: Status = Status.QUEUED


class Tasks:
    def __init__(self, json_response: str, default_dep: str):
        self.tasks: list[PlannedTask] = self.init_tasks(json_response, default_dep)
        self.default_dep = default_dep

    def __iter__(self):
        return iter(self.tasks)

    def __len__(self):
        return len(self.tasks)

    def init_tasks(self, json_response: str, default_dep: str) -> list[PlannedTask]:
        parsed_tasks = self.parse_tasks(json_response, default_dep)
        sorted_tasks = self.topological_sort(parsed_tasks)
        return sorted_tasks

    def parse_tasks(self, json_response: str, default_dep: str) -> list[PlannedTask]:
        try:
            cleaned_response = (
                json_response.replace("```json", "").replace("```", "").strip()
            )
            start = cleaned_response.find("[")
            end = cleaned_response.rfind("]")
            if start != -1 and end != -1:
                cleaned_response = cleaned_response[start : end + 1]

            data = json.loads(cleaned_response)
            tasks = []
            for item in data:
                task = PlannedTask(
                    step_id=item.get("step_id", ""),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    dependencies=item.get("dependencies", default_dep),
                    status=Status.QUEUED,
                )
                if task.dependencies is None or task.dependencies == []:
                    task.dependencies = [default_dep]
                tasks.append(task)
            return tasks
        except Exception as e:
            print(f"Failed to parse json : {e}")
            raise e
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
                if all(
                    dep in [t.step_id for t in sorted_tasks]
                    for dep in task.dependencies
                ):
                    sorted_tasks.append(task)
                    remaining.remove(task)
                    progress = True
                    break

            if not progress:
                sorted_tasks.extend(remaining)
                break

        return sorted_tasks

    def dependencies_met(self, task: PlannedTask) -> bool:
        task_ids = {t.step_id for t in self.tasks}
        task_ids.add(self.default_dep)
        return all(dep in task_ids for dep in task.dependencies)

    def render_tasks(self) -> str:
        plan_desc = "\n**Plan généré :**\n"
        for t in self.tasks:
            plan_desc += f"- {t.step_id}: {t.description}\n"
        plan_desc += "\n"
        return plan_desc
