"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Modal } from "@/components/ui/modal";
import { ApiError } from "@/lib/api/http-client";
import { authApi } from "@/lib/api/auth-api";
import type { UserRole } from "@/lib/types/auth";

const schema = z.object({
  email: z.email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
  full_name: z.string().min(2, "Mínimo 2 caracteres"),
  role: z.enum(["financial", "user"]),
});

type FormValues = z.infer<typeof schema>;

export function RegisterUserModal({
  open,
  onClose,
  onSuccess,
}: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [submitting, setSubmitting] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "", full_name: "", role: "financial" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      await authApi.register({
        email: values.email,
        password: values.password,
        full_name: values.full_name,
        role: values.role as Exclude<UserRole, "admin">,
      });
      toast.success("Utilizador registado");
      form.reset();
      onSuccess();
      onClose();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Erro ao registar");
    } finally {
      setSubmitting(false);
    }
  });

  return (
    <Modal open={open} onClose={onClose} title="Registar utilizador">
      <form onSubmit={onSubmit} className="space-y-4">
        <Input label="Nome completo" {...form.register("full_name")} error={form.formState.errors.full_name?.message} />
        <Input label="Email" type="email" {...form.register("email")} error={form.formState.errors.email?.message} />
        <Input
          label="Palavra-passe"
          type="password"
          {...form.register("password")}
          error={form.formState.errors.password?.message}
        />
        <Select label="Perfil" {...form.register("role")}>
          <option value="financial">Analista financeiro</option>
          <option value="user">Utilizador comum</option>
        </Select>
        <Button type="submit" loading={submitting} className="w-full">
          Registar
        </Button>
      </form>
    </Modal>
  );
}
