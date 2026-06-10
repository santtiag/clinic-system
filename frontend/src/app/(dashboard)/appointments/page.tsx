'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/providers/auth-provider';
import { apiFetch } from '@/lib/api';
import { Appointment, AppointmentStatus } from '@/types';
import { mapAppointments } from '@/lib/scheduling';
import { APPOINTMENT_STATUSES } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  CalendarDays,
  Filter,
  Plus,
  MoreVertical,
  XCircle,
  RefreshCw,
  CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

export default function AppointmentsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const { data: appointments, isLoading, refetch } = useQuery<Appointment[]>({
    queryKey: ['appointments', user?.role],
    queryFn: async () => {
      const endpoint =
        user?.role === 'patient' || user?.role === 'doctor'
          ? '/appointments/me'
          : '/appointments/all';
      return mapAppointments(await apiFetch(endpoint));
    },
    enabled: !!user,
  });

  const handleCancel = async (id: string) => {
    try {
      await apiFetch(`/appointments/${id}/cancel`, { method: 'PATCH' });
      toast.success('Cita cancelada exitosamente');
      refetch();
    } catch (err: any) {
      toast.error(err.message || 'Error al cancelar la cita');
    }
  };

  const handleAssign = async (appt: Appointment) => {
    try {
      const raw = await apiFetch<Record<string, unknown>[]>(
        `/doctors${appt.specialty ? `?specialty=${encodeURIComponent(appt.specialty)}` : ''}`
      );
      const doctors = (raw || []).map((d) => ({
        id: String(d.id),
        fullName: String(d.full_name ?? d.fullName ?? ''),
        specialty: String(d.specialty ?? ''),
      }));
      if (doctors.length === 0) {
        toast.error('No hay médicos disponibles para esta especialidad');
        return;
      }
      const list = doctors.map((d, i) => `${i + 1}. ${d.fullName} (${d.specialty})`).join('\n');
      const choice = window.prompt(`Seleccione el número del médico a asignar:\n${list}`);
      const idx = choice ? parseInt(choice, 10) - 1 : -1;
      if (idx < 0 || idx >= doctors.length) return;
      await apiFetch(`/appointments/${appt.id}/assign`, {
        method: 'PATCH',
        body: JSON.stringify({ doctorId: doctors[idx].id }),
      });
      toast.success(`Médico asignado: ${doctors[idx].fullName}`);
      refetch();
    } catch (err: any) {
      toast.error(err.message || 'Error al asignar médico');
    }
  };

  const handleStatusUpdate = async (id: string, newStatus: AppointmentStatus) => {
    try {
      await apiFetch(`/appointments/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      toast.success(`Estado actualizado a ${newStatus}`);
      refetch();
    } catch (err: any) {
      toast.error(err.message || 'Error al actualizar el estado');
    }
  };

  const filteredAppointments = appointments?.filter(a => {
    const matchesSearch = a.reason?.toLowerCase().includes(search.toLowerCase()) ||
                          a.doctorName?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || a.status === statusFilter;
    return matchesSearch && matchesStatus;
  }) || [];

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Citas Médicas</h1>
          <p className="text-slate-500">Gestiona y supervisa la agenda de consultas</p>
        </div>
        <Link href="/appointments/new">
          {(user?.role === 'patient' || user?.role === 'staff' || user?.role === 'admin') && (
          <Button className="bg-sky-600 hover:bg-sky-700 text-white gap-2 rounded-xl py-6">
            <Plus className="w-4 h-4" />
            Agendar Nueva Cita
          </Button>
          )}
        </Link>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-500">Filtros</span>
          </div>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full sm:w-auto">
            <Input
              placeholder="Buscar por motivo o médico..."
              className="w-full sm:w-64 h-9 bg-slate-50"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select
              className="h-9 px-3 rounded-lg border border-slate-200 bg-white text-sm text-slate-600 focus:ring-2 focus:ring-sky-500 outline-none"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">Todos los estados</option>
              {Object.entries(APPOINTMENT_STATUSES).map(([key, { label }]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-20 text-center space-y-4">
              <div className="w-12 h-12 bg-slate-100 rounded-full mx-auto animate-pulse" />
              <p className="text-slate-400">Cargando citas...</p>
            </div>
          ) : filteredAppointments.length === 0 ? (
            <div className="py-20 text-center space-y-3">
              <CalendarDays className="w-12 h-12 text-slate-300 mx-auto" />
              <p className="text-slate-500 font-medium">No se encontraron citas con los criterios seleccionados</p>
              <Button variant="link" onClick={() => {setSearch(''); setStatusFilter('all');}}>
                Limpiar filtros
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-slate-500 font-medium">Paciente / Médico</TableHead>
                    <TableHead className="text-slate-500 font-medium">Fecha y Hora</TableHead>
                    <TableHead className="text-slate-500 font-medium">Motivo</TableHead>
                    <TableHead className="text-slate-500 font-medium text-center">Estado</TableHead>
                    <TableHead className="text-slate-500 font-medium text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAppointments.map((a) => (
                    <TableRow key={a.id} className="group hover:bg-slate-50/50 transition-colors">
                      <TableCell className="font-medium text-slate-900">
                        <div className="flex flex-col">
                          <span>{a.patientName || 'Paciente'}</span>
                          <span className="text-xs text-slate-400">{a.doctorName || 'Dr. Asignado'}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-600">
                        <div className="flex flex-col">
                          {a.startTime ? (
                            <>
                              <span className="text-sm font-medium">{new Date(a.startTime).toLocaleDateString()}</span>
                              <span className="text-xs text-slate-400">
                                {new Date(a.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </>
                          ) : (
                            <>
                              <span className="text-sm font-medium">{new Date(a.createdAt).toLocaleDateString()}</span>
                              <span className="text-xs text-slate-400">Pendiente de horario</span>
                            </>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-500 max-w-xs truncate">
                        {a.reason || 'Consulta general'}
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge className={cn("px-2 py-0.5 border", APPOINTMENT_STATUSES[a.status as keyof typeof APPOINTMENT_STATUSES]?.color)}>
                          {APPOINTMENT_STATUSES[a.status as keyof typeof APPOINTMENT_STATUSES]?.label || a.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex flex-wrap justify-end gap-2">
                          {user?.role === 'patient' && a.status === 'programada' && (
                            <Button variant="ghost" size="sm" className="text-rose-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg" onClick={() => handleCancel(a.id)}>
                              <XCircle className="w-4 h-4 mr-2" />
                              Cancelar
                            </Button>
                          )}
                          {(user?.role === 'staff' || user?.role === 'admin') && a.status !== 'cancelada' && a.status !== 'completada' && (
                            <Button variant="ghost" size="sm" className="text-violet-500 hover:text-violet-600 hover:bg-violet-50 rounded-lg" onClick={() => handleAssign(a)}>
                              Asignar médico
                            </Button>
                          )}
                          {(user?.role === 'staff' || user?.role === 'admin') && a.status !== 'cancelada' && a.status !== 'completada' && (
                            <Button variant="ghost" size="sm" className="text-sky-500 hover:text-sky-600 hover:bg-sky-50 rounded-lg" onClick={() => router.push(`/appointments/${a.id}`)}>
                              <RefreshCw className="w-4 h-4 mr-2" />
                              Reagendar
                            </Button>
                          )}
                          {(user?.role === 'staff' || user?.role === 'admin') && a.status === 'programada' && (
                            <Button variant="ghost" size="sm" className="text-indigo-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg" onClick={() => handleStatusUpdate(a.id, 'confirmada' as AppointmentStatus)}>
                              Confirmar
                            </Button>
                          )}
                          {user?.role === 'doctor' && a.status === 'confirmada' && (
                            <Button variant="ghost" size="sm" className="text-amber-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg" onClick={() => handleStatusUpdate(a.id, 'en_atencion' as AppointmentStatus)}>
                              Iniciar
                            </Button>
                          )}
                          {user?.role === 'doctor' && a.status === 'en_atencion' && (
                            <Button variant="ghost" size="sm" className="text-emerald-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg" onClick={() => handleStatusUpdate(a.id, 'completada' as AppointmentStatus)}>
                              <CheckCircle2 className="w-4 h-4 mr-2" />
                              Completar
                            </Button>
                          )}
                          <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-600 rounded-lg">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
