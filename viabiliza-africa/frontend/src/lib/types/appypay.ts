import type { CheckoutResponse } from "@/lib/types/subscription";

export type AppyPayMethod = "gpo" | "ref";

export interface AppyPayPaymentResponse {
  payment: AppyPayPayment;
  checkout: CheckoutResponse;
  instructions: AppyPayInstructions;
  free_plan?: boolean;
}

export interface AppyPayPollResponse {
  payment: AppyPayPayment;
  instructions: AppyPayInstructions;
}

export interface AppyPayPayment {
  id: string;
  status: "pending" | "processing" | "paid" | "failed" | "cancelled" | "expired";
  payment_method: AppyPayMethod;
  amount: string;
  currency: string;
  merchant_transaction_id: string;
  phone_number?: string | null;
  reference_entity?: string | null;
  reference_number?: string | null;
  error_message?: string | null;
}

export interface AppyPayInstructions {
  type: AppyPayMethod;
  title: string;
  message: string;
  phone_number?: string | null;
  entity?: string | null;
  reference_number?: string | null;
}
