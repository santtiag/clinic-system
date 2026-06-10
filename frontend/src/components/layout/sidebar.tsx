'use client';

import { LayoutDashboard } from 'lucide-react';
import SidebarNav from '@/components/layout/sidebar-nav';

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex w-64 h-screen sticky top-0 shrink-0 bg-white border-r border-slate-200 flex-col">
      <div className="p-6 flex items-center gap-3">
        <div className="p-2 bg-sky-500 rounded-lg shadow-sm">
          <LayoutDashboard className="w-5 h-5 text-white" />
        </div>
        <span className="font-bold text-xl tracking-tight text-slate-900">
          Clinico<span className="text-sky-500">OS</span>
        </span>
      </div>
      <SidebarNav />
    </aside>
  );
}
