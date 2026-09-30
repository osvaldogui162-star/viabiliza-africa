"use client";

import { useEffect, useRef } from "react";

const BASE_TITLE = "ViabilizA+";

/** Mostra contagem no título do separador do browser, ex.: (3) ViabilizA+ */
export function useDocumentUnreadTitle(unreadCount: number) {
  const baseRef = useRef(BASE_TITLE);

  useEffect(() => {
    if (typeof document === "undefined") return;
    if (!baseRef.current || baseRef.current === BASE_TITLE) {
      const current = document.title.replace(/^\(\d+\)\s*/, "");
      if (current) baseRef.current = current.replace(/^\(\d+\)\s*/, "") || BASE_TITLE;
    }

    document.title =
      unreadCount > 0
        ? `(${unreadCount > 9 ? "9+" : unreadCount}) ${baseRef.current}`
        : baseRef.current;

    return () => {
      document.title = baseRef.current;
    };
  }, [unreadCount]);
}
