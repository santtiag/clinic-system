'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/providers/auth-provider';
import { apiFetch } from '@/lib/api';
import { MedicalRecord, EvolutionNote } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import {
  FileText,
  Plus,
  User,
  Clock,
  Stethoscope,
  ArrowLeft,
  Search,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function MedicalRecordPage() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [patientId, setPatientId] = useState('');
  const [observations, setObservations] = useState('');
  const [isAddingEvolution, setIsAddingEvolution] = useState(false);

  const { data: record, isLoading } = useQuery<MedicalRecord>({
    queryKey: ['medical-record', patientId],
    queryFn: async () => {
      return apiFetch(`/records/${patientId}`);
    },
    enabled: !!patientId,
  });

  const mutation = useMutation({
    mutationFn: async (obs: string) => {
      return apiFetch(`/records/${patientId}/evolutions`, {
        method: 'POST',
        body: JSON.stringify({ observations: obs }),
      });
    },
    onSuccess: () => {
      toast.success('Evolución clínica registrada');
      setObservations('');
      setIsAddingEvolution(false);
      queryClient.invalidateQueries({ queryKey: ['medical-record', patientId] });
    },
    onError: (err: any) => {
      toast.error(err.message || 'Error al registrar evolución');
    }
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (patientId) router.push(`/medical-records/${patientId}`);
  };

  useEffect(() => {
    if (user?.role === 'patient') {
      router.replace('/medical-records/me');
    }
  }, [user, router]);

  if (user?.role === 'patient') {
    return null;
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Historias Clínicas</h1>
          <p className="text-slate-500">Consulta y gestión de evoluciones médicas</p>
        </div>
      </div>

      {!patientId ? (
        <Card className="max-w-xl mx-auto border-none shadow-sm ring-1 ring-slate-200">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Search className="w-5 h-5 text-sky-500" />
              Buscar Paciente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="flex gap-3">
              <Input
                placeholder="Ingrese ID del paciente (UUID)..."
                className="flex-1"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
              />
              <Button type="submit" className="bg-sky-600 hover:bg-sky-700 text-white rounded-xl px-6">
                Acceder
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={() => setPatientId('')} className="rounded-lg">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver a la búsqueda
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <Card className="lg:col-span-1 border-none shadow-sm ring-1 ring-slate-200">
              <CardHeader className="flex flex-row items-center gap-3">
                <div className="p-2 bg-sky-100 rounded-lg">
                  <User className="w-5 h-5 text-sky-600" />
                </div>
                <CardTitle className="text-lg font-semibold">Ficha del Paciente</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-3">
                  <div>
                    <p className="text-xs text-slate-400 font-medium uppercase">ID Paciente</p>
                    <p className="text-sm font-mono text-slate-600 break-all">{patientId}</p>
                  </div>
                  <div className="pt-2 border-t border-slate-200">
                    <p className="text-xs text-slate-400 font-medium uppercase">Estado</p>
                    <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50">Activo</Badge>
                  </div>
                </div>
                <Button
                  onClick={() => setIsAddingEvolution(true)}
                  className="w-full bg-sky-600 hover:bg-sky-700 text-white gap-2 rounded-xl h-12"
                >
                  <Plus className="w-4 h-4" />
                  Agregar Evolución
                </Button>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2 border-none shadow-sm ring-1 ring-slate-200">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <FileText className="w-5 h-5 text-sky-500" />
                  Línea de Tiempo Clínica
                </CardTitle>
                <Badge variant="outline" className="text-slate-500">
                  {record?.evolutions.length || 0} Registros
                </Badge>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="py-20 text-center space-y-4">
                    <div className="w-12 h-12 bg-slate-100 rounded-full mx-auto animate-pulse" />
                    <p className="text-slate-400">Cargando historial clínico...</p>
                  </div>
                ) : record?.evolutions.length === 0 ? (
                  <div className="py-20 text-center space-y-3">
                    <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto text-slate-400">
                      <FileText className="w-8 h-8" />
                    </div>
                    <p className="text-slate-500 font-medium">Sin consultas previas registradas</p>
                  </div>
                ) : (
                  <div className="relative space-y-8 before:absolute before:left-6 before:top-0 before:bottom-0 before:w-0.5 before:bg-slate-200">
                    {record?.evolutions.map((note: EvolutionNote) => (
                      <div key={note.id} className="relative pl-12 group">
                        <div className="absolute left-0 top-1 w-12 h-12 rounded-full bg-white border-2 border-sky-500 flex items-center justify-center z-10 transition-transform group-hover:scale-110">
                          <Stethoscope className="w-5 h-5 text-sky-600" />
                        </div>
                        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-md transition-all group-hover:border-sky-200">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-xs font-bold text-sky-600 uppercase tracking-wider">Evolución Médica</span>
                            <div className="flex items-center gap-1 text-xs text-slate-400">
                              <Clock className="w-3 h-3" />
                              {new Date(note.createdAt).toLocaleString('es-ES')}
                            </div>
                          </div>
                          <p className="text-sm text-slate-700 leading-relaxed">
                            {note.observations}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {isAddingEvolution && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
              <Card className="w-full max-w-lg shadow-2xl border-none ring-1 ring-slate-200 animate-in zoom-in-95 duration-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold flex items-center gap-2">
                    <Plus className="w-5 h-5 text-sky-500" />
                    Nueva Evolución Clínica
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="observations">Observaciones Médicas</Label>
                    <Textarea
                      id="observations"
                      placeholder="Describa los hallazgos, diagnóstico y tratamiento..."
                      className="min-h-[200px] rounded-xl"
                      value={observations}
                      onChange={(e) => setObservations(e.target.value)}
                    />
                  </div>
                  <div className="flex justify-end gap-3 pt-4">
                    <Button variant="ghost" onClick={() => setIsAddingEvolution(false)} className="rounded-xl">
                      Cancelar
                    </Button>
                    <Button
                      onClick={() => mutation.mutate(observations)}
                      disabled={mutation.isPending || !observations}
                      className="bg-sky-600 hover:bg-sky-700 text-white rounded-xl px-8"
                    >
                      {mutation.isPending ? 'Guardando...' : 'Guardar Evolución'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
