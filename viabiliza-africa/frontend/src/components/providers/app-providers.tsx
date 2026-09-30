"use client";

import { Toaster } from "sonner";

import { AuthProvider } from "@/components/providers/auth-provider";
import { LocaleProvider } from "@/components/providers/locale-provider";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <LocaleProvider>
      <AuthProvider>
        {children}
        <Toaster
          richColors
          position="top-right"
          closeButton
          toastOptions={{
            classNames: {
              toast: "va-toast",
              title: "font-semibold",
              description: "text-sm opacity-90",
            },
          }}
        />
      </AuthProvider>
    </LocaleProvider>
  );
}
