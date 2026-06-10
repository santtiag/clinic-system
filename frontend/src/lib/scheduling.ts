import { Appointment, AvailabilitySlot } from '@/types';

/** Maps scheduling-service snake_case slot payloads to frontend types. */
export function mapAvailabilitySlot(raw: Record<string, unknown>): AvailabilitySlot {
  return {
    id: String(raw.id),
    doctorId: String(raw.doctor_id ?? raw.doctorId ?? ''),
    startTime: String(raw.start_time ?? raw.startTime ?? ''),
    endTime: String(raw.end_time ?? raw.endTime ?? ''),
    doctorName: raw.doctor_name ? String(raw.doctor_name) : raw.doctorName ? String(raw.doctorName) : undefined,
    specialty: raw.specialty ? String(raw.specialty) : undefined,
  };
}

export function mapAvailabilitySlots(raw: unknown): AvailabilitySlot[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item) => mapAvailabilitySlot(item as Record<string, unknown>));
}

/** Maps scheduling-service snake_case appointment payloads to frontend types. */
export function mapAppointment(raw: Record<string, unknown>): Appointment {
  return {
    id: String(raw.id),
    patientId: String(raw.patient_id ?? raw.patientId ?? ''),
    doctorId: String(raw.doctor_id ?? raw.doctorId ?? ''),
    slotId: String(raw.slot_id ?? raw.slotId ?? ''),
    status: (raw.status as Appointment['status']) ?? 'programada',
    reason: raw.reason ? String(raw.reason) : '',
    createdAt: String(raw.created_at ?? raw.createdAt ?? ''),
    startTime: raw.start_time ? String(raw.start_time) : raw.startTime ? String(raw.startTime) : undefined,
    endTime: raw.end_time ? String(raw.end_time) : raw.endTime ? String(raw.endTime) : undefined,
    doctorName: raw.doctor_name ? String(raw.doctor_name) : raw.doctorName ? String(raw.doctorName) : undefined,
    patientName: raw.patient_name ? String(raw.patient_name) : raw.patientName ? String(raw.patientName) : undefined,
    specialty: raw.specialty ? String(raw.specialty) : undefined,
  };
}

export function mapAppointments(raw: unknown): Appointment[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item) => mapAppointment(item as Record<string, unknown>));
}
