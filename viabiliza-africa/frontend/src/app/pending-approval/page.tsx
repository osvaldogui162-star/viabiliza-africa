"use client";

import { Suspense } from "react";

import { AuthShell } from "@/features/auth/components/auth-shell";
import { useI18n } from "@/components/providers/locale-provider";
import PendingApprovalContent from "./pending-approval-content";

function Fallback() {
  return <div className="h-40 animate-pulse rounded-xl bg-zinc-100" />;
}

export default function Page() {
  const { locale } = useI18n();
  return (
    <AuthShell title={locale === "en" ? "Pending approval" : "Aprovação pendente"}>
      <Suspense fallback={<Fallback />}>
        <PendingApprovalContent />
      </Suspense>
    </AuthShell>
  );
}
