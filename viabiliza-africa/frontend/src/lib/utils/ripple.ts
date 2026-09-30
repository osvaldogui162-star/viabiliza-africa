import type { MouseEvent } from "react";

export function spawnRipple(event: MouseEvent<HTMLElement>, className = "va-ripple") {
  const node = event.currentTarget;
  const rect = node.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height) * 1.6;
  const ripple = document.createElement("span");
  ripple.className = className;
  ripple.style.width = `${size}px`;
  ripple.style.height = `${size}px`;
  ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
  ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
  node.appendChild(ripple);
  ripple.addEventListener("animationend", () => ripple.remove(), { once: true });
}
