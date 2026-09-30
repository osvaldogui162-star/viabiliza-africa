export type NotificationType =
  | "chat_message"
  | "chat_mention"
  | "report_ready"
  | "project_shared"
  | "payment_confirmed"
  | "subscription_expiring"
  | "system";

export interface AppNotification {
  id: string;
  type: NotificationType;
  title: string;
  body?: string | null;
  href?: string | null;
  project_id?: string | null;
  metadata?: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

export interface NotificationsResponse {
  items: AppNotification[];
  total: number;
  unread_count: number;
}

export interface ChatOnlineUser {
  user_id: string;
  name: string;
}

export interface ChatPollResponse {
  messages: Array<{
    id: string;
    project_id: string;
    user_id: string;
    user_name: string;
    content: string;
    created_at: string;
  }>;
  online: ChatOnlineUser[];
}
