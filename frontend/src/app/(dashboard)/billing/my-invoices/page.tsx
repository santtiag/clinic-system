'use client';

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiFetch } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { CreditCard, Download } from 'lucide-react';
import { toast } from 'sonner';

export default function MyInvoicesPage() {
  const queryClient = useQueryClient();

  const { data: invoices, isLoading } = useQuery<any[]>({
    queryKey: ['my-invoices'],
    queryFn: () => apiFetch('/invoices/me'),
  });

  const payMutation = useMutation({
    mutationFn: (inv: any) =>
      apiFetch('/payments', {
        method: 'POST',
        body: JSON.stringify({
          invoice_id: inv.id,
          amount: inv.amount,
          method: 'tarjeta',
          transaction_ref: `PAT-${Date.now()}`,
        }),
      }),
    onSuccess: () => {
      toast.success('Pago procesado');
      queryClient.invalidateQueries({ queryKey: ['my-invoices'] });
    },
    onError: (err: any) => toast.error(err.message),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
          <CreditCard className="w-8 h-8 text-sky-500" />
          Mis Facturas
        </h1>
        <p className="text-slate-500">Consulta y paga tus recibos de consulta</p>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardContent className="pt-6">
          {isLoading ? (
            <p className="text-center py-12 text-slate-400">Cargando...</p>
          ) : !invoices?.length ? (
            <p className="text-center py-12 text-slate-500">No tienes facturas registradas</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Monto</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoices.map((inv) => (
                  <TableRow key={inv.id}>
                    <TableCell>{inv.description || 'Consulta médica'}</TableCell>
                    <TableCell className="font-bold">${inv.amount}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{inv.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      {inv.status === 'pendiente' && (
                        <Button size="sm" onClick={() => payMutation.mutate(inv)} className="bg-sky-600">
                          Pagar
                        </Button>
                      )}
                      {inv.status === 'pagado' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => window.open(`${process.env.NEXT_PUBLIC_API_URL}/invoices/${inv.id}/receipt.pdf`, '_blank')}
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Recibo
                        </Button>
                      )}
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
