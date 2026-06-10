'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/providers/auth-provider';
import { apiFetch } from '@/lib/api';
import { Appointment, AvailabilitySlot } from '@/types';
import { mapAvailabilitySlots, mapAppointment } from '@/lib/scheduling';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import {
  CalendarDays,
  Clock,
  ArrowLeft,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';
import { useRouter, useParams } from 'next/navigation';
import { cn } from '@/lib/utils';

export default function ReschedulePage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();
  const appointmentId = params.id as string;

  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);

  const { data: appointment, isLoading: isLoadingAppt } = useQuery<Appointment>({
    queryKey: ['appointment', appointmentId],
    queryFn: async () => mapAppointment(await apiFetch(`/appointments/${appointmentId}`)),
  });

  const { data: slots, isLoading: isLoadingSlots } = useQuery<AvailabilitySlot[]>({
    queryKey: ['availability-reschedule', appointment?.specialty],
    queryFn: async () => {
      const params = appointment?.specialty
        ? `?specialty=${encodeURIComponent(appointment.specialty)}`
        : '';
      return mapAvailabilitySlots(await apiFetch(`/availability${params}`));
    },
    enabled: !!appointment,
  });

  const mutation = useMutation({
    mutationFn: async (slotId: string) => {
      return apiFetch<Appointment>('/appointments/' + appointmentId + '/reschedule', {
        method: 'PATCH',
        body: JSON.stringify({ new_slot_id: slotId }),
      });
    },
    onSuccess: () => {
      toast.success('Cita reprogramada exitosamente');
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      router.push('/appointments');
    },
    onError: (err: any) => {
      toast.error(err.message || 'Error al reprogramar la cita');
    }
  });

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => router.back()} className="rounded-xl">
          Volver
        </Button>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Reprogramar Cita</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-1 border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <CalendarDays className="w-5 h-5 text-sky-500" />
              Cita Actual
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoadingAppt ? (
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-slate-100 rounded w-3/4" />
                <div className="h-4 bg-slate-100 rounded w-1/2" />
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Estado:</span>
                  <span className="font-medium text-slate-900">{appointment?.status}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Motivo:</span>
                  <span className="font-medium text-slate-900 text-right">{appointment?.reason}</span>
                </div>
                <div className="pt-2 border-t border-slate-200 flex items-center gap-2 text-xs text-slate-400">
                  <Clock className="w-3 h-3" />
                  Creada el {appointment?.createdAt ? new Date(appointment.createdAt).toLocaleDateString() : '...'}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Clock className="w-5 h-5 text-sky-500" />
              Seleccionar Nuevo Horario
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingSlots ? (
              <div className="py-20 text-center space-y-4">
                <div className="w-12 h-12 bg-slate-100 rounded-full mx-auto animate-pulse" />
                <p className="text-slate-400">Cargando horarios disponibles...</p>
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
                          {new Date(slot.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span className="text-xs text-slate-500">
                          {new Date(slot.startTime).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                        </span>
                        {slot.doctorName && (
                          <span className="text-xs font-medium text-sky-700 mt-1">{slot.doctorName}</span>
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
            ) : (
              <div className="py-20 text-center space-y-3">
                <p className="text-slate-500 font-medium">No hay horarios disponibles para este médico.</p>
                <Button variant="outline" onClick={() => router.back()} className="rounded-xl">
                  Volver a la lista
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {selectedSlot && (
        <div className="flex justify-center pt-6">
          <Button
            onClick={() => mutation.mutate(selectedSlot)}
            disabled={mutation.isPending}
            className="bg-sky-600 hover:bg-sky-700 text-white font-medium px-12 py-6 rounded-2xl shadow-lg shadow-sky-200"
          >
            {mutation.isPending ? 'Reprogramando...' : 'Confirmar Cambio de Horario'}
          </Button>
        </div>
      )}
    </div>
  );
}
