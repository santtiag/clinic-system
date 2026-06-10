'use client';

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DollarSign, Wallet } from 'lucide-react';
import { toast } from 'sonner';

export default function BillingCheckoutPage() {
  const queryClient = useQueryClient();

  const { data: invoices, isLoading } = useQuery<any[]>({
    queryKey: ['checkout-pending'],
    queryFn: () => apiFetch('/invoices/pending'),
  });

  const payMutation = useMutation({
    mutationFn: (inv: any) =>
      apiFetch('/payments', {
        method: 'POST',
        body: JSON.stringify({
          invoice_id: inv.id,
          amount: inv.amount,
          method: 'efectivo',
          transaction_ref: `CASH-${Date.now()}`,
        }),
      }),
    onSuccess: () => {
      toast.success('Pago registrado en caja');
      queryClient.invalidateQueries({ queryKey: ['checkout-pending'] });
    },
    onError: (err: any) => toast.error(err.message),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
          <Wallet className="w-8 h-8 text-sky-500" />
          Caja / Cobros
        </h1>
        <p className="text-slate-500">Registrar pagos de consultas completadas</p>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardHeader>
          <CardTitle>Facturas Pendientes de Cobro</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-center py-12 text-slate-400">Cargando...</p>
          ) : !invoices?.length ? (
            <p className="text-center py-12 text-slate-500">No hay facturas pendientes</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Factura</TableHead>
                  <TableHead>Monto</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((inv) => (
                  <TableRow key={inv.id}>
                    <TableCell className="font-mono text-xs">{inv.id.slice(0, 8)}...</TableCell>
                    <TableCell className="font-bold">${inv.amount}</TableCell>
                    <TableCell>
                      <Badge className="bg-amber-50 text-amber-700 border-amber-200">{inv.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        className="gap-1 bg-emerald-600 hover:bg-emerald-700"
                        onClick={() => payMutation.mutate(inv)}
                      >
                        <DollarSign className="w-4 h-4" />
                        Cobrar
                      </Button>
                    </TableCell>
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
