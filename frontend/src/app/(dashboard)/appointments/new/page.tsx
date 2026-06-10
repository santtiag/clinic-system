'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/providers/auth-provider';
import { apiFetch } from '@/lib/api';
import { AvailabilitySlot, Appointment } from '@/types';
import { SPECIALTIES } from '@/lib/constants';
import { mapAvailabilitySlots } from '@/lib/scheduling';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  CalendarDays,
  Search,
  Clock,
  User,
  Stethoscope,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Textarea } from '@/components/ui/textarea';

export default function NewAppointmentPage() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>('');
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [reason, setReason] = useState('');

  const { data: slots, isLoading: isLoadingSlots, isError: isSlotsError } = useQuery<AvailabilitySlot[]>({
    queryKey: ['availability', selectedSpecialty],
    queryFn: async () => {
      const params = selectedSpecialty ? `?specialty=${encodeURIComponent(selectedSpecialty)}` : '';
      const data = await apiFetch<unknown>(`/availability${params}`);
      return mapAvailabilitySlots(data);
    },
    enabled: !!selectedSpecialty,
  });

  const mutation = useMutation({
    mutationFn: async (payload: { slot_id: string; reason: string }) => {
      return apiFetch<Appointment>('/appointments', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      toast.success('Cita agendada exitosamente');
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      router.push('/appointments');
    },
    onError: (err: any) => {
      toast.error(err.message || 'Error al agendar la cita');
    }
  });

  const handleBook = () => {
    if (!selectedSlot) return;
    mutation.mutate({ slot_id: selectedSlot, reason });
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => router.back()} className="rounded-xl">
          Volver
        </Button>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Agendar Cita</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-1 border-none shadow-sm ring-1 ring-slate-200 h-fit">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Search className="w-5 h-5 text-sky-500" />
              Búsqueda de Especialista
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Especialidad Médica</Label>
              <Select onValueChange={(value) => setSelectedSpecialty(value ?? '')} value={selectedSpecialty}>
                <SelectTrigger className="w-full rounded-xl">
                  <SelectValue placeholder="Seleccione especialidad..." />
                </SelectTrigger>
                <SelectContent>
                  {SPECIALTIES.map(s => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {!selectedSpecialty && (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center space-y-2">
                <Stethoscope className="w-8 h-8 text-slate-300 mx-auto" />
                <p className="text-sm text-slate-500">Por favor seleccione una especialidad para ver los horarios disponibles.</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <CalendarDays className="w-5 h-5 text-sky-500" />
              Horarios Disponibles
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingSlots ? (
              <div className="py-20 text-center space-y-4">
                <div className="w-12 h-12 bg-slate-100 rounded-full mx-auto animate-pulse" />
                <p className="text-slate-400">Buscando espacios disponibles...</p>
              </div>
            ) : isSlotsError ? (
              <div className="py-20 text-center space-y-3">
                <p className="text-rose-500 font-medium">Error al cargar horarios. Intente de nuevo.</p>
              </div>
            ) : slots && slots.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {slots.map((slot) => (
                  <div
                    key={slot.id}
                    onClick={() => setSelectedSlot(slot.id)}
                    className={cn(
                      "p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-center justify-between",
                      selectedSlot === slot.id
                        ? "border-sky-500 bg-sky-50 shadow-md ring-1 ring-sky-500"
                        : "border-slate-100 bg-white hover:border-sky-200 hover:bg-slate-50"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-white rounded-lg border border-slate-200 shadow-sm">
                        <Clock className="w-4 h-4 text-sky-600" />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-900">
                          {slot.startTime
                            ? new Date(slot.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                            : '—'}
                        </span>
                        <span className="text-xs text-slate-500">
                          {slot.startTime
                            ? new Date(slot.startTime).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
                            : ''}
                        </span>
                        {slot.doctorName && (
                          <span className="text-xs font-medium text-sky-700 mt-1">
                            {slot.doctorName}
                          </span>
                        )}
                        {slot.specialty && (
                          <span className="text-[11px] text-slate-400">{slot.specialty}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {selectedSlot === slot.id ? (
                        <CheckCircle2 className="w-5 h-5 text-sky-600" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-slate-300" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : selectedSpecialty && (
              <div className="py-20 text-center space-y-3">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto text-slate-400">
                  <Search className="w-8 h-8" />
                </div>
                <p className="text-slate-500 font-medium">No hay horarios disponibles para esta especialidad.</p>
                <Button variant="outline" onClick={() => setSelectedSpecialty('')} className="rounded-xl">
                  Cambiar especialidad
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {selectedSlot && (
        <Card className="max-w-2xl mx-auto border-none shadow-lg ring-2 ring-sky-500 animate-in fade-in slide-in-from-bottom-4 duration-300">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <User className="w-5 h-5 text-sky-500" />
              Confirmar Detalles de la Cita
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="reason">Motivo de la Consulta</Label>
              <Textarea
                id="reason"
                placeholder="Describa brevemente el motivo de su cita..."
                className="min-h-[100px] rounded-xl"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>
            <div className="flex items-center justify-end gap-3 pt-4">
              <Button
                variant="ghost"
                onClick={() => setSelectedSlot(null)}
                className="rounded-xl"
              >
                Cancelar
              </Button>
              <Button
                onClick={handleBook}
                disabled={mutation.isPending}
                className="bg-sky-600 hover:bg-sky-700 text-white font-medium px-8 rounded-xl py-6"
              >
                {mutation.isPending ? 'Confirmando...' : 'Confirmar Reserva'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
