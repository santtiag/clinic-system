'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { apiFetch } from '@/lib/api';
import { LucideUserPlus, LucideMail, LucideCalendar, LucideFingerprint, Stethoscope } from 'lucide-react';
import Link from 'next/link';
import { SPECIALTIES } from '@/lib/constants';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [accountType, setAccountType] = useState<'patient' | 'doctor'>('patient');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    dni: '',
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    specialty: SPECIALTIES[2],
    licenseNumber: '',
  });

  const validateForm = (): string | null => {
    if (formData.username.length < 3) return 'El nombre de usuario debe tener al menos 3 caracteres';
    if (formData.password.length < 8) return 'La contraseña debe tener al menos 8 caracteres';
    if (!/^\d{7,8}$/.test(formData.dni)) return 'El DNI debe tener 7 u 8 dígitos numéricos';
    if (!formData.dateOfBirth) return 'La fecha de nacimiento es obligatoria';
    if (accountType === 'doctor' && !formData.licenseNumber) return 'El número de colegiatura es obligatorio';
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validationError = validateForm();
    if (validationError) {
      toast.error(validationError);
      return;
    }

    setIsLoading(true);
    try {
      const endpoint = accountType === 'doctor' ? '/auth/register/doctor' : '/auth/register/patient';
      await apiFetch(endpoint, { method: 'POST', body: JSON.stringify(formData) });
      toast.success(
        accountType === 'doctor'
          ? 'Registro enviado. Un administrador validará tu cuenta.'
          : 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.'
      );
      router.push('/login');
    } catch (err: any) {
      toast.error(err.message || 'Error al registrar');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
      <Card className="w-full max-w-2xl shadow-xl border-none ring-1 ring-slate-200">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-emerald-500 rounded-2xl shadow-lg shadow-emerald-200">
              {accountType === 'doctor' ? <Stethoscope className="w-8 h-8 text-white" /> : <LucideUserPlus className="w-8 h-8 text-white" />}
            </div>
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">Registro</CardTitle>
          <CardDescription>Cree su cuenta según su rol en la clínica</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={accountType} onValueChange={(v) => setAccountType(v as 'patient' | 'doctor')} className="mb-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="patient">Paciente</TabsTrigger>
              <TabsTrigger value="doctor">Médico</TabsTrigger>
            </TabsList>
          </Tabs>

          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Nombre de Usuario</Label>
                <Input id="username" required value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Correo Electrónico</Label>
                <Input id="email" type="email" required value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input id="password" type="password" minLength={8} required value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dni">DNI / Cédula</Label>
                <Input id="dni" pattern="\d{7,8}" required value={formData.dni} onChange={(e) => setFormData({ ...formData, dni: e.target.value })} />
              </div>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">Nombre(s)</Label>
                <Input id="firstName" required value={formData.firstName} onChange={(e) => setFormData({ ...formData, firstName: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Apellidos</Label>
                <Input id="lastName" required value={formData.lastName} onChange={(e) => setFormData({ ...formData, lastName: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dateOfBirth">Fecha de Nacimiento</Label>
                <Input id="dateOfBirth" type="date" required value={formData.dateOfBirth} onChange={(e) => setFormData({ ...formData, dateOfBirth: e.target.value })} />
              </div>
              {accountType === 'doctor' && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="specialty">Especialidad</Label>
                    <select
                      id="specialty"
                      className="w-full h-10 px-3 rounded-md border border-slate-200"
                      value={formData.specialty}
                      onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                    >
                      {SPECIALTIES.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="licenseNumber">Número de Colegiatura</Label>
                    <Input id="licenseNumber" required value={formData.licenseNumber} onChange={(e) => setFormData({ ...formData, licenseNumber: e.target.value })} />
                  </div>
                </>
              )}
              <div className="flex items-end justify-end pt-4">
                <Button type="submit" className="w-full md:w-auto bg-emerald-600 hover:bg-emerald-700 text-white py-6 px-8 rounded-xl" disabled={isLoading}>
                  {isLoading ? 'Registrando...' : 'Crear Cuenta'}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col gap-4 justify-center text-center">
          <div className="text-sm text-slate-500">
            ¿Ya tienes cuenta?{' '}
            <Link href="/login" className="text-sky-600 font-semibold hover:underline">Inicia sesión aquí</Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
