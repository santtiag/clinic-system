'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/auth-provider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import { LucideLock, LucideMail, LucideUser } from 'lucide-react';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const data = await apiFetch<{ access_token: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(formData),
      });
      login(data.access_token);
      toast.success('Bienvenido al Sistema Clínico');
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err.message || 'Credenciales incorrectas');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
      <Card className="w-full max-w-md shadow-xl border-none ring-1 ring-slate-200">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-sky-500 rounded-2xl shadow-lg shadow-sky-200">
              <LucideLock className="w-8 h-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">Iniciar Sesión</CardTitle>
          <CardDescription>
            Ingrese sus credenciales para acceder al portal clínico
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Usuario o Email</Label>
              <div className="relative">
                <LucideUser className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                <Input
                  id="username"
                  placeholder="admin_user"
                  className="pl-10"
                  required
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <div className="relative">
                <LucideLock className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  className="pl-10"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
            </div>
            <Button
              type="submit"
              className="w-full bg-sky-600 hover:bg-sky-700 text-white font-medium py-6 rounded-xl transition-all"
              disabled={isLoading}
            >
              {isLoading ? 'Autenticando...' : 'Acceder al Sistema'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col gap-4 justify-center text-center">
          <div className="text-sm text-slate-500">
            ¿No tienes cuenta?{' '}
            <Link href="/register" className="text-sky-600 font-semibold hover:underline">
              Regístrate como paciente
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
