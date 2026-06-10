import { Invoice } from '@/types';

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
