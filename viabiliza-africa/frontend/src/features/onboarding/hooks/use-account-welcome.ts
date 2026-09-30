"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import {
  completeAccountWelcome,
  shouldShowAccountWelcome,
} from "@/lib/auth/welcome-session";

export function useAccountWelcome() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const urlWelcome = searchParams.get("welcome") === "1";

  const [visible, setVisible] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    const show = shouldShowAccountWelcome(urlWelcome);
    if (show) {
      const timer = window.setTimeout(() => setVisible(true), 420);
      return () => window.clearTimeout(timer);
    }
    setVisible(false);
    return undefined;
  }, [ready, urlWelcome]);

  const dismiss = useCallback(() => {
    setVisible(false);
    completeAccountWelcome();
    if (urlWelcome) {
      router.replace(pathname, { scroll: false });
    }
  }, [pathname, router, urlWelcome]);

  return { visible, dismiss };
}
