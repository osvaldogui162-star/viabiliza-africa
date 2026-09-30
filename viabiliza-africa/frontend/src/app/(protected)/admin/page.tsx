"use client";

import { Suspense } from "react";

import { AdminSettingsHub } from "@/features/admin/components/admin-settings-hub";
import { PageLoader } from "@/components/ui/spinner";

export default function AdminPage() {
  return (
    <Suspense fallback={<PageLoader message="A carregar consola admin…" />}>
      <AdminSettingsHub />
    </Suspense>
  );
}
