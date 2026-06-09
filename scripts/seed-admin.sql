-- Crea el usuario administrador inicial para poder gestionar el resto de roles.
-- Ejecutar DESPUES de que identity-service haya creado las tablas (init_db):
--   PGPASSWORD=clinico_secret psql -h localhost -p 5432 -U clinico -d identity_db -f scripts/seed-admin.sql
--
-- Credenciales por defecto:
--   usuario:    admin
--   contraseña: Admin1234
-- Cambiar la contraseña tras el primer inicio de sesión.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO users (
  id, username, email, hashed_password, role, dni,
  first_name, last_name, date_of_birth, is_active, created_at, updated_at
)
SELECT
  gen_random_uuid(),
  'admin',
  'admin@clinico.local',
  crypt('Admin1234', gen_salt('bf', 12)),
  'ADMIN'::role_enum,
  '10000000',
  'Administrador',
  'General',
  '1990-01-01'::date,
  true,
  now(),
  now()
WHERE NOT EXISTS (
  SELECT 1 FROM users WHERE username = 'admin'
);
