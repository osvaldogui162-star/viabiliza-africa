import type { Project } from "@/lib/types/project";

export function exportProjectsCsv(projects: Project[], filename = "projectos.csv") {
  const headers = [
    "id",
    "nome",
    "empresa",
    "sector",
    "pais",
    "moeda",
    "investimento",
    "estado",
    "partilhado",
    "colaboradores",
    "actualizado",
  ];

  const rows = projects.map((p) =>
    [
      p.id,
      p.name,
      p.company_name,
      p.sector_label,
      p.country_label,
      p.currency,
      p.investment_amount,
      p.status_label,
      p.is_shared ? "sim" : "nao",
      String(p.shares_count),
      p.updated_at,
    ]
      .map((v) => `"${String(v).replace(/"/g, '""')}"`)
      .join(","),
  );

  const blob = new Blob([[headers.join(","), ...rows].join("\n")], {
    type: "text/csv;charset=utf-8;",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
