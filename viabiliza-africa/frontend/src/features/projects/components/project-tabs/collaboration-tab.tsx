"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import {
  GitBranch,
  GripVertical,
  Link2,
  MessageSquare,
  Plus,
  Trash2,
  Users,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageLoader } from "@/components/ui/spinner";
import { useAuth } from "@/components/providers/auth-provider";
import { useI18n } from "@/components/providers/locale-provider";
import { ProjectCallout } from "@/features/projects/components/project-callout";
import { ProjectScrollPanel } from "@/features/projects/components/project-scroll-panel";
import { ApiError } from "@/lib/api/http-client";
import { collaborationApi } from "@/lib/api/collaboration-api";
import { notificationsApi } from "@/lib/api/notifications-api";
import { projectsApi } from "@/lib/api/projects-api";
import { formatDateTime } from "@/lib/utils/format";
import type { ChatMessage, GroupedTasks, Task, TaskDependency, TaskStatus } from "@/lib/types/collaboration";
import type { Project, ProjectShare } from "@/lib/types/project";
import { cn } from "@/lib/utils/cn";

const COLUMN_STYLES: Record<TaskStatus, string> = {
  todo: "border-zinc-200 bg-zinc-50/80",
  in_progress: "border-blue-200 bg-blue-50/40",
  review: "border-amber-200 bg-amber-50/40",
  done: "border-emerald-200 bg-emerald-50/40",
};

const POLL_MS = 3500;

export function CollaborationTab({ project }: { project: Project }) {
  const { user } = useAuth();
  const { t, intlLocale } = useI18n();
  const en = intlLocale.startsWith("en");
  const [tasks, setTasks] = useState<GroupedTasks | null>(null);
  const [dependencies, setDependencies] = useState<TaskDependency[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [online, setOnline] = useState<{ user_id: string; name: string }[]>([]);
  const [members, setMembers] = useState<ProjectShare[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTask, setNewTask] = useState("");
  const [newMessage, setNewMessage] = useState("");
  const [dragOver, setDragOver] = useState<TaskStatus | null>(null);
  const [depModal, setDepModal] = useState(false);
  const [predId, setPredId] = useState("");
  const [succId, setSuccId] = useState("");
  const lastMsgId = useRef<string | null>(null);
  const messagesRef = useRef<HTMLDivElement | null>(null);

  const columns = useMemo(
    (): { status: TaskStatus; label: string }[] => [
      { status: "todo", label: t("collaboration.todo") },
      { status: "in_progress", label: t("collaboration.inProgress") },
      { status: "review", label: t("collaboration.review") },
      { status: "done", label: t("collaboration.done") },
    ],
    [t],
  );

  const flatTasks = useMemo(() => {
    if (!tasks) return [];
    return columns.flatMap((c) => tasks[c.status] ?? []);
  }, [tasks, columns]);

  const totalTasks = flatTasks.length;

  const load = useCallback(async () => {
    try {
      const [taskRes, chatRes, depRes, sharesRes] = await Promise.all([
        collaborationApi.listTasks(project.id),
        collaborationApi.listChatMessages(project.id),
        collaborationApi.listDependencies(project.id),
        projectsApi.listShares(project.id).catch(() => ({ items: [] as ProjectShare[] })),
      ]);
      setTasks(taskRes as GroupedTasks);
      setMessages(chatRes.items);
      setDependencies(depRes.items ?? []);
      setMembers(sharesRes.items ?? []);
      if (chatRes.items[0]) lastMsgId.current = chatRes.items[chatRes.items.length - 1]?.id ?? null;
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("collaboration.loadError"));
    } finally {
      setLoading(false);
    }
  }, [project.id, t]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const poll = async () => {
      try {
        const res = await notificationsApi.pollChat(project.id, lastMsgId.current ?? undefined);
        if (res.messages.length) {
          setMessages((prev) => {
            const ids = new Set(prev.map((m) => m.id));
            const merged = [...prev];
            for (const m of res.messages) {
              if (!ids.has(m.id)) merged.push(m as ChatMessage);
            }
            return merged;
          });
          lastMsgId.current = res.messages[res.messages.length - 1].id;
          messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight, behavior: "smooth" });
        }
        setOnline(res.online ?? []);
      } catch {
        /* silent poll */
      }
    };
    void poll();
    const id = window.setInterval(() => void poll(), POLL_MS);
    return () => window.clearInterval(id);
  }, [project.id]);

  useEffect(() => {
    if (messages.length && user) {
      const last = messages[messages.length - 1];
      if (last?.id && !last.id.startsWith("tmp")) {
        void notificationsApi.markChatRead(project.id, last.id);
      }
    }
  }, [messages, project.id, user]);

  async function handleCreateTask() {
    if (!newTask.trim()) return;
    try {
      await collaborationApi.createTask(project.id, { title: newTask });
      setNewTask("");
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("collaboration.createTaskError"));
    }
  }

  async function handleMoveTask(taskId: string, status: TaskStatus) {
    try {
      await collaborationApi.moveTask(project.id, taskId, status);
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("collaboration.moveTaskError"));
    }
  }

  async function handleAssign(task: Task, assigneeId: string) {
    try {
      await collaborationApi.updateTask(project.id, task.id, {
        assignee_id: assigneeId || null,
      });
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("collaboration.moveTaskError"));
    }
  }

  async function handleCreateDependency() {
    if (!predId || !succId) return;
    try {
      await collaborationApi.createDependency(project.id, predId, succId);
      setDepModal(false);
      setPredId("");
      setSuccId("");
      void load();
      toast.success(en ? "Dependency created" : "Dependência criada");
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : en ? "Failed" : "Falha");
    }
  }

  async function handleSendMessage() {
    if (!newMessage.trim()) return;
    const content = newMessage;
    setNewMessage("");
    try {
      const sent = await collaborationApi.sendChatMessage(project.id, content);
      lastMsgId.current = sent.id;
      void load();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("collaboration.sendError"));
    }
  }

  function taskDeps(taskId: string) {
    return dependencies.filter((d) => d.successor_task_id === taskId);
  }

  if (loading) return <PageLoader />;

  return (
    <div className="space-y-4">
      <ProjectCallout variant="neutral" title={t("projectTabs.collaboration")}>
        {totalTasks} {en ? "tasks" : "tarefas"} · {messages.length} {en ? "messages" : "mensagens"}
        {online.length ? ` · ${online.length} ${en ? "online" : "online"}` : ""}
      </ProjectCallout>

      <div className="grid gap-4 xl:grid-cols-12">
        <Card variant="panel" className="xl:col-span-8">
          <CardHeader
            eyebrow={t("collaboration.kanban")}
            title={t("projectTabs.collaboration")}
            description={`${totalTasks} ${en ? "tasks" : "tarefas"}`}
            action={
              <Button size="sm" variant="outline" onClick={() => setDepModal(true)}>
                <GitBranch className="h-3.5 w-3.5" />
                {en ? "Dependencies" : "Dependências"}
              </Button>
            }
          />
          <div className="mb-4 flex gap-2">
            <Input
              placeholder={t("collaboration.newTask")}
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && void handleCreateTask()}
            />
            <Button onClick={() => void handleCreateTask()} className="shrink-0">
              <Plus className="h-4 w-4" />
            </Button>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {columns.map((col) => {
              const colTasks = tasks?.[col.status] ?? [];
              return (
                <div
                  key={col.status}
                  className={cn(
                    "flex max-h-[min(52vh,480px)] flex-col rounded-xl border p-2.5 transition",
                    COLUMN_STYLES[col.status],
                    dragOver === col.status && "ring-2 ring-teal-400",
                  )}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragOver(col.status);
                  }}
                  onDragLeave={() => setDragOver(null)}
                  onDrop={(e) => {
                    setDragOver(null);
                    try {
                      const data = JSON.parse(e.dataTransfer.getData("text/task"));
                      if (data?.id) void handleMoveTask(data.id, col.status);
                    } catch {
                      /* ignore */
                    }
                  }}
                >
                  <p className="mb-2 shrink-0 text-[10px] font-bold uppercase tracking-wide text-zinc-600">
                    {col.label}{" "}
                    <span className="rounded-full bg-white/80 px-1.5 py-0.5 text-zinc-700">{colTasks.length}</span>
                  </p>
                  <div className="min-h-0 flex-1 space-y-2 overflow-y-auto pr-0.5">
                    {colTasks.length === 0 ? (
                      <p className="rounded-lg border border-dashed border-zinc-200/80 bg-white/50 px-2 py-6 text-center text-xs text-zinc-400">
                        {en ? "Drop here" : "Arraste aqui"}
                      </p>
                    ) : (
                      colTasks.map((task) => (
                        <TaskCard
                          key={task.id}
                          task={task}
                          deps={taskDeps(task.id)}
                          flatTasks={flatTasks}
                          members={members}
                          ownerName={project.owner?.full_name}
                          onAssign={(aid) => void handleAssign(task, aid)}
                        />
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {dependencies.length > 0 ? (
            <div className="mt-4 rounded-xl border border-zinc-100 bg-zinc-50/80 p-3">
              <p className="mb-2 flex items-center gap-1 text-xs font-bold uppercase text-zinc-500">
                <Link2 className="h-3.5 w-3.5" />
                {en ? "Task dependencies" : "Dependências entre tarefas"}
              </p>
              <ul className="space-y-1 text-xs text-zinc-600">
                {dependencies.map((d) => {
                  const pred = flatTasks.find((t) => t.id === d.predecessor_task_id);
                  const succ = flatTasks.find((t) => t.id === d.successor_task_id);
                  return (
                    <li key={d.id} className="flex items-center justify-between gap-2 rounded-lg bg-white px-2 py-1.5">
                      <span>
                        {pred?.title ?? "?"} → {succ?.title ?? "?"}
                      </span>
                      <button type="button" onClick={() => void collaborationApi.deleteDependency(project.id, d.id).then(load)}>
                        <Trash2 className="h-3.5 w-3.5 text-rose-500" />
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : null}
        </Card>

        <Card variant="panel" className="flex flex-col xl:col-span-4">
          <CardHeader
            eyebrow={t("collaboration.chat")}
            title={t("collaboration.chat")}
            description={
              online.length
                ? `${online.map((o) => o.name.split(" ")[0]).join(", ")} ${en ? "online" : "online"}`
                : undefined
            }
          />
          {online.length ? (
            <div className="mb-2 flex flex-wrap gap-1">
              {online.map((o) => (
                <span key={o.user_id} className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
                  <span className="va-live-dot h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  {o.name.split(" ")[0]}
                </span>
              ))}
            </div>
          ) : null}
          <ProjectScrollPanel ref={messagesRef} maxHeight="max-h-[min(44vh,420px)]" className="mb-3 flex-1 bg-zinc-50/50 p-2">
            {messages.length === 0 ? (
              <EmptyState compact title={t("collaboration.messagePlaceholder")} />
            ) : (
              <div className="space-y-2">
                {messages.map((msg) => {
                  const isMe = msg.user_id === user?.id;
                  return (
                    <div
                      key={msg.id}
                      className={cn(
                        "rounded-xl border p-3 text-sm shadow-sm",
                        isMe ? "ml-4 border-teal-100 bg-teal-50/80" : "mr-4 border-zinc-100 bg-white",
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-800">
                          {msg.user_name.charAt(0).toUpperCase()}
                        </span>
                        <p className="font-semibold text-teal-800">{msg.user_name}</p>
                      </div>
                      <p className="mt-2 leading-relaxed text-zinc-700">{msg.content}</p>
                      <p className="mt-1.5 text-[10px] text-zinc-400">{formatDateTime(msg.created_at, intlLocale)}</p>
                    </div>
                  );
                })}
              </div>
            )}
          </ProjectScrollPanel>
          <div className="flex shrink-0 gap-2">
            <Input
              placeholder={t("collaboration.messagePlaceholder")}
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && void handleSendMessage()}
            />
            <Button onClick={() => void handleSendMessage()} className="shrink-0">
              <MessageSquare className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      </div>

      <Modal
        open={depModal}
        onClose={() => setDepModal(false)}
        title={en ? "New dependency" : "Nova dependência"}
        footer={<Button onClick={() => void handleCreateDependency()}>{en ? "Create" : "Criar"}</Button>}
      >
        <div className="space-y-3">
          <label className="block text-xs font-semibold text-zinc-600">{en ? "Predecessor" : "Predecessora"}</label>
          <select className="w-full rounded-xl border px-3 py-2 text-sm" value={predId} onChange={(e) => setPredId(e.target.value)}>
            <option value="">—</option>
            {flatTasks.map((t) => (
              <option key={t.id} value={t.id}>{t.title}</option>
            ))}
          </select>
          <label className="block text-xs font-semibold text-zinc-600">{en ? "Successor" : "Sucessora"}</label>
          <select className="w-full rounded-xl border px-3 py-2 text-sm" value={succId} onChange={(e) => setSuccId(e.target.value)}>
            <option value="">—</option>
            {flatTasks.map((t) => (
              <option key={t.id} value={t.id}>{t.title}</option>
            ))}
          </select>
        </div>
      </Modal>
    </div>
  );
}

function TaskCard({
  task,
  deps,
  flatTasks,
  members,
  ownerName,
  onAssign,
}: {
  task: Task;
  deps: TaskDependency[];
  flatTasks: Task[];
  members: ProjectShare[];
  ownerName?: string;
  onAssign: (id: string) => void;
}) {
  const pendingDeps = deps.filter((d) => {
    const pred = flatTasks.find((t) => t.id === d.predecessor_task_id);
    return pred && pred.status !== "done";
  });

  return (
    <div
      className="group rounded-lg border border-white/80 bg-white p-3 text-sm shadow-sm transition hover:shadow-md"
      draggable
      onDragStart={(e) => e.dataTransfer.setData("text/task", JSON.stringify({ id: task.id, from: task.status }))}
    >
      <div className="flex items-start gap-2">
        <GripVertical className="mt-0.5 h-4 w-4 shrink-0 cursor-grab text-zinc-300 opacity-0 transition group-hover:opacity-100" />
        <div className="min-w-0 flex-1">
          <p className="font-semibold leading-snug text-zinc-900">{task.title}</p>
          {pendingDeps.length ? (
            <p className="mt-1 text-[10px] font-medium text-amber-700">
              {pendingDeps.length} dep. pendente(s)
            </p>
          ) : null}
          <div className="mt-2 flex items-center gap-2">
            <Users className="h-3.5 w-3.5 text-zinc-400" />
            <select
              className="max-w-full truncate rounded-md border border-zinc-100 bg-zinc-50 px-1.5 py-0.5 text-[10px]"
              value={task.assignee_id ?? ""}
              onChange={(e) => onAssign(e.target.value)}
              onClick={(e) => e.stopPropagation()}
            >
              <option value="">{ownerName ?? "—"}</option>
              {members.map((m) => (
                <option key={m.user_id} value={m.user_id}>{m.user_full_name ?? m.user_email}</option>
              ))}
            </select>
          </div>
          {task.assignee_name ? (
            <p className="mt-1 text-xs text-teal-700">{task.assignee_name}</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
