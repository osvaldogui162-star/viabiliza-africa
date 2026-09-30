import { redirect } from "next/navigation";

/** Atalho em português → separador Promoções na consola admin */
export default function AdminPromocoesPage() {
  redirect("/admin?tab=promotions");
}
