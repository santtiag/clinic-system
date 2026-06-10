'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/providers/auth-provider';
import { Bell, Search, Menu, LayoutDashboard } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { USER_ROLES } from '@/lib/constants';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import SidebarNav from '@/components/layout/sidebar-nav';

export default function Topbar() {
  const { user, refreshUser } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (user && !user.name) {
      refreshUser();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  const displayName =
    user?.name || user?.username || (user ? `Usuario ${user.id.substring(0, 6)}` : 'Invitado');

  const initials = (() => {
    if (!user) return 'U';
    const source = user.name || user.username;
    if (source) {
      const parts = source.trim().split(/\s+/);
      const letters = parts.length > 1 ? parts[0][0] + parts[1][0] : source.substring(0, 2);
      return letters.toUpperCase();
    }
    return user.id.substring(0, 2).toUpperCase();
  })();

  return (
    <>
      <header className="h-16 border-b border-slate-200 bg-white px-4 sm:px-6 flex items-center justify-between gap-4 sticky top-0 z-10 shrink-0">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden text-slate-500 hover:bg-slate-50 shrink-0"
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Abrir menú de navegación"
          >
            <Menu className="w-5 h-5" />
          </Button>

          <div className="relative w-full max-w-md hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            <Input
              placeholder="Buscar paciente, cita o reporte..."
              className="pl-10 bg-slate-50 border-transparent focus:bg-white transition-all"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-4 shrink-0">
          <Button
            variant="ghost"
            size="icon"
            className="relative text-slate-500 hover:bg-slate-50"
            aria-label="Notificaciones"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full border-2 border-white" />
          </Button>

          <div className="flex items-center gap-3 pl-2 sm:pl-4 border-l border-slate-200">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold text-slate-900 line-clamp-1 max-w-[140px]">
                {user ? displayName : 'Invitado'}
              </p>
              <p className="text-xs text-slate-500">
                {user ? USER_ROLES[user.role] : 'Invitado'}
              </p>
            </div>
            <Avatar className="h-9 w-9 border border-slate-200 shrink-0">
              <AvatarImage src="" />
              <AvatarFallback className="bg-sky-100 text-sky-600 font-bold text-xs">
                {initials}
              </AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>

      <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
        <SheetContent side="left" className="w-72 p-0 flex flex-col">
          <SheetHeader className="p-6 border-b border-slate-100">
            <SheetTitle className="flex items-center gap-3">
              <div className="p-2 bg-sky-500 rounded-lg shadow-sm">
                <LayoutDashboard className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl tracking-tight text-slate-900">
                Clinico<span className="text-sky-500">OS</span>
              </span>
            </SheetTitle>
          </SheetHeader>
          <SidebarNav onNavigate={() => setMobileMenuOpen(false)} />
        </SheetContent>
      </Sheet>
    </>
  );
}
