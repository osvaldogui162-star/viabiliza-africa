import { OfficeView } from "@/features/office/components/office-view";

export default async function EscritorioPage({
  searchParams,
}: {
  searchParams: Promise<{ owner_id?: string }>;
}) {
  const { owner_id: ownerId } = await searchParams;
  return <OfficeView ownerId={ownerId} />;
}
