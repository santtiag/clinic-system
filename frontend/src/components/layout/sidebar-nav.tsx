'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';
import { Role } from '@/types';
import {
  LayoutDashboard,
  CalendarDays,
  FileText,
  CreditCard,
  BarChart3,
  ShieldCheck,
  LogOut,
  Users,
  ClipboardList,
  Wallet,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

const MENU_ITEMS = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    href: '/dashboard',
    roles: [Role.PATIENT, Role.DOCTOR, Role.STAFF, Role.ADMIN],
  },
  {
    id: 'appointments',
    label: 'Citas',
    icon: CalendarDays,
    href: '/appointments',
    roles: [Role.PATIENT, Role.DOCTOR, Role.STAFF, Role.ADMIN],
  },
  {
    id: 'medical-records',
    label: 'Historias Clínicas',
    icon: FileText,
    href: '/medical-records',
    roles: [Role.DOCTOR, Role.ADMIN],
  },
  {
    id: 'my-record',
    label: 'Mi Historia',
    icon: FileText,
    href: '/medical-records/me',
    roles: [Role.PATIENT],
  },
  {
    id: 'billing',
    label: 'Facturación',
    icon: CreditCard,
    href: '/billing',
    roles: [Role.STAFF, Role.ADMIN],
  },
  {
    id: 'checkout',
    label: 'Caja',
    icon: Wallet,
    href: '/billing/checkout',
    roles: [Role.STAFF, Role.ADMIN],
  },
  {
    id: 'my-invoices',
    label: 'Mis Facturas',
    icon: CreditCard,
    href: '/billing/my-invoices',
    roles: [Role.PATIENT],
  },
  {
    id: 'reports',
    label: 'Reportes',
    icon: BarChart3,
    href: '/reports',
    roles: [Role.DOCTOR, Role.STAFF, Role.ADMIN],
  },
  {
    id: 'admin-users',
    label: 'Usuarios',
    icon: Users,
    href: '/admin/users',
    roles: [Role.ADMIN],
  },
  {
    id: 'admin-audit',
    label: 'Auditoría',
    icon: ClipboardList,
    href: '/admin/audit',
    roles: [Role.ADMIN],
  },
  {
    id: 'admin',
    label: 'Panel Admin',
    icon: ShieldCheck,
    href: '/admin',
    roles: [Role.ADMIN],
  },
];

interface SidebarNavProps {
  onNavigate?: () => void;
}

export default function SidebarNav({ onNavigate }: SidebarNavProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  if (!user) return null;

  const filteredMenu = MENU_ITEMS.filter((item) =>
    item.roles.includes(user.role as Role)
  );

  return (
    <>
      <nav className="flex-1 px-4 space-y-1">
        {filteredMenu.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.id}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group',
                isActive
                  ? 'bg-sky-50 text-sky-600 font-medium'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
              )}
            >
              <item.icon
                className={cn(
                  'w-5 h-5 shrink-0 transition-colors',
                  isActive
                    ? 'text-sky-600'
                    : 'text-slate-400 group-hover:text-slate-600'
                )}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-100">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg h-11"
          onClick={() => {
            onNavigate?.();
            logout();
          }}
        >
          <LogOut className="w-5 h-5" />
          Cerrar Sesión
        </Button>
      </div>
    </>
  );
}
