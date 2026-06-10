CREATE DATABASE identity_db;
CREATE DATABASE scheduling_db;
CREATE DATABASE medical_db;
CREATE DATABASE billing_db;
CREATE DATABASE reporting_db;
CREATE DATABASE audit_db;

-- scheduling_db: nuevo estado de cancelación solicitada
\c scheduling_db;
ALTER TYPE appointment_status_enum ADD VALUE IF NOT EXISTS 'cancelacion_solicitada';
