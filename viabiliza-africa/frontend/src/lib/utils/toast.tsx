"use client";

import { toast } from "sonner";
import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";
import type { ReactNode } from "react";

function toastIcon(type: "success" | "error" | "info" | "warning"): ReactNode {
  const cls = "h-4 w-4 shrink-0";
  if (type === "success") return <CheckCircle2 className={cls} />;
  if (type === "error") return <XCircle className={cls} />;
  if (type === "warning") return <AlertTriangle className={cls} />;
  return <Info className={cls} />;
}

export function notifySuccess(message: string) {
  toast.success(message, { icon: toastIcon("success"), className: "va-toast" });
}

export function notifyError(message: string) {
  toast.error(message, { icon: toastIcon("error"), className: "va-toast va-toast-error" });
}

export function notifyInfo(message: string) {
  toast.info(message, { icon: toastIcon("info"), className: "va-toast" });
}

export function notifyWarning(message: string) {
  toast.warning(message, { icon: toastIcon("warning"), className: "va-toast" });
}
