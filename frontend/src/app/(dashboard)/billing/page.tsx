'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/providers/auth-provider';
import { apiFetch } from '@/lib/api';
import { mapInvoices } from '@/lib/billing';
import { Invoice, Payment } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  CreditCard,
  Receipt,
  DollarSign,
  Download,
  MoreVertical,
  Plus,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

export default function BillingPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const { data: invoices, isLoading, refetch } = useQuery<Invoice[]>({
    queryKey: ['invoices', statusFilter],
    queryFn: async () => {
      const endpoint = statusFilter === 'all' ? '/invoices' : `/invoices?status=${statusFilter}`;
      return mapInvoices(await apiFetch(endpoint));
    },
  });

  const paymentMutation = useMutation({
    mutationFn: async (payload: { invoice_id: string; amount: number; method: string }) => {
      return apiFetch<Payment>('/payments', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      toast.success('Pago procesado exitosamente');
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
    },
    onError: (err: any) => {
      toast.error(err.message || 'Error al procesar el pago');
    }
  });

  const filteredInvoices = invoices || [];

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Facturación</h1>
          <p className="text-slate-500">Gestión de recibos, pagos y reembolsos de servicios</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <Button variant="outline" className="gap-2 rounded-xl text-slate-600 hover:bg-slate-50" onClick={() => window.open(`${process.env.NEXT_PUBLIC_API_URL}/reports/export?report_type=income&format=csv`, '_blank')}>
            <Download className="w-4 h-4" />
            Exportar CSV
          </Button>
          <Button className="bg-sky-600 hover:bg-sky-700 text-white gap-2 rounded-xl">
            <Plus className="w-4 h-4" />
            Generar Factura
          </Button>
        </div>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Receipt className="w-5 h-5 text-sky-500" />
            Listado de Facturas
          </CardTitle>
          <select
            className="h-9 px-3 rounded-lg border border-slate-200 bg-white text-sm text-slate-600 focus:ring-2 focus:ring-sky-500 outline-none w-full sm:w-auto"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Todos los estados</option>
            <option value="pendiente">Pendientes</option>
            <option value="pagado">Pagados</option>
            <option value="reembolsado">Reembolsados</option>
          </select>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-20 text-center space-y-4">
              <div className="w-12 h-12 bg-slate-100 rounded-full mx-auto animate-pulse" />
              <p className="text-slate-400">Cargando facturas...</p>
            </div>
          ) : filteredInvoices.length === 0 ? (
            <div className="py-20 text-center space-y-3">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto text-slate-400">
                <CreditCard className="w-8 h-8" />
              </div>
              <p className="text-slate-500 font-medium">No se encontraron facturas para este filtro</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-slate-500 font-medium">ID Factura</TableHead>
                    <TableHead className="text-slate-500 font-medium">Paciente / Médico</TableHead>
                    <TableHead className="text-slate-500 font-medium">Monto</TableHead>
                    <TableHead className="text-slate-500 font-medium text-center">Estado</TableHead>
                    <TableHead className="text-slate-500 font-medium text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredInvoices.map((inv) => (
                    <TableRow key={inv.id} className="group hover:bg-slate-50/50 transition-colors">
                      <TableCell className="font-mono text-xs text-slate-500">
                        {inv.id.substring(0, 8)}...
                      </TableCell>
                      <TableCell className="text-slate-900">
                        <span className="font-medium">{(inv.patientId || '—').substring(0, 8)}...</span>
                        <span className="text-slate-400 ml-2">/</span>
                        <span className="text-slate-500">{(inv.doctorId || '—').substring(0, 8)}...</span>
                      </TableCell>
                      <TableCell className="font-bold text-slate-900">
                        ${inv.amount.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline" className={cn(
                          "px-2 py-0.5 border",
                          inv.status === 'pagado' ? 'text-emerald-600 border-emerald-200 bg-emerald-50' :
                          inv.status === 'pendiente' ? 'text-amber-600 border-amber-200 bg-amber-50' :
                          'text-slate-500 border-slate-200 bg-slate-50'
                        )}>
                          {inv.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          {inv.status === 'pendiente' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-sky-600 hover:text-sky-700 hover:bg-sky-50 rounded-lg gap-1"
                              onClick={() => paymentMutation.mutate({ invoice_id: inv.id, amount: inv.amount, method: 'tarjeta' })}
                            >
                              <DollarSign className="w-3 h-3" />
                              Pagar
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
