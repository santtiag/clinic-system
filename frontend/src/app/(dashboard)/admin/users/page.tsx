'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { Users, UserCheck, UserX, UserPlus } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { USER_ROLES, SPECIALTIES } from '@/lib/constants';

const EMPTY_FORM = {
  username: '',
  email: '',
  password: '',
  dni: '',
  firstName: '',
  lastName: '',
  dateOfBirth: '',
  role: 'staff',
  specialty: '',
  licenseNumber: '',
};

export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const [roleFilter, setRoleFilter] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ ...EMPTY_FORM });

  const { data: users, isLoading } = useQuery<any[]>({
    queryKey: ['admin-users'],
    queryFn: () => apiFetch('/auth/users'),
  });

  const activateMutation = useMutation({
    mutationFn: (userId: string) =>
      apiFetch(`/auth/users/${userId}/activate`, { method: 'PATCH' }),
    onSuccess: () => {
      toast.success('Usuario activado');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (err: any) => toast.error(err.message),
  });

  const createMutation = useMutation({
    mutationFn: (payload: typeof EMPTY_FORM) => {
      const body: Record<string, unknown> = {
        username: payload.username,
        email: payload.email,
        password: payload.password,
        dni: payload.dni,
        firstName: payload.firstName,
        lastName: payload.lastName,
        dateOfBirth: payload.dateOfBirth,
        role: payload.role,
      };
      if (payload.role === 'doctor') {
        body.specialty = payload.specialty;
        body.licenseNumber = payload.licenseNumber;
      }
      return apiFetch('/auth/users', {
        method: 'POST',
        body: JSON.stringify(body),
      });
    },
    onSuccess: () => {
      toast.success('Usuario creado exitosamente');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setForm({ ...EMPTY_FORM });
      setShowForm(false);
    },
    onError: (err: any) => toast.error(err.message || 'Error al crear usuario'),
  });

  const handleCreate = () => {
    if (
      !form.username || !form.email || !form.password || !form.dni ||
      !form.firstName || !form.lastName || !form.dateOfBirth
    ) {
      toast.error('Complete todos los campos obligatorios');
      return;
    }
    if (form.role === 'doctor' && (!form.specialty || !form.licenseNumber)) {
      toast.error('Especialidad y matrícula son obligatorias para médicos');
      return;
    }
    createMutation.mutate(form);
  };

  const filtered = users?.filter((u) => roleFilter === 'all' || u.role === roleFilter) ?? [];

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-8 h-8 text-sky-500" />
            Gestión de Usuarios
          </h1>
          <p className="text-slate-500">Administrar roles, activación de médicos y accesos</p>
        </div>
        <Button
          className="bg-sky-600 hover:bg-sky-700 text-white gap-2 rounded-xl"
          onClick={() => setShowForm((v) => !v)}
        >
          <UserPlus className="w-4 h-4" />
          {showForm ? 'Cerrar formulario' : 'Nuevo Usuario Interno'}
        </Button>
      </div>

      {showForm && (
        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle>Crear Usuario Interno</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label>Nombre</Label>
                <Input value={form.firstName} onChange={(e) => setForm({ ...form, firstName: e.target.value })} />
              </div>
              <div className="space-y-1">
                <Label>Apellido</Label>
                <Input value={form.lastName} onChange={(e) => setForm({ ...form, lastName: e.target.value })} />
              </div>
              <div className="space-y-1">
                <Label>Usuario</Label>
                <Input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
              </div>
              <div className="space-y-1">
                <Label>Email</Label>
                <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </div>
              <div className="space-y-1">
                <Label>DNI</Label>
                <Input value={form.dni} onChange={(e) => setForm({ ...form, dni: e.target.value })} />
              </div>
              <div className="space-y-1">
                <Label>Fecha de Nacimiento</Label>
                <Input
                  type="date"
                  value={form.dateOfBirth}
                  onChange={(e) => setForm({ ...form, dateOfBirth: e.target.value })}
                />
              </div>
              <div className="space-y-1">
                <Label>Contraseña</Label>
                <Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
              </div>
              <div className="space-y-1">
                <Label>Rol</Label>
                <select
                  className="h-9 w-full px-3 rounded-lg border border-slate-200 text-sm"
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                >
                  <option value="staff">Personal Administrativo</option>
                  <option value="admin">Administrador</option>
                  <option value="doctor">Médico</option>
                </select>
              </div>
              {form.role === 'doctor' && (
                <>
                  <div className="space-y-1">
                    <Label>Especialidad</Label>
                    <select
                      className="h-9 w-full px-3 rounded-lg border border-slate-200 text-sm"
                      value={form.specialty}
                      onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                    >
                      <option value="">Seleccione...</option>
                      {SPECIALTIES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-1">
                    <Label>Matrícula / Licencia</Label>
                    <Input value={form.licenseNumber} onChange={(e) => setForm({ ...form, licenseNumber: e.target.value })} />
                  </div>
                </>
              )}
            </div>
            <div className="flex justify-end">
              <Button
                className="bg-sky-600 hover:bg-sky-700 text-white rounded-xl"
                onClick={handleCreate}
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? 'Creando...' : 'Crear Usuario'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Usuarios del Sistema</CardTitle>
          <select
            className="h-9 px-3 rounded-lg border border-slate-200 text-sm"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
          >
            <option value="all">Todos los roles</option>
            <option value="patient">Pacientes</option>
            <option value="doctor">Médicos</option>
            <option value="staff">Staff</option>
            <option value="admin">Administradores</option>
          </select>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-center py-12 text-slate-400">Cargando usuarios...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Rol</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{u.firstName} {u.lastName}</p>
                        <p className="text-xs text-slate-400">{u.email}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{USER_ROLES[u.role as keyof typeof USER_ROLES] ?? u.role}</Badge>
                    </TableCell>
                    <TableCell>
                      {u.isActive ? (
                        <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200">Activo</Badge>
                      ) : (
                        <Badge className="bg-amber-50 text-amber-700 border-amber-200">Pendiente</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {!u.isActive && u.role === 'doctor' && (
                        <Button
                          size="sm"
                          className="gap-1 bg-sky-600 hover:bg-sky-700"
                          onClick={() => activateMutation.mutate(u.id)}
                        >
                          <UserCheck className="w-4 h-4" />
                          Activar
                        </Button>
                      )}
                      {u.isActive && (
                        <UserX className="w-4 h-4 text-slate-300 inline" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
