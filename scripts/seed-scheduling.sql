-- Seed médicos y horarios de disponibilidad para agendamiento de citas.
-- Ejecutar: PGPASSWORD=clinico_secret psql -h localhost -p 5433 -U clinico -d scheduling_db -f scripts/seed-scheduling.sql

-- Médico vinculado a usuario identity (Santiago Soto - Dermatología)
INSERT INTO doctors (id, user_id, full_name, specialty)
SELECT
  'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::uuid,
  'dacd6ee1-c64b-46ed-a8c7-c28f3b73357e'::uuid,
  'Santiago Soto Villegas',
  'Dermatología'::specialty_enum
WHERE NOT EXISTS (
  SELECT 1 FROM doctors WHERE user_id = 'dacd6ee1-c64b-46ed-a8c7-c28f3b73357e'::uuid
);

-- NOTA: A partir de la sincronización por eventos (doctor.registered), los médicos
-- reales se crean automáticamente en scheduling con el user_id de su cuenta de
-- identity. Los siguientes registros demo usan user_id aleatorios y NO tienen una
-- cuenta de identity asociada (no podrán iniciar sesión ni ver "sus" citas). Útiles
-- solo para poblar disponibilidad de prueba. Para médicos que inicien sesión, créalos
-- vía /auth/register/doctor o /auth/users (rol doctor) y deja que el evento los sincronice.

-- Médicos demo para otras especialidades
INSERT INTO doctors (id, user_id, full_name, specialty)
SELECT gen_random_uuid(), gen_random_uuid(), 'Dr. Ana Cardio', 'Cardiología'::specialty_enum
WHERE NOT EXISTS (SELECT 1 FROM doctors WHERE full_name = 'Dr. Ana Cardio');

INSERT INTO doctors (id, user_id, full_name, specialty)
SELECT gen_random_uuid(), gen_random_uuid(), 'Dr. Luis General', 'Medicina General'::specialty_enum
WHERE NOT EXISTS (SELECT 1 FROM doctors WHERE full_name = 'Dr. Luis General');

INSERT INTO doctors (id, user_id, full_name, specialty)
SELECT gen_random_uuid(), gen_random_uuid(), 'Dra. María Pediatría', 'Pediatría'::specialty_enum
WHERE NOT EXISTS (SELECT 1 FROM doctors WHERE full_name = 'Dra. María Pediatría');

-- Horarios: próximos 14 días, 9:00-17:00 cada hora, solo días laborables
INSERT INTO availability_slots (id, doctor_id, start_time, end_time, is_available)
SELECT
  gen_random_uuid(),
  d.id,
  (CURRENT_DATE + day_offset + time '09:00:00' + (hour_offset || ' hours')::interval),
  (CURRENT_DATE + day_offset + time '09:00:00' + ((hour_offset + 1) || ' hours')::interval),
  true
FROM doctors d
CROSS JOIN generate_series(0, 13) AS day_offset
CROSS JOIN generate_series(0, 7) AS hour_offset
WHERE EXTRACT(DOW FROM CURRENT_DATE + day_offset) BETWEEN 1 AND 5
  AND NOT EXISTS (
    SELECT 1 FROM availability_slots s
    WHERE s.doctor_id = d.id
      AND s.start_time >= CURRENT_DATE
  );
