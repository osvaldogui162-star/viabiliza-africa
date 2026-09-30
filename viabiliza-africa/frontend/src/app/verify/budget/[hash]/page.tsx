import { VerifyBudgetClient } from "./verify-budget-client";

export default async function VerifyBudgetPage({
  params,
}: {
  params: Promise<{ hash: string }>;
}) {
  const { hash } = await params;
  return <VerifyBudgetClient hash={hash} />;
}
