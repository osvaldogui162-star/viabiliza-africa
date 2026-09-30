import { apiRequest, buildQuery } from "@/lib/api/http-client";
import type {
  AppyPayMethod,
  AppyPayPaymentResponse,
  AppyPayPollResponse,
} from "@/lib/types/appypay";
import type {
  BillingCycle,
  CurrencyDisplay,
  MySubscriptionResponse,
  PlansResponse,
} from "@/lib/types/subscription";

export const subscriptionApi = {
  listPlans() {
    return apiRequest<PlansResponse>("/plans", "GET", undefined, false);
  },

  getMySubscription() {
    return apiRequest<MySubscriptionResponse>("/me/subscription", "GET");
  },

  prepareCheckout(planCode: string, billingCycle: BillingCycle, currency: CurrencyDisplay) {
    return apiRequest(
      `/plans/checkout-preview${buildQuery({ plan_code: planCode, billing_cycle: billingCycle, currency })}`,
      "GET",
      undefined,
      false,
    );
  },

  initiateAppyPayPayment(payload: {
    plan_code: string;
    billing_cycle: BillingCycle;
    payment_method: AppyPayMethod;
    phone_number?: string;
  }) {
    return apiRequest<AppyPayPaymentResponse>("/me/subscription/payments/appypay", "POST", payload);
  },

  pollAppyPayPayment(paymentId: string) {
    return apiRequest<AppyPayPollResponse>(`/me/subscription/payments/${paymentId}`, "GET");
  },

  mockAppyPayReference(paymentId: string) {
    return apiRequest<AppyPayPollResponse>(
      `/me/subscription/payments/${paymentId}/mock-reference`,
      "POST",
      {},
    );
  },
};
