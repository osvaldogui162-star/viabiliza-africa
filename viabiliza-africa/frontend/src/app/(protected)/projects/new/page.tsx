import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { ProjectWizard } from "@/features/projects/components/project-wizard";

export default function NewProjectPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center gap-3">
        <Link
          href="/projects"
          className="rounded-lg p-1.5 text-zinc-500 transition hover:bg-zinc-100 hover:text-zinc-700"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">Novo projecto</h1>
          <p className="text-sm text-zinc-500">
            Registo profissional em 4 passos — representante, empresa, projecto e banco
          </p>
        </div>
      </div>

      <ProjectWizard />
    </div>
  );
}
