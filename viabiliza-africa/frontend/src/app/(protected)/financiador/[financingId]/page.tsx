import { FinancierMonitoringView } from "@/features/financier/components/financier-monitoring-view";

export default async function FinancierMonitoringPage({
  params,
}: {
  params: Promise<{ financingId: string }>;
}) {
  const { financingId } = await params;
  return <FinancierMonitoringView financingId={financingId} />;
}
