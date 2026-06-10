'use client';

import { Button } from '@/components/ui/button';
import { ShieldAlert } from 'lucide-react';
import Link from 'next/link';

export default function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
      <div className="text-center max-w-md space-y-6 p-12 bg-white rounded-3xl shadow-xl ring-1 ring-slate-200">
        <div className="flex justify-center">
          <div className="p-4 bg-rose-100 rounded-full">
            <ShieldAlert className="w-12 h-12 text-rose-600" />
          </div>
        </div>
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-slate-900">Acceso Restringido</h1>
          <p className="text-slate-500">
            Lo sentimos, no tienes los permisos necesarios para acceder a esta sección del sistema.
          </p>
        </div>
        <Link href="/dashboard">
          <Button className="w-full bg-sky-600 hover:bg-sky-700 text-white rounded-xl py-6">
            Volver al Inicio
          </Button>
        </Link>
      </div>
    </div>
  );
}
