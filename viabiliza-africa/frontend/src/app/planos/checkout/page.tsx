import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";

import { CheckoutPageClient } from "@/features/subscription/components/checkout-page";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Checkout | ViabilizA+ África",
  description: "Finalizar pagamento da assinatura",
};

export default function CheckoutPage() {
  return (
    <div className={`${inter.variable} ${poppins.variable} pricing-font-scope min-h-screen`}>
      <CheckoutPageClient />
    </div>
  );
}
