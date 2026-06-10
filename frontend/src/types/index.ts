export enum Role {
  PATIENT = 'patient',
  DOCTOR = 'doctor',
  ADMIN = 'admin',
  STAFF = 'staff',
}

export type User = {
  id: string;
  username: string;
  email: string;
  role: Role;
  dni: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
};

export type AppointmentStatus = 'programada' | 'confirmada' | 'en_atencion' | 'completada' | 'cancelada';

export type Appointment = {
  id: string;
  patientId: string;
  doctorId: string;
  slotId: string;
  status: AppointmentStatus;
  reason: string;
  createdAt: string;
  startTime?: string;
  endTime?: string;
  doctorName?: string;
  patientName?: string;
  specialty?: string;
};

export type Doctor = {
  id: string;
  userId: string;
  fullName: string;
  specialty: string;
};

export type AvailabilitySlot = {
  id: string;
  doctorId: string;
  startTime: string;
  endTime: string;
  doctorName?: string;
  specialty?: string;
};

export type EvolutionNote = {
  id: string;
  recordId: string;
  doctorId: string;
  observations: string;
  createdAt: string;
};

export type MedicalRecord = {
  recordId: string;
  patientId: string;
  evolutions: EvolutionNote[];
};

export type InvoiceStatus = 'pendiente' | 'pagado' | 'fallido' | 'cancelado' | 'reembolsado';

export type Invoice = {
  id: string;
  appointmentId: string;
  patientId: string;
  doctorId: string;
  amount: number;
  status: InvoiceStatus;
  description: string;
  createdAt: string;
};

export type Payment = {
  id: string;
  invoiceId: string;
  amount: number;
  method: string;
  status: string;
  transactionRef: string;
  createdAt: string;
};

export type IncomeReport = {
  totalIncome: number;
  count: number;
  invoices: any[];
};

export type AppointmentStats = {
  total: number;
  byStatus: Record<string, number>;
};

export type AdminSummary = {
  users: {
    total: number;
    patients: number;
    doctors: number;
    pending_doctors?: number;
  };
  appointments: {
    total: number;
    completed_today?: number;
    completedToday?: number;
  };
  billing: {
    pending_invoices?: number;
    pendingInvoices?: number;
    pending_amount?: number;
    pendingAmount?: number;
    total_income?: number;
    totalIncome?: number;
  };
  generated_at?: string;
  generatedAt?: string;
};
