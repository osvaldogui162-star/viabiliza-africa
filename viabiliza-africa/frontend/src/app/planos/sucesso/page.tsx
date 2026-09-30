import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";

import { PaymentSuccessPage } from "@/features/subscription/components/payment-success-page";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Pagamento confirmado | ViabilizA+ África",
};

export default function SuccessPage() {
  return (
    <div className={`${inter.variable} ${poppins.variable} pricing-font-scope min-h-screen`}>
      <PaymentSuccessPage />
    </div>
  );
}
