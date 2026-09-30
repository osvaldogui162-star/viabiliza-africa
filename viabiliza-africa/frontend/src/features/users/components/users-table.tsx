"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { UserPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PageLoader } from "@/components/ui/spinner";
import { RegisterUserModal } from "@/features/users/components/register-user-modal";
import { usersApi } from "@/lib/api/users-api";
import type { User, UserRole } from "@/lib/types/auth";
import { ApiError } from "@/lib/api/http-client";

export function UsersTable() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [registerOpen, setRegisterOpen] = useState(false);

  async function loadUsers() {
    setLoading(true);
    try {
      const response = await usersApi.list();
      setUsers(response.items);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Erro ao carregar utilizadores";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadUsers();
  }, []);

  async function toggleUser(user: User) {
    try {
      await usersApi.update(user.id, { is_active: !user.is_active });
      toast.success("Estado actualizado");
      void loadUsers();
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Erro ao actualizar utilizador";
      toast.error(message);
    }
  }

  async function changeRole(user: User, role: UserRole) {
    try {
      await usersApi.updateRole(user.id, role);
      toast.success("Perfil actualizado");
      void loadUsers();
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Erro ao alterar perfil";
      toast.error(message);
    }
  }

  if (loading) return <PageLoader layout="section" message="A carregar utilizadores..." />;

  return (
    <>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => setRegisterOpen(true)}>
          <UserPlus className="h-4 w-4" /> Registar utilizador
        </Button>
      </div>

      <div className="overflow-x-auto rounded-xl border bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-zinc-50 text-left">
            <tr>
              <th className="p-3">Nome</th>
              <th className="p-3">Email</th>
              <th className="p-3">Perfil</th>
              <th className="p-3">Estado</th>
              <th className="p-3">Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-t">
                <td className="p-3">{user.full_name}</td>
                <td className="p-3">{user.email}</td>
                <td className="p-3">
                  <select
                    className="rounded border px-2 py-1"
                    value={user.role}
                    onChange={(event) => void changeRole(user, event.target.value as UserRole)}
                  >
                    <option value="admin">admin</option>
                    <option value="financial">financial</option>
                    <option value="user">user</option>
                  </select>
                </td>
                <td className="p-3">{user.is_active ? "Activo" : "Inactivo"}</td>
                <td className="p-3">
                  <button
                    onClick={() => void toggleUser(user)}
                    className="rounded-lg border px-3 py-1 hover:bg-zinc-50"
                  >
                    {user.is_active ? "Desactivar" : "Activar"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <RegisterUserModal
        open={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onSuccess={() => void loadUsers()}
      />
    </>
  );
}
