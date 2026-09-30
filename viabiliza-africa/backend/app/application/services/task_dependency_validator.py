from uuid import UUID

from app.domain.entities.collaboration import TaskDependency
from app.domain.enums.task_status import TaskStatus
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.collaboration_repository import (
    IKanbanTaskRepository,
    ITaskDependencyRepository,
)


class TaskDependencyValidator:
    """Valida dependências e ciclos entre tarefas."""

    def __init__(
        self,
        task_repository: IKanbanTaskRepository,
        dependency_repository: ITaskDependencyRepository,
    ) -> None:
        self._tasks = task_repository
        self._deps = dependency_repository

    def validate_create(
        self,
        project_id: UUID,
        predecessor_id: UUID,
        successor_id: UUID,
    ) -> None:
        if predecessor_id == successor_id:
            raise ValidationError("Uma tarefa não pode depender de si mesma")

        pred = self._tasks.find_by_id(predecessor_id)
        succ = self._tasks.find_by_id(successor_id)
        if pred is None or succ is None:
            raise ValidationError("Tarefa predecessora ou sucessora não encontrada")
        if pred.project_id != project_id or succ.project_id != project_id:
            raise ValidationError("As tarefas devem pertencer ao mesmo projeto")

        if self._deps.exists(predecessor_id, successor_id):
            raise ValidationError("Dependência já existe")

        if self._would_create_cycle(project_id, predecessor_id, successor_id):
            raise ValidationError("Dependência criaria um ciclo entre tarefas")

    def validate_move_to_done(self, task_id: UUID) -> None:
        predecessors = self._deps.find_predecessors(task_id)
        for dep in predecessors:
            task = self._tasks.find_by_id(dep.predecessor_task_id)
            if task and task.status != TaskStatus.DONE:
                raise ValidationError(
                    f"Tarefa bloqueada: '{task.title}' deve ser concluída primeiro"
                )

    def _would_create_cycle(
        self, project_id: UUID, predecessor_id: UUID, successor_id: UUID
    ) -> bool:
        """Se successor pode alcançar predecessor, adicionar aresta cria ciclo."""
        deps = self._deps.find_by_project(project_id)
        graph = self._build_graph(deps)
        graph.setdefault(predecessor_id, set()).add(successor_id)
        return self._can_reach(graph, successor_id, predecessor_id)

    def _build_graph(self, deps: list[TaskDependency]) -> dict[UUID, set[UUID]]:
        graph: dict[UUID, set[UUID]] = {}
        for dep in deps:
            graph.setdefault(dep.predecessor_task_id, set()).add(dep.successor_task_id)
        return graph

    def _can_reach(self, graph: dict[UUID, set[UUID]], start: UUID, target: UUID) -> bool:
        stack = [start]
        visited: set[UUID] = set()
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(graph.get(node, set()))
        return False
