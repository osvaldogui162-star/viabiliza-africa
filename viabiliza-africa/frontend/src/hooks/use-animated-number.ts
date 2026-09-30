"use client";

import { useEffect, useState } from "react";

function easeOutCubic(t: number) {
  return 1 - (1 - t) ** 3;
}

export function useAnimatedNumber(target: number, duration = 1100, active = true) {
  const [value, setValue] = useState(active ? 0 : target);

  useEffect(() => {
    if (!active) {
      setValue(target);
      return;
    }

    let frame = 0;
    let start: number | null = null;
    const from = 0;

    const tick = (ts: number) => {
      if (start == null) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      setValue(from + (target - from) * easeOutCubic(progress));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, duration, active]);

  return value;
}
