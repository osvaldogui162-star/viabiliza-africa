"use client";

import { X } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";

const SIZE_CLASS = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
  full: "max-w-[min(96vw,72rem)]",
} as const;

export function Modal({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  className,
  size = "md",
  bodyClassName,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
  size?: keyof typeof SIZE_CLASS;
  bodyClassName?: string;
}) {
  const [mounted, setMounted] = useState(open);
  const [visible, setVisible] = useState(false);
  const [portalReady, setPortalReady] = useState(false);

  useEffect(() => {
    setPortalReady(true);
  }, []);

  useEffect(() => {
    if (open) {
      setMounted(true);
      const id = requestAnimationFrame(() => setVisible(true));
      return () => cancelAnimationFrame(id);
    }
    setVisible(false);
    return undefined;
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!mounted || !portalReady) return null;

  return createPortal(
    <div className="fixed inset-0 z-[120] flex items-center justify-center p-4 sm:p-6">
      <div
        className={cn(
          "absolute inset-0 bg-zinc-900/50 backdrop-blur-[2px] transition-opacity duration-300",
          visible ? "opacity-100" : "opacity-0",
        )}
        onClick={onClose}
        onTransitionEnd={() => {
          if (!visible) setMounted(false);
        }}
      />
      <div
        className={cn(
          "va-modal relative z-10 flex w-full max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl border border-zinc-200/80 bg-white shadow-2xl transition-all duration-300",
          SIZE_CLASS[size],
          visible ? "scale-100 opacity-100" : "scale-[0.98] opacity-0",
          className,
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="flex shrink-0 items-start justify-between gap-4 border-b border-zinc-100 bg-gradient-to-r from-zinc-50/90 via-white to-teal-50/40 px-5 py-4">
          <div className="min-w-0">
            <h3 id="modal-title" className="text-lg font-bold tracking-tight text-zinc-900">
              {title}
            </h3>
            {description ? (
              <p className="mt-1 text-sm leading-snug text-zinc-500">{description}</p>
            ) : null}
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Fechar" className="shrink-0">
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className={cn("min-h-0 flex-1 overflow-y-auto px-5 py-4", bodyClassName)}>{children}</div>
        {footer ? (
          <div className="shrink-0 border-t border-zinc-100 bg-zinc-50/60 px-5 py-3">{footer}</div>
        ) : null}
      </div>
    </div>,
    document.body,
  );
}
