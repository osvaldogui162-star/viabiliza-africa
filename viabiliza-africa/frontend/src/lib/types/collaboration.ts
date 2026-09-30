export type TaskStatus = "todo" | "in_progress" | "review" | "done";

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  assignee_id: string | null;
  assignee_name: string | null;
  due_date: string | null;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface TaskDependency {
  id: string;
  project_id: string;
  predecessor_task_id: string;
  successor_task_id: string;
  created_at: string;
}

export interface GroupedTasks {
  todo: Task[];
  in_progress: Task[];
  review: Task[];
  done: Task[];
}

export interface ChatMessage {
  id: string;
  project_id: string;
  user_id: string;
  user_name: string;
  content: string;
  created_at: string;
}

export interface ChatMessagesResponse {
  items: ChatMessage[];
  total: number;
}
