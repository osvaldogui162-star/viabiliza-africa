"use client";

import { BrandPageLoader, type BrandLoaderLayout, type BrandLoaderTheme } from "@/components/brand/brand-page-loader";

export function BrandLoadingRoot({
  layout = "fullscreen",
  theme = "light",
  message,
}: {
  layout?: BrandLoaderLayout;
  theme?: BrandLoaderTheme;
  message?: string;
}) {
  return <BrandPageLoader layout={layout} theme={theme} message={message} priority />;
}
