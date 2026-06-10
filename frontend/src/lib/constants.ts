import { Role } from '@/types';

export const SPECIALTIES = [
  'Cardiología',
  'Dermatología',
  'Medicina General',
  'Pediatría',
];

export const APPOINTMENT_STATUSES = {
  programada: { label: 'Programada', color: 'bg-sky-100 text-sky-700 border-sky-200' },
  confirmada: { label: 'Confirmada', color: 'bg-indigo-100 text-indigo-700 border-indigo-200' },
  en_atencion: { label: 'En Atención', color: 'bg-amber-100 text-amber-700 border-amber-200' },
  completada: { label: 'Completada', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  cancelacion_solicitada: { label: 'Cancelación Solicitada', color: 'bg-orange-100 text-orange-700 border-orange-200' },
  cancelada: { label: 'Cancelada', color: 'bg-rose-100 text-rose-700 border-rose-200' },
};

export const USER_ROLES = {
  [Role.PATIENT]: 'Paciente',
  [Role.DOCTOR]: 'Médico',
  [Role.ADMIN]: 'Administrador',
  [Role.STAFF]: 'Personal Administrativo',
};

export const ROLE_HOME: Record<Role, string> = {
  [Role.PATIENT]: '/dashboard',
  [Role.DOCTOR]: '/dashboard',
  [Role.STAFF]: '/dashboard',
  [Role.ADMIN]: '/dashboard',
};

export const ROLE_QUICK_ACTIONS: Record<Role, { label: string; href: string }[]> = {
  [Role.PATIENT]: [
    { label: 'Agendar Cita', href: '/appointments/new' },
    { label: 'Mi Historia', href: '/medical-records/me' },
    { label: 'Mis Facturas', href: '/billing/my-invoices' },
  ],
  [Role.DOCTOR]: [
    { label: 'Agenda del Día', href: '/appointments' },
    { label: 'Historias Clínicas', href: '/medical-records' },
    { label: 'Reportes', href: '/reports' },
  ],
  [Role.STAFF]: [
    { label: 'Gestionar Citas', href: '/appointments' },
    { label: 'Caja / Cobros', href: '/billing/checkout' },
    { label: 'Facturación', href: '/billing' },
  ],
  [Role.ADMIN]: [
    { label: 'Usuarios', href: '/admin/users' },
    { label: 'Auditoría', href: '/admin/audit' },
    { label: 'Reportes', href: '/reports' },
  ],
};
