"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";

import { cn } from "@/lib/utils/cn";

type AnchoredPanelProps = {
  open: boolean;
  onClose: () => void;
  anchorRef: React.RefObject<HTMLElement | null>;
  children: ReactNode;
  className?: string;
  backdropClassName?: string;
  align?: "right" | "left";
};

export function AnchoredPanel({
  open,
  onClose,
  anchorRef,
  children,
  className,
  backdropClassName,
  align = "right",
}: AnchoredPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);
  const [style, setStyle] = useState<{ top: number; left?: number; right?: number }>({ top: 0, right: 0 });

  useEffect(() => {
    setMounted(true);
  }, []);

  const updatePosition = useCallback(() => {
    const anchor = anchorRef.current;
    const panel = panelRef.current;
    if (!anchor || !panel) return;

    const rect = anchor.getBoundingClientRect();
    const panelHeight = panel.offsetHeight || 280;
    const panelWidth = panel.offsetWidth || 288;
    const gap = 8;
    const viewportPad = 12;

    let top = rect.bottom + gap;
    if (top + panelHeight > window.innerHeight - viewportPad) {
      top = Math.max(viewportPad, rect.top - panelHeight - gap);
    }

    if (align === "right") {
      let right = window.innerWidth - rect.right;
      right = Math.max(viewportPad, Math.min(right, window.innerWidth - panelWidth - viewportPad));
      setStyle({ top, right });
      return;
    }

    let left = rect.left;
    left = Math.max(viewportPad, Math.min(left, window.innerWidth - panelWidth - viewportPad));
    setStyle({ top, left });
  }, [align, anchorRef]);

  useLayoutEffect(() => {
    if (!open) return;
    updatePosition();
  }, [open, updatePosition]);

  useEffect(() => {
    if (!open) return;
    const id = requestAnimationFrame(() => updatePosition());
    const onLayout = () => updatePosition();
    window.addEventListener("resize", onLayout);
    window.addEventListener("scroll", onLayout, true);
    return () => {
      cancelAnimationFrame(id);
      window.removeEventListener("resize", onLayout);
      window.removeEventListener("scroll", onLayout, true);
    };
  }, [open, updatePosition]);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !mounted) return null;

  return createPortal(
    <>
      <button
        type="button"
        aria-label="Fechar"
        className={cn("fixed inset-0 z-[90] cursor-default bg-slate-900/25 backdrop-blur-[1px]", backdropClassName)}
        onClick={onClose}
      />
      <div
        ref={panelRef}
        className={cn("va-dropdown-in fixed z-[91]", className)}
        style={{ top: style.top, right: style.right, left: style.left }}
      >
        {children}
      </div>
    </>,
    document.body,
  );
}
