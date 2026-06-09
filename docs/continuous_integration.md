Voy a armarte la guía completa de Gitflow paso a paso. La división de features entre Santiago y Eliel se alinea con las tareas y responsables del backlog: Santiago cubre Infraestructura, Identity, Scheduling y Reporting/Admin [4][5][6][8], mientras que Eliel cubre Medical Record, Billing y Workers [6][7].

---

## PARTE 1: SANTIAGO — SETUP INICIAL DEL REPOSITORIO Y GITFLOW

Desde la terminal, dentro de la carpeta `sistema-clinico` (sin `.git`):

### Paso 1.1: Inicializar repositorio local
```bash
cd sistema-clinico
git init
```

### Paso 1.2: Configurar identidad de Santiago
```bash
git config user.name "santtiag"
git config user.email "santiago@clinica.dev"
```

### Paso 1.3: Crear `.gitignore` base
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv/
venv/

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Docker / Infra
*.log
postgres_data/
redis_data/
rabbitmq_data/
grafana_data/
prometheus_data/

# Build
dist/
build/
EOF
```

### Paso 1.4: Preparar commit inicial estructural
Crea un `README.md` mínimo para poder subir `main`:
```bash
echo "# Clinic System" > README.md
git add README.md .gitignore
git commit -m "chore: initial repository setup with .gitignore"
```

### Paso 1.5: Conectar con GitHub y subir `main`
```bash
git remote add origin https://github.com/santtiag/clinic-system.git
git branch -M main
git push -u origin main
```

### Paso 1.6: Crear y subir rama `develop` (trunk de integración)
```bash
git checkout -b develop
git push -u origin develop
```

### Paso 1.7: Añadir a Eliel como colaborador (desde GitHub web)
1. Abre https://github.com/santtiag/clinic-system/settings/access
2. Click en **Invite a collaborator**
3. Busca `RamosEliel` y envía invitación.
4. Eliel debe aceptar el email/invitación de GitHub.

### Paso 1.8: Configurar `develop` como rama por defecto (opcional pero recomendado)
En GitHub web: Settings → Branches → Default branch → `develop`.

---

## PARTE 2: SANTIAGO — SUBIR SUS FEATURES

### 🔹 Feature 1: Infraestructura base, Kong, Docker y Monitoreo

```bash
git checkout develop
git checkout -b feature/infra-monitoring
```

Añade solo la infraestructura base:
```bash
git add docker-compose.yml
git add Kong/
git add scripts/
git add monitoring/
git commit -m "feat(infra): add docker-compose, kong gateway and monitoring stack

- Kong declarative config for 6 microservices
- Prometheus, Grafana, Loki, Jaeger setup
- PostgreSQL init script for multi-tenant DBs"
```

Sube la rama y mergea a `develop`:
```bash
git push -u origin feature/infra-monitoring
git checkout develop
git merge feature/infra-monitoring --no-ff -m "merge: infrastructure and monitoring stack"
git push origin develop
```

### 🔹 Feature 2: Identity Service (Gestión de Identidad y Acceso)

```bash
git checkout develop
git checkout -b feature/identity-service
git add services/identity-service/
git commit -m "feat(identity): implement identity service with JWT and DDD layers

- Domain-driven design: domain, application, infrastructure, presentation
- User registration, secure login, role-based access control
- Async SQLAlchemy with PostgreSQL (identity_db)
- RabbitMQ event publishing support"
```

```bash
git push -u origin feature/identity-service
git checkout develop
git merge feature/identity-service --no-ff -m "merge: identity service (HU-GIA-01/02) [4]"
git push origin develop
```

### 🔹 Feature 3: Scheduling Service (Agendamiento completo)

```bash
git checkout develop
git checkout -b feature/scheduling-service
git add services/scheduling-service/
git commit -m "feat(scheduling): implement appointment scheduling and management

- Search availability by specialty and doctor [5]
- Book appointments with slot locking
- Cancel and reschedule with 24h validation [6]
- Doctor status workflow: programada → confirmada → en_atencion → completada
- RabbitMQ events for async notifications"
```

```bash
git push -u origin feature/scheduling-service
git checkout develop
git merge feature/scheduling-service --no-ff -m "merge: scheduling service (HU-AGC-01/02/03/05) [5][6]"
git push origin develop
```

### 🔹 Feature 4: Reporting, Admin Panel y Métricas Prometheus

```bash
git checkout develop
git checkout -b feature/reporting-admin-prometheus
git add services/reporting-service/
git add services/admin-panel/
git add workers/notification-worker/
git add workers/audit-worker/
```

**Nota:** Aquí incluimos los `requirements.txt` actualizados de todos los servicios que ahora tienen `prometheus-fastapi-instrumentator`:
```bash
git add services/*/requirements.txt
git add services/*/src/main.py
```

Commit:
```bash
git commit -m "feat(reporting): add reporting service, admin panel and prometheus metrics

- Income reports with doctor/period filters [8]
- Appointment statistics aggregation
- Admin dashboard consolidating operational KPIs
- CSV export base (prepared for PDF/Excel) [8]
- Prometheus /metrics endpoint on all FastAPI services"
```

```bash
git push -u origin feature/reporting-admin-prometheus
git checkout develop
git merge feature/reporting-admin-prometheus --no-ff -m "merge: reporting, admin panel and observability [8]"
git push origin develop
```

---

## PARTE 3: ELIEL — CLONAR Y SUBIR SUS FEATURES

Eliel, desde tu computadora (después de aceptar la invitación en GitHub):

### Paso 3.1: Clonar y posicionarse en `develop`
```bash
git clone https://github.com/santtiag/clinic-system.git
cd clinic-system
git checkout develop
git config user.name "RamosEliel"
git config user.email "eliel@clinica.dev"
```

### 🔹 Feature 5: Medical Record Service (Historia Clínica)

```bash
git checkout -b feature/medical-record-service
git add services/medical-record-service/
git commit -m "feat(medical): implement electronic health record service

- Medical records per patient with evolution notes [6]
- Doctor-only write access, patient read access
- Own PostgreSQL database (medical_db) respecting DDD boundaries [3]
- Async SQLAlchemy with repository pattern"
```

```bash
git push -u origin feature/medical-record-service
git checkout develop
git merge feature/medical-record-service --no-ff -m "merge: medical record service (HU-HCE-02) [6]"
git push origin develop
```

### 🔹 Feature 6: Billing Service (Facturación y Pagos)

```bash
git checkout develop
git checkout -b feature/billing-service
git add services/billing-service/
git commit -m "feat(billing): implement billing service with automatic invoicing

- Auto-generate invoices on appointment completion via RabbitMQ [7]
- Payment processing with status management [7]
- Refund workflow (reembolsos)
- Own PostgreSQL database (billing_db) [3]
- RabbitMQ consumer for appointments.status_updated events"
```

```bash
git push -u origin feature/billing-service
git checkout develop
git merge feature/billing-service --no-ff -m "merge: billing service (HU-FAP-01/02/03) [7]"
git push origin develop
```

### 🔹 Feature 7: Background Workers (Notification + Audit)

```bash
git checkout develop
git checkout -b feature/workers
git add workers/notification-worker/
git add workers/audit-worker/
git commit -m "feat(workers): add notification and audit workers

- Notification Worker: consumes appointments events (cancelled, rescheduled, completed)
- Audit Worker: persists domain events to audit_db for traceability
- RabbitMQ topic exchange binding with durable queues"
```

```bash
git push -u origin feature/workers
git checkout develop
git merge feature/workers --no-ff -m "merge: notification and audit workers"
git push origin develop
```

---

## PARTE 4: RELEASE A PRODUCCIÓN (MAIN + TAG)

Cuando ambos validan que `develop` está estable:

### Paso 4.1: Crear rama release
```bash
git checkout develop
git checkout -b release/v1.0.0
git push -u origin release/v1.0.0
```

### Paso 4.2: Merge a `main` con tag
```bash
git checkout main
git merge release/v1.0.0 --no-ff -m "release: clinic system v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0 - Core microservices complete"
git push origin main
git push origin --tags
```

---

## PARTE 5: RESUMEN DE COMANDOS POR DESARROLLADOR

### Santiago (Owner) — Cheat Sheet
```bash
# Setup
git init
git remote add origin https://github.com/santtiag/clinic-system.git
git add README.md .gitignore
git commit -m "chore: initial setup"
git push -u origin main
git checkout -b develop && git push -u origin develop

# Feature loop (repetir por cada feature)
git checkout develop
git checkout -b feature/NOMBRE
git add <archivos-correspondientes>
git commit -m "feat(área): descripción"
git push -u origin feature/NOMBRE
git checkout develop
git merge feature/NOMBRE --no-ff -m "merge: descripción"
git push origin develop
```

### Eliel (Collaborator) — Cheat Sheet
```bash
# Clonar una vez
git clone https://github.com/santtiag/clinic-system.git
cd clinic-system
git config user.name "RamosEliel"
git config user.email "eliel@clinica.dev"

# Feature loop (repetir por cada feature)
git checkout develop
git checkout -b feature/NOMBRE
git add <archivos-correspondientes>
git commit -m "feat(área): descripción"
git push -u origin feature/NOMBRE
git checkout develop
git merge feature/NOMBRE --no-ff -m "merge: descripción"
git push origin develop
```

---

## VERIFICACIÓN FINAL DEL WORKFLOW

1. **Ramas en GitHub**: Deben existir `main`, `develop`, y las 7 `feature/*` (opcionalmente borrarlas tras merge).
2. **Commits en develop**: Uno por feature merge (`--no-ff`), manteniendo historia legible.
3. **Tag**: `v1.0.0` apuntando al último commit de `main`.
4. **Colaborador**: `RamosEliel` debe aparecer en Settings → Manage access.

```bash
# Verificar estado local de Santiago
git log --oneline --graph --all --decorate

# Verificar en GitHub
open https://github.com/santtiag/clinic-system/branches
```
