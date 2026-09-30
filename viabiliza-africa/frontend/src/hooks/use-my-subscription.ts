"use client";

import { useCallback, useEffect, useState } from "react";
import { subscriptionApi } from "@/lib/api/subscription-api";
import type { MySubscriptionResponse } from "@/lib/types/subscription";

export function useMySubscription(enabled = true) {
  const [data, setData] = useState<MySubscriptionResponse | null>(null);
  const [loading, setLoading] = useState(enabled);

  const reload = useCallback(async () => {
    if (!enabled) return;
    setLoading(true);
    try {
      setData(await subscriptionApi.getMySubscription());
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [enabled]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, loading, reload, capabilities: data?.capabilities ?? null };
}
