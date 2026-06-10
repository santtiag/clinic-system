'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, Stethoscope, Clock } from 'lucide-react';

export default function MyMedicalRecordPage() {
  const { data: record, isLoading } = useQuery<any>({
    queryKey: ['my-medical-record'],
    queryFn: () => apiFetch('/records/me'),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Mi Historia Clínica</h1>
        <p className="text-slate-500">Consulta segura de tus registros médicos personales</p>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-sky-500" />
            Línea de Tiempo
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-slate-400 py-12 text-center">Cargando...</p>
          ) : !record?.evolutions?.length ? (
            <p className="text-slate-500 py-12 text-center">No hay registros clínicos disponibles aún</p>
          ) : (
            <div className="space-y-6">
              {record.evolutions.map((note: any) => (
                <div key={note.id} className="p-4 rounded-xl border border-slate-200">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="outline" className="gap-1">
                      <Stethoscope className="w-3 h-3" />
                      Evolución
                    </Badge>
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(note.created_at).toLocaleString('es-ES')}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700">{note.observations}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
