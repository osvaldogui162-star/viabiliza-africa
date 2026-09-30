import { apiRequest } from "@/lib/api/http-client";

import type {
  ChatMessagesResponse,
  GroupedTasks,
  Task,
  TaskDependency,
  TaskStatus,
} from "@/lib/types/collaboration";

export const collaborationApi = {
  listTasks(projectId: string, grouped = true) {
    return apiRequest<GroupedTasks | { items: Task[] }>(
      `/projects/${projectId}/tasks?grouped=${grouped}`,
      "GET",
    );
  },

  createTask(
    projectId: string,
    payload: { title: string; description?: string; due_date?: string; assignee_id?: string },
  ) {
    return apiRequest<Task>(`/projects/${projectId}/tasks`, "POST", payload);
  },

  updateTask(
    projectId: string,
    taskId: string,
    payload: Partial<{ title: string; description: string; assignee_id: string | null; due_date: string }>,
  ) {
    return apiRequest<Task>(`/projects/${projectId}/tasks/${taskId}`, "PATCH", payload);
  },

  moveTask(projectId: string, taskId: string, status: TaskStatus, position?: number) {
    return apiRequest<Task>(`/projects/${projectId}/tasks/${taskId}/move`, "PATCH", {
      status,
      position,
    });
  },

  deleteTask(projectId: string, taskId: string) {
    return apiRequest<{ message: string }>(`/projects/${projectId}/tasks/${taskId}`, "DELETE");
  },

  listDependencies(projectId: string) {
    return apiRequest<{ items: TaskDependency[]; total: number }>(
      `/projects/${projectId}/tasks/dependencies`,
      "GET",
    );
  },

  createDependency(projectId: string, predecessorId: string, successorId: string) {
    return apiRequest<TaskDependency>(`/projects/${projectId}/tasks/dependencies`, "POST", {
      predecessor_task_id: predecessorId,
      successor_task_id: successorId,
    });
  },

  deleteDependency(projectId: string, dependencyId: string) {
    return apiRequest<{ message: string }>(
      `/projects/${projectId}/tasks/dependencies/${dependencyId}`,
      "DELETE",
    );
  },

  listChatMessages(projectId: string, limit = 50) {
    return apiRequest<ChatMessagesResponse>(
      `/projects/${projectId}/chat/messages?limit=${limit}`,
      "GET",
    );
  },

  sendChatMessage(projectId: string, content: string) {
    return apiRequest<{ id: string; content: string; created_at: string }>(
      `/projects/${projectId}/chat/messages`,
      "POST",
      { content },
    );
  },
};
