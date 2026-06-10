'use client';

import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { AdminSummary } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Users,
  CalendarCheck,
  DollarSign,
  TrendingUp,
  ShieldAlert,
  Activity,
  LayoutGrid,
  ShieldCheck,
} from 'lucide-react';

const KPI_COLORS: Record<string, { bg: string; text: string }> = {
  'bg-sky-500': { bg: 'bg-sky-50', text: 'text-sky-600' },
  'bg-indigo-500': { bg: 'bg-indigo-50', text: 'text-indigo-600' },
  'bg-emerald-500': { bg: 'bg-emerald-50', text: 'text-emerald-600' },
  'bg-amber-500': { bg: 'bg-amber-50', text: 'text-amber-600' },
};

function AdminKpiCard({ title, value, icon: Icon, color, description }: any) {
  const palette = KPI_COLORS[color] ?? KPI_COLORS['bg-sky-500'];

  return (
    <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden group hover:ring-sky-500 transition-all duration-300">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-2.5 rounded-xl ${palette.bg}`}>
            <Icon className={`w-6 h-6 ${palette.text}`} />
          </div>
          <div className="p-2 rounded-full bg-slate-50 border border-slate-100">
            <Activity className="w-4 h-4 text-slate-400" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <h3 className="text-3xl font-bold text-slate-900">{value}</h3>
          <p className="text-xs text-slate-400 pt-2 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            {description}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function AdminPage() {
  const { data: summary, isLoading } = useQuery<AdminSummary>({
    queryKey: ['admin-dashboard'],
    queryFn: () => apiFetch('/admin/dashboard'),
  });

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-sky-500 rounded-lg shadow-sm">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Panel de Administración</h1>
            <p className="text-slate-500">Visión global de la operación clínica</p>
          </div>
        </div>
        <Badge variant="outline" className="px-3 py-1 bg-sky-50 border-sky-200 text-sky-600 font-medium">
          Admin Mode
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AdminKpiCard
          title="Total de Usuarios"
          value={isLoading ? '...' : summary?.users.total}
          icon={Users}
          color="bg-sky-500"
          description="Crecimiento mensual +4%"
        />
        <AdminKpiCard
          title="Citas Totales"
          value={isLoading ? '...' : summary?.appointments.total}
          icon={CalendarCheck}
          color="bg-indigo-500"
          description="Tasa de ocupación 88%"
        />
        <AdminKpiCard
          title="Ingresos Totales"
          value={isLoading ? '...' : `$${summary?.billing.totalIncome?.toLocaleString()}`}
          icon={DollarSign}
          color="bg-emerald-500"
          description="Margen neto +12%"
        />
        <AdminKpiCard
          title="Facturas Pendientes"
          value={isLoading ? '...' : summary?.billing.pendingInvoices}
          icon={ShieldAlert}
          color="bg-amber-500"
          description="Promedio cobro 3 días"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold">Distribución de Roles</CardTitle>
            <LayoutGrid className="w-5 h-5 text-slate-400" />
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-sm font-medium text-slate-600">Pacientes</span>
                <span className="text-sm font-bold text-slate-900">{summary?.users.patients || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-sm font-medium text-slate-600">Médicos</span>
                <span className="text-sm font-bold text-slate-900">{summary?.users.doctors || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-sm font-medium text-slate-600">Staff Administrativo</span>
                <span className="text-sm font-bold text-slate-900">
                  {(summary?.users.total ?? 0) - (summary?.users.patients || 0) - (summary?.users.doctors || 0)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Estado del Sistema</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50 border border-emerald-100">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-emerald-700">Kong API Gateway</span>
              </div>
              <span className="text-xs font-bold text-emerald-600 uppercase">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50 border border-emerald-100">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-emerald-700">Identity Service</span>
              </div>
              <span className="text-xs font-bold text-emerald-600 uppercase">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50 border border-emerald-100">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-emerald-700">PostgreSQL Database</span>
              </div>
              <span className="text-xs font-bold text-emerald-600 uppercase">Online</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
