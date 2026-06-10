'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ClipboardList } from 'lucide-react';

export default function AdminAuditPage() {
  const [userId, setUserId] = useState('');
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');

  const { data: logs, refetch, isLoading } = useQuery<any[]>({
    queryKey: ['admin-audit', userId, start, end],
    queryFn: () => {
      const params = new URLSearchParams();
      if (userId) params.set('user_id', userId);
      if (start) params.set('start', start);
      if (end) params.set('end', end);
      return apiFetch(`/admin/audit?${params.toString()}`);
    },
    enabled: false,
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
          <ClipboardList className="w-8 h-8 text-sky-500" />
          Auditoría del Sistema
        </h1>
        <p className="text-slate-500">Historial de cambios y eventos registrados</p>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Input placeholder="ID de usuario" value={userId} onChange={(e) => setUserId(e.target.value)} className="max-w-xs" />
          <Input type="date" value={start} onChange={(e) => setStart(e.target.value)} />
          <Input type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
          <Button onClick={() => refetch()} className="bg-sky-600 hover:bg-sky-700">Buscar</Button>
        </CardContent>
      </Card>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardContent className="pt-6">
          {isLoading ? (
            <p className="text-center py-12 text-slate-400">Cargando...</p>
          ) : !logs?.length ? (
            <p className="text-center py-12 text-slate-500">No se han registrado cambios para los criterios seleccionados</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Evento</TableHead>
                  <TableHead>Detalle</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="text-sm">{new Date(log.occurredAt).toLocaleString('es-ES')}</TableCell>
                    <TableCell className="font-mono text-xs">{log.routingKey}</TableCell>
                    <TableCell className="text-xs text-slate-500 max-w-md truncate">{log.payload}</TableCell>
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
