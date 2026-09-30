import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";

import { AccountSubscriptionPage } from "@/features/subscription/components/account-subscription-page";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Minha assinatura | ViabilizA+ África",
};

export default function SubscriptionAccountPage() {
  return (
    <div className={`${inter.variable} ${poppins.variable} pricing-font-scope min-h-screen`}>
      <AccountSubscriptionPage />
    </div>
  );
}
