import { Invoice, Payment } from '@/types';

/** Maps billing-service snake_case invoice payloads to frontend types. */
export function mapInvoice(raw: Record<string, unknown>): Invoice {
  return {
    id: String(raw.id),
    appointmentId: String(raw.appointment_id ?? raw.appointmentId ?? ''),
    patientId: String(raw.patient_id ?? raw.patientId ?? ''),
    doctorId: String(raw.doctor_id ?? raw.doctorId ?? ''),
    amount: Number(raw.amount ?? 0),
    status: (raw.status as Invoice['status']) ?? 'pendiente',
    description: raw.description ? String(raw.description) : '',
    createdAt: String(raw.created_at ?? raw.createdAt ?? ''),
  };
}

export function mapInvoices(raw: unknown): Invoice[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item) => mapInvoice(item as Record<string, unknown>));
}

/** Maps billing-service snake_case payment payloads to frontend types. */
export function mapPayment(raw: Record<string, unknown>): Payment {
  return {
    id: String(raw.id),
    invoiceId: String(raw.invoice_id ?? raw.invoiceId ?? ''),
    amount: Number(raw.amount ?? 0),
    method: String(raw.method ?? ''),
    status: String(raw.status ?? ''),
    transactionRef: String(raw.transaction_ref ?? raw.transactionRef ?? ''),
    createdAt: String(raw.created_at ?? raw.createdAt ?? ''),
  };
}

export function mapPayments(raw: unknown): Payment[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item) => mapPayment(item as Record<string, unknown>));
}
