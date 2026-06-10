import { User, Role } from '@/types';

export const getAuthToken = () => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('clinico_token');
};

export const setAuthToken = (token: string) => {
  localStorage.setItem('clinico_token', token);
};

export const clearAuthToken = () => {
  localStorage.removeItem('clinico_token');
};

export function decodeToken(
  token: string
): { sub: string; role: Role; name?: string; username?: string } | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16).toUpperCase()).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}
