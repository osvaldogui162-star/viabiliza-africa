"""Serviço central de notificações in-app."""

from __future__ import annotations

import re
from uuid import UUID

from app.domain.enums.user_role import UserRole
from app.domain.repositories.notification_repository import INotificationRepository
from app.domain.repositories.user_repository import IUserRepository


_MENTION_RE = re.compile(r"@([\w\u00C0-\u024F.-]+)")


class NotificationService:
    def __init__(
        self,
        notification_repository: INotificationRepository,
        user_repository: IUserRepository,
    ) -> None:
        self._notifications = notification_repository
        self._users = user_repository

    def notify(
        self,
        *,
        user_id: UUID,
        type: str,
        title: str,
        body: str | None = None,
        href: str | None = None,
        project_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> None:
        self._notifications.create(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            href=href,
            project_id=project_id,
            metadata=metadata,
        )

    def notify_chat_message(
        self,
        *,
        project_id: UUID,
        project_name: str,
        sender_id: UUID,
        sender_name: str,
        content: str,
        member_ids: list[UUID],
    ) -> None:
        """Notifica todos os membros do projecto (excepto o remetente)."""
        preview = content[:200]
        for uid in {m for m in member_ids if m and m != sender_id}:
            self.notify(
                user_id=uid,
                type="chat_message",
                title=f"Nova mensagem de {sender_name}",
                body=preview,
                href=f"/projects/{project_id}?tab=collaboration",
                project_id=project_id,
                metadata={"sender_id": str(sender_id), "project_name": project_name},
            )

    def notify_chat_mentions(
        self,
        *,
        project_id: UUID,
        sender_id: UUID,
        sender_name: str,
        content: str,
        member_ids: list[UUID],
    ) -> None:
        mentions = _MENTION_RE.findall(content)
        if not mentions:
            return

        users = self._users.find_by_ids(member_ids)
        lower_content = content.lower()
        for uid, user in users.items():
            if uid == sender_id:
                continue
            token = user.full_name.split()[0].lower() if user.full_name else ""
            email_token = user.email.split("@")[0].lower()
            matched = any(
                m.lower() in (token, email_token, user.full_name.lower())
                for m in mentions
            ) or "todos" in lower_content or "all" in lower_content
            if matched or "todos" in lower_content or "all" in lower_content:
                self.notify(
                    user_id=uid,
                    type="chat_mention",
                    title=f"{sender_name} mencionou-o no chat",
                    body=content[:200],
                    href=f"/projects/{project_id}",
                    project_id=project_id,
                    metadata={"sender_id": str(sender_id)},
                )

    def notify_report_ready(
        self,
        *,
        user_ids: list[UUID],
        project_id: UUID,
        project_name: str,
        report_type: str,
    ) -> None:
        for uid in user_ids:
            self.notify(
                user_id=uid,
                type="report_ready",
                title="Relatório gerado",
                body=f"{report_type.upper()} — {project_name}",
                href=f"/projects/{project_id}",
                project_id=project_id,
            )

    def notify_project_shared(
        self,
        *,
        target_user_id: UUID,
        project_id: UUID,
        project_name: str,
        sharer_name: str,
    ) -> None:
        self.notify(
            user_id=target_user_id,
            type="project_shared",
            title="Projecto partilhado consigo",
            body=f"{sharer_name} partilhou «{project_name}»",
            href=f"/projects/{project_id}",
            project_id=project_id,
        )

    def notify_payment_confirmed(
        self,
        *,
        user_id: UUID,
        plan_name: str,
        amount_label: str,
    ) -> None:
        self.notify(
            user_id=user_id,
            type="payment_confirmed",
            title="Pagamento confirmado",
            body=f"Plano {plan_name} — {amount_label}",
            href="/conta/assinatura",
        )

    def notify_subscription_expiring(
        self,
        *,
        user_id: UUID,
        plan_name: str,
        days_remaining: int,
    ) -> None:
        self.notify(
            user_id=user_id,
            type="subscription_expiring",
            title="Subscrição a expirar",
            body=f"«{plan_name}» expira em {days_remaining} dia(s)",
            href="/conta/assinatura",
            metadata={"days_remaining": days_remaining},
        )

    def notify_user_access_granted(
        self,
        *,
        user_id: UUID,
        plan_name: str | None,
        ends_at,
        approved: bool,
    ) -> None:
        if approved:
            title = "Conta aprovada"
            if plan_name and ends_at:
                body = f"Acesso activo — plano {plan_name} até {ends_at.strftime('%d/%m/%Y')}"
            elif plan_name:
                body = f"Acesso activo — plano {plan_name}"
            else:
                body = "A sua conta foi aprovada. Já pode iniciar sessão."
        else:
            title = "Acesso actualizado"
            body = (
                f"Plano {plan_name} renovado até {ends_at.strftime('%d/%m/%Y')}"
                if plan_name and ends_at
                else "O seu acesso à plataforma foi actualizado."
            )
        self.notify(
            user_id=user_id,
            type="access_granted",
            title=title,
            body=body,
            href="/login",
        )

    def notify_admins_new_registration(
        self,
        *,
        email: str,
        full_name: str,
        role: str,
        provider: str,
        pending_approval: bool,
    ) -> None:
        admins = self._users.find_all(role=UserRole.ADMIN, is_active=True, limit=100)
        status = "aguarda aprovação" if pending_approval else "activa"
        for admin in admins:
            self.notify(
                user_id=admin.id,
                type="new_registration",
                title="Novo registo na plataforma",
                body=f"{full_name} ({email}) — {role} via {provider} · {status}",
                href="/admin/utilizadores",
                metadata={
                    "email": email,
                    "role": role,
                    "provider": provider,
                    "pending_approval": pending_approval,
                },
            )
