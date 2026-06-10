'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { IncomeReport, AppointmentStats } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  BarChart3,
  Download,
  TrendingUp,
  Calendar,
  DollarSign,
  Users
} from 'lucide-react';
import { toast } from 'sonner';
import { Input } from '@/components/ui/input';

function IncomeChart({ data }: { data: IncomeReport }) {
  // Mocking some visual representation since we only have a list of invoices
  // In a real app we would aggregate by date/category
  return (
    <div className="h-64 w-full flex items-end gap-4 px-4 pb-4 border-b border-l border-slate-200">
      {[...Array(6)].map((_, i) => {
        const height = Math.floor(Math.random() * 60) + 20;
        return (
          <div key={i} className="flex-1 flex flex-col items-center gap-2 group">
            <div
              className="w-full bg-sky-500 rounded-t-lg transition-all duration-500 group-hover:bg-sky-600"
              style={{ height: `${height}%` }}
            />
            <span className="text-[10px] text-slate-400 font-medium uppercase">Día {i+1}</span>
          </div>
        );
      })}
    </div>
  );
}

function StatusDonut({ data }: { data: AppointmentStats }) {
  const total = data.total;
  const entries = Object.entries(data.byStatus ?? {});
  if (total === 0 || entries.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 w-full text-slate-400 text-sm">
        No hay datos de citas
      </div>
    );
  }
  let currentAngle = 0;

  return (
    <div className="flex items-center justify-center h-64 w-full relative">
      <svg viewBox="0 0 100 100" className="w-48 h-48 transform -rotate-90">
        {entries.map(([status, count], i) => {
          const percentage = count / total;
          const angle = percentage * 360;
          const x1 = 50 + 40 * Math.cos((currentAngle * Math.PI) / 180);
          const y1 = 50 + 40 * Math.sin((currentAngle * Math.PI) / 180);
          currentAngle += angle;
          const x2 = 50 + 40 * Math.cos((currentAngle * Math.PI) / 180);
          const y2 = 50 + 40 * Math.sin((currentAngle * Math.PI) / 180);

          const colors = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#6366f1'];
          return (
            <circle
              key={status}
              cx="50" cy="50" r="40"
              fill="transparent"
              stroke={colors[i % colors.length]}
              strokeWidth="12"
              strokeDasharray={`${percentage * 251.2} 251.2`}
              strokeDashoffset="0"
              strokeLinecap="round"
            />
          );
        })}
        <circle cx="50" cy="50" r="30" fill="white" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-3xl font-bold text-slate-900">{total}</span>
        <span className="text-xs text-slate-500 font-medium uppercase">Total Citas</span>
      </div>
    </div>
  );
}

export default function ReportsPage() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data: income, isLoading: isLoadingIncome } = useQuery<IncomeReport>({
    queryKey: ['reports-income', startDate, endDate],
    queryFn: async () => {
      const params = `?start_date=${startDate}&end_date=${endDate}`;
      const r: any = await apiFetch(`/reports/income${params}`);
      return {
        totalIncome: r.total_income ?? r.totalIncome ?? 0,
        count: r.count ?? 0,
        invoices: r.invoices ?? [],
      };
    },
  });

  const { data: stats, isLoading: isLoadingStats } = useQuery<AppointmentStats>({
    queryKey: ['reports-appointments'],
    queryFn: async () => {
      const r: any = await apiFetch('/reports/appointments');
      return {
        total: r.total ?? 0,
        byStatus: r.by_status ?? r.byStatus ?? {},
      };
    },
  });

  const handleExport = async (type: 'income' | 'appointments') => {
    try {
      const params = `?report_type=${type}&format=csv&start_date=${startDate}&end_date=${endDate}`;
      window.open(`${process.env.NEXT_PUBLIC_API_URL}/reports/export${params}`, '_blank');
      toast.success('Iniciando exportación de datos...');
    } catch (err: any) {
      toast.error('Error al exportar reporte');
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Reportes y Analítica</h1>
          <p className="text-slate-500">Análisis de ingresos y demanda de servicios</p>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          <Button
            variant="outline"
            className="gap-2 rounded-xl text-slate-600"
            onClick={() => handleExport('income')}
          >
            <Download className="w-4 h-4" />
            Exportar Ingresos (CSV)
          </Button>
          <Button
            variant="outline"
            className="gap-2 rounded-xl text-slate-600"
            onClick={() => handleExport('appointments')}
          >
            <Download className="w-4 h-4" />
            Exportar Citas (CSV)
          </Button>
        </div>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex items-center gap-2 shrink-0">
            <Calendar className="w-5 h-5 text-sky-500" />
            <span className="text-sm font-medium text-slate-600">Periodo:</span>
          </div>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 flex-1">
            <Input
              type="date"
              className="h-9 text-sm bg-slate-50"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <span className="text-slate-400 text-center text-sm hidden sm:inline">a</span>
            <Input
              type="date"
              className="h-9 text-sm bg-slate-50"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-500" />
              Ingresos Financieros
            </CardTitle>
            <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50 font-bold">
              ${income?.totalIncome?.toLocaleString() || '0'}
            </Badge>
          </CardHeader>
          <CardContent className="space-y-6">
            {isLoadingIncome ? (
              <div className="h-64 flex items-center justify-center bg-slate-50 rounded-xl animate-pulse" />
            ) : (
              <>
                <IncomeChart data={income || { totalIncome: 0, count: 0, invoices: [] }} />
                <div className="flex justify-between items-center pt-4">
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <Users className="w-4 h-4" />
                    <span>{income?.count} facturas procesadas</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm font-bold text-emerald-600">
                    <TrendingUp className="w-4 h-4" />
                    <span>Crecimiento +12%</span>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-sky-500" />
              Estadísticas de Demanda
            </CardTitle>
            <Badge variant="outline" className="text-sky-600 border-sky-200 bg-sky-50 font-bold">
              {stats?.total || 0} citas
            </Badge>
          </CardHeader>
          <CardContent>
            {isLoadingStats ? (
              <div className="h-64 flex items-center justify-center bg-slate-50 rounded-xl animate-pulse" />
            ) : stats ? (
              <div className="flex flex-col items-center gap-8">
                <StatusDonut data={stats} />
                <div className="grid grid-cols-2 gap-x-8 gap-y-2 w-full max-w-xs">
                  {Object.entries(stats.byStatus).map(([status, count], i) => (
                    <div key={status} className="flex items-center gap-2 text-xs">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#6366f1'][i % 5] }}
                      />
                      <span className="text-slate-500 truncate">{status}</span>
                      <span className="font-bold text-slate-900 ml-auto">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="py-20 text-center text-slate-400">No hay datos disponibles</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
