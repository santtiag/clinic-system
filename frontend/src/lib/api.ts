import { getAuthToken } from '@/lib/auth';

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const FIELD_LABELS: Record<string, string> = {
  username: 'Nombre de usuario',
  email: 'Correo electrónico',
  password: 'Contraseña',
  dni: 'DNI',
  firstName: 'Nombre',
  lastName: 'Apellidos',
  dateOfBirth: 'Fecha de nacimiento',
};

function parseApiError(body: unknown): string {
  if (!body || typeof body !== 'object') {
    return 'Error en la solicitud';
  }

  const { detail, message } = body as { detail?: unknown; message?: string };

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item || typeof item !== 'object' || !('msg' in item)) return null;
        const field = Array.isArray(item.loc) ? String(item.loc.at(-1) ?? '') : '';
        const label = FIELD_LABELS[field] ?? field;
        return label ? `${label}: ${item.msg}` : String(item.msg);
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join('. ');
    }
  }

  return message || 'Error en la solicitud';
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers);

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (!options.body && !headers.has('Content-Type')) {
    // No content type for GET
  } else if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('clinico_token');
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(parseApiError(error));
  }

  if (response.status === 204) return {} as T;

  return response.json();
}

/** Downloads a file from an authenticated endpoint and triggers a browser save. */
export async function apiDownload(endpoint: string, fallbackFilename = 'download'): Promise<void> {
  const token = getAuthToken();
  const headers = new Headers();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${endpoint}`, { headers });

  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('clinico_token');
      window.location.href = '/login';
    }
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(parseApiError(error));
  }

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition');
  let filename = fallbackFilename;
  if (disposition) {
    const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (match?.[1]) {
      filename = match[1].replace(/['"]/g, '');
    }
  }

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
