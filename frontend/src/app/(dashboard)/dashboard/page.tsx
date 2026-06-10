'use client';

import React from 'react';
import { useAuth } from '@/providers/auth-provider';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { AdminSummary, Role } from '@/types';
import { ROLE_QUICK_ACTIONS } from '@/lib/constants';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Users,
  CalendarCheck,
  TrendingUp,
  CreditCard,
  FileText,
  Stethoscope,
  Clock,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

function StatCard({ title, value, icon: Icon, color }: {
  title: string;
  value: string | number | undefined;
  icon: React.ElementType;
  color: string;
}) {
  return (
    <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden">
      <CardContent className="p-6 flex items-center justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <h3 className="text-2xl font-bold text-slate-900">{value ?? '...'}</h3>
        </div>
        <div className={`p-3 rounded-xl ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();

  const { data: adminData, isLoading: isLoadingAdmin } = useQuery<AdminSummary>({
    queryKey: ['admin-dashboard'],
    queryFn: () => apiFetch('/admin/dashboard'),
    enabled: user?.role === Role.ADMIN,
  });

  const { data: myAppointments } = useQuery<any[]>({
    queryKey: ['dashboard-appointments'],
    queryFn: () => apiFetch('/appointments/me'),
    enabled: user?.role === Role.PATIENT,
  });

  const { data: allAppointments } = useQuery<any[]>({
    queryKey: ['dashboard-all-appointments'],
    queryFn: () => apiFetch('/appointments/all'),
    enabled: user?.role === Role.DOCTOR || user?.role === Role.STAFF,
  });

  const { data: myInvoices } = useQuery<any[]>({
    queryKey: ['dashboard-invoices'],
    queryFn: () => apiFetch('/invoices/me'),
    enabled: user?.role === Role.PATIENT,
  });

  const { data: pendingInvoices } = useQuery<any[]>({
    queryKey: ['dashboard-pending'],
    queryFn: () => apiFetch('/invoices/pending'),
    enabled: user?.role === Role.STAFF || user?.role === Role.ADMIN,
  });

  if (!user) return null;

  const nextAppointment = myAppointments?.find((a) => a.status === 'programada' || a.status === 'confirmada');
  const doctorToday = allAppointments?.filter((a) => {
    const d = a.start_time || a.startTime || a.created_at || a.createdAt;
    return d?.startsWith(new Date().toISOString().slice(0, 10));
  }) ?? [];
  const waitingCount = allAppointments?.filter((a) => a.status === 'en_atencion').length ?? 0;
  const completedCount = allAppointments?.filter((a) => a.status === 'completada').length ?? 0;
  const pendingCount = myInvoices?.filter((i) => i.status === 'pendiente').length ?? 0;
  const quickActions = ROLE_QUICK_ACTIONS[user.role as Role] ?? [];

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Panel de Control</h1>
          <p className="text-slate-500">Bienvenido. Aquí tienes el resumen según tu rol.</p>
        </div>
        <Badge variant="outline" className="w-fit px-3 py-1 bg-white border-slate-200 text-slate-600 font-medium capitalize">
          {new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })}
        </Badge>
      </div>

      {user.role === Role.ADMIN && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard title="Total Usuarios" value={isLoadingAdmin ? undefined : adminData?.users?.total} icon={Users} color="bg-sky-500" />
          <StatCard title="Citas Totales" value={isLoadingAdmin ? undefined : adminData?.appointments?.total} icon={CalendarCheck} color="bg-indigo-500" />
          <StatCard title="Médicos Pendientes" value={isLoadingAdmin ? undefined : adminData?.users?.pending_doctors} icon={Stethoscope} color="bg-amber-500" />
          <StatCard title="Ingresos Totales" value={isLoadingAdmin ? undefined : `$${adminData?.billing?.total_income?.toLocaleString() ?? 0}`} icon={TrendingUp} color="bg-emerald-500" />
        </div>
      )}

      {user.role === Role.DOCTOR && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard title="Citas Hoy" value={doctorToday.length} icon={CalendarCheck} color="bg-sky-500" />
          <StatCard title="En Atención" value={waitingCount} icon={Clock} color="bg-amber-500" />
          <StatCard title="Completadas" value={completedCount} icon={TrendingUp} color="bg-emerald-500" />
        </div>
      )}

      {user.role === Role.PATIENT && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Próxima Cita"
            value={nextAppointment ? (nextAppointment.start_time ? new Date(nextAppointment.start_time).toLocaleString('es-ES') : 'Programada') : 'Sin citas'}
            icon={CalendarCheck}
            color="bg-sky-500"
          />
          <StatCard title="Mis Consultas" value={myAppointments?.length ?? 0} icon={FileText} color="bg-indigo-500" />
          <StatCard title="Facturas Pendientes" value={pendingCount} icon={CreditCard} color="bg-emerald-500" />
        </div>
      )}

      {user.role === Role.STAFF && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard title="Citas Activas" value={allAppointments?.length ?? 0} icon={CalendarCheck} color="bg-sky-500" />
          <StatCard title="Por Confirmar" value={allAppointments?.filter((a) => a.status === 'programada').length ?? 0} icon={Clock} color="bg-amber-500" />
          <StatCard title="Pendientes Cobro" value={pendingInvoices?.length ?? 0} icon={CreditCard} color="bg-emerald-500" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2 border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Acciones según tu rol</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {quickActions.map((action) => (
              <Link key={action.href} href={action.href} className="block">
                <Button variant="outline" className="w-full justify-start gap-3 h-12 px-4 rounded-xl">
                  {action.label}
                </Button>
              </Link>
            ))}
          </CardContent>
        </Card>

        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Tu Rol</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge className="capitalize text-sm px-3 py-1">{user.role}</Badge>
            <p className="text-sm text-slate-500 mt-4">
              El menú lateral muestra solo las secciones disponibles para tu perfil.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
