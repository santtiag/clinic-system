'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiFetch, apiDownload } from '@/lib/api';
import { mapInvoices, mapPayments } from '@/lib/billing';
import { mapAppointments } from '@/lib/scheduling';
import { Appointment, Invoice, Payment } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  CreditCard,
  Receipt,
  DollarSign,
  Download,
  MoreVertical,
  Plus,
  Eye,
  RotateCcw,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

export default function BillingPage() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const [generateOpen, setGenerateOpen] = useState(false);
  const [selectedAppointmentId, setSelectedAppointmentId] = useState('');
  const [amount, setAmount] = useState('50');
  const [description, setDescription] = useState('Consulta médica');

  const [detailInvoice, setDetailInvoice] = useState<Invoice | null>(null);
  const [refundInvoice, setRefundInvoice] = useState<Invoice | null>(null);
  const [refundPaymentId, setRefundPaymentId] = useState('');
  const [refundAmount, setRefundAmount] = useState('');
  const [refundReason, setRefundReason] = useState('');

  const { data: invoices, isLoading } = useQuery<Invoice[]>({
    queryKey: ['invoices', statusFilter],
    queryFn: async () => {
      const endpoint = statusFilter === 'all' ? '/invoices' : `/invoices?status=${statusFilter}`;
      return mapInvoices(await apiFetch(endpoint));
    },
  });

  const { data: appointments } = useQuery<Appointment[]>({
    queryKey: ['appointments-for-billing'],
    queryFn: async () => mapAppointments(await apiFetch('/appointments/all')),
    enabled: generateOpen,
  });

  const { data: detailPayments, isLoading: detailPaymentsLoading } = useQuery<Payment[]>({
    queryKey: ['invoice-payments', detailInvoice?.id],
    queryFn: async () => mapPayments(await apiFetch(`/invoices/${detailInvoice!.id}/payments`)),
    enabled: !!detailInvoice,
  });

  const { data: refundPayments, isLoading: refundPaymentsLoading } = useQuery<Payment[]>({
    queryKey: ['invoice-payments-refund', refundInvoice?.id],
    queryFn: async () => mapPayments(await apiFetch(`/invoices/${refundInvoice!.id}/payments`)),
    enabled: !!refundInvoice,
  });

  const selectedAppointment = appointments?.find((a) => a.id === selectedAppointmentId);

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
    onError: (err: Error) => {
      toast.error(err.message || 'Error al procesar el pago');
    },
  });

  const generateMutation = useMutation({
    mutationFn: async (payload: {
      appointment_id: string;
      patient_id: string;
      doctor_id: string;
      amount: number;
      description: string;
    }) => {
      return apiFetch('/invoices', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      toast.success('Factura generada exitosamente');
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      setGenerateOpen(false);
      setSelectedAppointmentId('');
      setAmount('50');
      setDescription('Consulta médica');
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Error al generar la factura');
    },
  });

  const refundMutation = useMutation({
    mutationFn: async (payload: { payment_id: string; amount: number; reason: string }) => {
      return apiFetch('/refunds', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    onSuccess: () => {
      toast.success('Reembolso procesado exitosamente');
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      setRefundInvoice(null);
      setRefundPaymentId('');
      setRefundAmount('');
      setRefundReason('');
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Error al procesar el reembolso');
    },
  });

  const handleGenerate = () => {
    if (!selectedAppointment) {
      toast.error('Selecciona una cita');
      return;
    }
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      toast.error('Ingresa un monto válido');
      return;
    }
    generateMutation.mutate({
      appointment_id: selectedAppointment.id,
      patient_id: selectedAppointment.patientId,
      doctor_id: selectedAppointment.doctorId,
      amount: parsedAmount,
      description: description.trim() || 'Consulta médica',
    });
  };

  const handleOpenRefund = (inv: Invoice) => {
    setRefundInvoice(inv);
    setRefundPaymentId('');
    setRefundAmount('');
    setRefundReason('');
  };

  const handleRefundPaymentSelect = (paymentId: string) => {
    setRefundPaymentId(paymentId);
    const payment = refundPayments?.find((p) => p.id === paymentId);
    if (payment) {
      setRefundAmount(String(payment.amount));
    }
  };

  const handleRefund = () => {
    if (!refundPaymentId) {
      toast.error('Selecciona un pago');
      return;
    }
    const parsedAmount = parseFloat(refundAmount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      toast.error('Ingresa un monto válido');
      return;
    }
    refundMutation.mutate({
      payment_id: refundPaymentId,
      amount: parsedAmount,
      reason: refundReason.trim() || 'Reembolso solicitado',
    });
  };

  const downloadReceipt = async (invoiceId: string) => {
    try {
      await apiDownload(`/invoices/${invoiceId}/receipt.pdf`, `receipt_${invoiceId}.pdf`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Error al descargar el recibo');
    }
  };

  const filteredInvoices = invoices || [];

  const statusBadgeClass = (status: Invoice['status']) =>
    cn(
      'px-2 py-0.5 border',
      status === 'pagado' ? 'text-emerald-600 border-emerald-200 bg-emerald-50' :
      status === 'pendiente' ? 'text-amber-600 border-amber-200 bg-amber-50' :
      status === 'reembolsado' ? 'text-violet-600 border-violet-200 bg-violet-50' :
      'text-slate-500 border-slate-200 bg-slate-50'
    );

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Facturación</h1>
          <p className="text-slate-500">Gestión de recibos, pagos y reembolsos de servicios</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            variant="outline"
            className="gap-2 rounded-xl text-slate-600 hover:bg-slate-50"
            onClick={async () => {
              try {
                await apiDownload('/reports/export?report_type=income&format=csv', 'income_report.csv');
                toast.success('Reporte exportado exitosamente');
              } catch (err: unknown) {
                toast.error(err instanceof Error ? err.message : 'Error al exportar reporte');
              }
            }}
          >
            <Download className="w-4 h-4" />
            Exportar CSV
          </Button>
          <Button
            className="bg-sky-600 hover:bg-sky-700 text-white gap-2 rounded-xl"
            onClick={() => setGenerateOpen(true)}
          >
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
                        <Badge variant="outline" className={statusBadgeClass(inv.status)}>
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
                              onClick={() => paymentMutation.mutate({
                                invoice_id: inv.id,
                                amount: inv.amount,
                                method: 'tarjeta',
                              })}
                              disabled={paymentMutation.isPending}
                            >
                              <DollarSign className="w-3 h-3" />
                              Pagar
                            </Button>
                          )}
                          <DropdownMenu>
                            <DropdownMenuTrigger
                              render={
                                <Button variant="ghost" size="sm" className="text-slate-400 hover:text-slate-600 rounded-lg">
                                  <MoreVertical className="w-4 h-4" />
                                </Button>
                              }
                            />
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => setDetailInvoice(inv)}>
                                <Eye className="w-4 h-4" />
                                Ver detalle
                              </DropdownMenuItem>
                              {(inv.status === 'pagado' || inv.status === 'reembolsado') && (
                                <DropdownMenuItem onClick={() => downloadReceipt(inv.id)}>
                                  <Download className="w-4 h-4" />
                                  Descargar recibo
                                </DropdownMenuItem>
                              )}
                              {inv.status === 'pagado' && (
                                <>
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem
                                    variant="destructive"
                                    onClick={() => handleOpenRefund(inv)}
                                  >
                                    <RotateCcw className="w-4 h-4" />
                                    Reembolsar
                                  </DropdownMenuItem>
                                </>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
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

      {/* Dialog: Generar Factura */}
      <Dialog open={generateOpen} onOpenChange={setGenerateOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Generar Factura</DialogTitle>
            <DialogDescription>
              Selecciona una cita existente para generar el recibo de cobro.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="appointment">Cita</Label>
              <select
                id="appointment"
                className="w-full h-9 px-3 rounded-lg border border-slate-200 bg-white text-sm text-slate-600 focus:ring-2 focus:ring-sky-500 outline-none"
                value={selectedAppointmentId}
                onChange={(e) => setSelectedAppointmentId(e.target.value)}
              >
                <option value="">Seleccionar cita...</option>
                {(appointments || []).map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.patientName || 'Paciente'} / {a.doctorName || 'Médico'}
                    {a.startTime ? ` — ${new Date(a.startTime).toLocaleDateString()}` : ''}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="amount">Monto ($)</Label>
              <Input
                id="amount"
                type="number"
                min="0"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Descripción</Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Consulta médica"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setGenerateOpen(false)}>
              Cancelar
            </Button>
            <Button
              className="bg-sky-600 hover:bg-sky-700"
              onClick={handleGenerate}
              disabled={generateMutation.isPending || !selectedAppointmentId}
            >
              {generateMutation.isPending ? 'Generando...' : 'Generar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog: Detalle de Factura */}
      <Dialog open={!!detailInvoice} onOpenChange={(open) => !open && setDetailInvoice(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Detalle de Factura</DialogTitle>
            <DialogDescription>
              Información completa y pagos asociados.
            </DialogDescription>
          </DialogHeader>
          {detailInvoice && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-slate-500">ID</p>
                  <p className="font-mono text-xs">{detailInvoice.id}</p>
                </div>
                <div>
                  <p className="text-slate-500">Estado</p>
                  <Badge variant="outline" className={statusBadgeClass(detailInvoice.status)}>
                    {detailInvoice.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-slate-500">Monto</p>
                  <p className="font-bold">${detailInvoice.amount.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-slate-500">Fecha</p>
                  <p>{detailInvoice.createdAt ? new Date(detailInvoice.createdAt).toLocaleString() : '—'}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-slate-500">Descripción</p>
                  <p>{detailInvoice.description || 'Consulta médica'}</p>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-slate-700 mb-2">Pagos asociados</p>
                {detailPaymentsLoading ? (
                  <p className="text-sm text-slate-400">Cargando pagos...</p>
                ) : !detailPayments?.length ? (
                  <p className="text-sm text-slate-400">Sin pagos registrados</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Método</TableHead>
                        <TableHead>Monto</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Ref.</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {detailPayments.map((p) => (
                        <TableRow key={p.id}>
                          <TableCell>{p.method}</TableCell>
                          <TableCell className="font-medium">${p.amount}</TableCell>
                          <TableCell>{p.status}</TableCell>
                          <TableCell className="font-mono text-xs">{p.transactionRef}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailInvoice(null)}>
              Cerrar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog: Reembolso */}
      <Dialog open={!!refundInvoice} onOpenChange={(open) => !open && setRefundInvoice(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Procesar Reembolso</DialogTitle>
            <DialogDescription>
              Selecciona el pago a reembolsar e indica el monto y motivo.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {refundPaymentsLoading ? (
              <p className="text-sm text-slate-400">Cargando pagos...</p>
            ) : !refundPayments?.length ? (
              <p className="text-sm text-slate-400">No hay pagos disponibles para reembolsar</p>
            ) : (
              <>
                <div className="space-y-2">
                  <Label htmlFor="refund-payment">Pago</Label>
                  <select
                    id="refund-payment"
                    className="w-full h-9 px-3 rounded-lg border border-slate-200 bg-white text-sm text-slate-600 focus:ring-2 focus:ring-sky-500 outline-none"
                    value={refundPaymentId}
                    onChange={(e) => handleRefundPaymentSelect(e.target.value)}
                  >
                    <option value="">Seleccionar pago...</option>
                    {refundPayments.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.method} — ${p.amount} ({p.transactionRef})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="refund-amount">Monto a reembolsar ($)</Label>
                  <Input
                    id="refund-amount"
                    type="number"
                    min="0"
                    step="0.01"
                    value={refundAmount}
                    onChange={(e) => setRefundAmount(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="refund-reason">Motivo</Label>
                  <Input
                    id="refund-reason"
                    value={refundReason}
                    onChange={(e) => setRefundReason(e.target.value)}
                    placeholder="Motivo del reembolso"
                  />
                </div>
              </>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRefundInvoice(null)}>
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={handleRefund}
              disabled={refundMutation.isPending || !refundPaymentId}
            >
              {refundMutation.isPending ? 'Procesando...' : 'Reembolsar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
