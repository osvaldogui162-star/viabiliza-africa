import { VerifyReportClient } from "./verify-report-client";

export default async function VerifyReportPage({
  params,
}: {
  params: Promise<{ hash: string }>;
}) {
  const { hash } = await params;
  return <VerifyReportClient hash={hash} />;
}
