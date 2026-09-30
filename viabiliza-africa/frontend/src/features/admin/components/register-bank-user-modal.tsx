"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { BankInstitutionSelect } from "@/features/financier/components/bank-institution-select";
import { ANGOLAN_BANK_CODES } from "@/lib/data/angolan-banks";
import { useI18n } from "@/components/providers/locale-provider";
import { ApiError } from "@/lib/api/http-client";
import { authApi } from "@/lib/api/auth-api";

const schema = z.object({
  email: z.email("Email inválido"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
  full_name: z.string().min(2, "Mínimo 2 caracteres"),
  bank_code: z.enum(ANGOLAN_BANK_CODES),
});

type FormValues = z.infer<typeof schema>;

export function RegisterBankUserModal({
  open,
  onClose,
  onSuccess,
}: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const { t } = useI18n();
  const [submitting, setSubmitting] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "", full_name: "", bank_code: "bfa" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      await authApi.register({
        email: values.email,
        password: values.password,
        full_name: values.full_name,
        role: "bank",
        bank_code: values.bank_code,
      });
      toast.success(t("adminBank.createSuccess"));
      form.reset({ email: "", password: "", full_name: "", bank_code: values.bank_code });
      onSuccess();
      onClose();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  });

  return (
    <Modal open={open} onClose={onClose} title={t("adminBank.createAccess")} description={t("adminBank.createDesc")}>
      <form onSubmit={onSubmit} className="space-y-4">
        <BankInstitutionSelect
          label={t("adminBank.institution")}
          value={form.watch("bank_code")}
          onChange={(code) => form.setValue("bank_code", code as FormValues["bank_code"], { shouldValidate: true })}
        />
        <Input
          label={t("adminBank.contactName")}
          {...form.register("full_name")}
          error={form.formState.errors.full_name?.message}
        />
        <Input
          label={t("common.email")}
          type="email"
          {...form.register("email")}
          error={form.formState.errors.email?.message}
        />
        <Input
          label={t("common.password")}
          type="password"
          {...form.register("password")}
          error={form.formState.errors.password?.message}
        />
        <Button type="submit" loading={submitting} className="w-full">
          {t("adminBank.createAccess")}
        </Button>
      </form>
    </Modal>
  );
}
