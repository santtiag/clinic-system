# Sistema Clinico - Contexto para Claude

## Vision General

Sistema de gestion clinica basado en microservicios con FastAPI, Next.js, Domain-Driven Design (DDD) y practicas de Extreme Programming (XP). Gestiona identidad de usuarios, agendamiento de citas, historias clinicas electronicas, facturacion y reportes.

## Arquitectura

```
                                    Kong API Gateway (8000)
                                           |
    +------------------+-------------------+---------------+---------------+
    |                  |                   |               |               |
Identity(8001)  Scheduling(8002)  Medical(8003)  Billing(8004)  Reporting(8005)
    |                  |                   |               |               |
    +------------------+-------------------+---------------+---------------+
                                           |
                                     PostgreSQL (5432)
                                     RabbitMQ (5672/15672)
                                     Redis (6379)
```

### Componentes Principales

| Componente | Puerto | Descripcion |
|------------|--------|-------------|
| Kong API Gateway | 8000/8443 | Proxy, rate limiting, routing, CORS |
| Identity Service | 8001 | Autenticacion JWT, registro, perfiles |
| Scheduling Service | 8002 | Citas, disponibilidad, estados |
| Medical Record Service | 8003 | Historias clinicas, prescripciones, adjuntos |
| Billing Service | 8004 | Recibos, pagos, reembolsos |
| Reporting Service | 8005 | Reportes financieros, estadisticas de demanda |
| Admin Panel | 8006 | Dashboard administrativo |
| Frontend Next.js | 3001 | Interfaz de usuario |
| RabbitMQ | 5672/15672 | Mensajeria entre servicios |
| PostgreSQL | 5432 | Base de datos (una por servicio) |
| Redis | 6379 | Cache y rate limiting |
| Prometheus | 9090 | Metricas |
| Grafana | 3000 | Dashboards (admin/admin) |
| Loki | 3100 | Logs centralizados |
| Jaeger | 16686 | Distributed tracing |

## Estructura de Directorios

```
sistema-clinico/
├── common/                    # Codigo compartido entre servicios
│   ├── config.py              # Variables de entorno y settings
│   ├── database.py            # Conexion async PostgreSQL con SQLAlchemy
│   ├── security.py            # JWT, password hashing
│   ├── logging.py             # Logging estructurado con trace IDs
│   ├── messaging.py           # RabbitMQ publisher/consumer
│   ├── schemas.py             # Schemas Pydantic compartidos
│   └── exceptions.py          # Excepciones de aplicacion
├── services/
│   ├── identity-service/      # Registro, login, perfiles, roles
│   ├── scheduling-service/    # Citas, disponibilidad, calendario
│   ├── medical-record-service/ # Historia clinica, prescripciones, adjuntos
│   ├── billing-service/       # Facturacion, pagos, recibos
│   ├── reporting-service/     # Reportes, estadisticas, exportacion
│   └── admin-panel/           # Dashboard y administracion
├── workers/
│   ├── notification-worker/   # Procesa eventos y envia notificaciones
│   └── audit-worker/          # Registra logs de auditoria
├── frontend/                  # Next.js 14+ App Router
│   ├── src/app/               # Paginas (login, registro, panel, etc.)
│   ├── src/components/        # Componentes React
│   └── src/lib/api.ts         # Cliente API
├── Kong/
│   └── kong.yml               # Configuracion de rutas y plugins
├── monitoring/
│   ├── grafana/               # Dashboards y datasources
│   ├── loki/                  # Configuracion de logs
│   └── prometheus.yml         # Targets de scraping
├── scripts/
│   └── init-db.sql            # Creacion de bases de datos
├── documents/                 # Backlog, historias de usuario
├── docs/                      # Documentacion tecnica y guias
└── docker-compose.yml         # Orquestacion completa
```

## Estructura de un Microservicio

Cada servicio sigue esta estructura interna:

```
service-name/
├── src/
│   ├── domain/                # Entidades, servicios de dominio, repositorios
│   ├── infrastructure/        # Implementaciones de repositorios, clientes HTTP
│   ├── presentation/            # Routers FastAPI, schemas Pydantic
│   │   └── routers/
│   └── main.py                # Punto de entrada FastAPI
├── tests/
├── Dockerfile
├── requirements.txt
└── ...
```

## Convenciones

### Commits
- Seguir **Conventional Commits**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`
- Formato: `tipo(alcance): descripcion breve`
- Incluir `Resolves: T-NN` en el cuerpo para vincular tareas
- Push directo a `main` esta permitido, pero se recomienda trabajar en ramas `feature/` y mergear explicitamente

### Ramas (GitHub Flow)
- `main`: codigo estable. Es la unica rama permanente.
- `feature/sprint-N/T-NN-descripcion`: una rama por tarea, creada desde `main` y mergeada de vuelta a `main`
- No existe rama `develop`. No existen ramas `release/`.
- Tags en `main` al finalizar cada sprint: `sprint-N`

### Codigo Python
- FastAPI con SQLAlchemy async
- Pydantic v2 para validacion
- Inyeccion de dependencias via `Depends()`
- UUID para IDs de entidades
- enums para estados y roles

### Codigo TypeScript / Next.js
- App Router (no pages router)
- Tailwind CSS para estilos
- React Query para estado de servidor
- Componentes en `src/components/`

## Como Ejecutar

### Prerrequisitos
- Docker y Docker Compose
- Git

### Iniciar todos los servicios

```bash
docker-compose up -d
```

### Verificar estado

```bash
docker-compose ps

# Health checks
curl http://localhost:8001/health  # Identity
curl http://localhost:8002/health  # Scheduling
curl http://localhost:8003/health  # Medical Record
curl http://localhost:8004/health  # Billing
curl http://localhost:8005/health  # Reporting
curl http://localhost:8006/health  # Admin Panel
```

### Ver logs

```bash
docker-compose logs -f identity-service
docker-compose logs -f scheduling-service
```

### Reiniciar un servicio

```bash
docker-compose restart identity-service
```

## Tecnologias

| Capa | Tecnologia |
|------|------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| Frontend | Next.js 14+, React 18, TypeScript, Tailwind CSS |
| Base de Datos | PostgreSQL 15, asyncpg |
| Cache | Redis 7 |
| Mensajeria | RabbitMQ 3.12, aio-pika |
| API Gateway | Kong 3.4 |
| Monitoreo | Prometheus, Grafana 10, Loki 2.8, Jaeger 1.47 |
| Contenedores | Docker, Docker Compose |
| Testing | pytest, pytest-asyncio |

## Bounded Contexts

| Contexto | Servicio | Historias de Usuario |
|----------|----------|---------------------|
| Gestion de Identidad y Acceso | Identity Service | HU-GIA-01, HU-GIA-02, HU-GIA-03 |
| Agendamiento de Citas | Scheduling Service | HU-AGC-01 a HU-AGC-05 |
| Historia Clinica Electronica | Medical Record Service | HU-HCE-01 a HU-HCE-04 |
| Facturacion y Pagos | Billing Service | HU-FAP-01 a HU-FAP-03 |
| Reportes Medicos | Reporting Service | HU-RPM-01, HU-RPM-02 |
| Notificaciones | Notification Worker | HU-AGC-04 |
| Auditoria | Audit Worker | HU-GIA-03 |

## Repositorio Remoto

- **URL:** `https://github.com/santtiag/clinic-system`
- **Propietario:** Santiago Romero (`santtiag`)
- **Colaborador:** Eliel Berrio (`RamosEliel`)
- **Visibilidad:** Publico
- **Flujo:** GitHub Flow (`main` + `feature/*` branches)

## Desarrolladores

- **Santiago Romero** - GitHub: `santtiag`
- **Eliel Berrio** - GitHub: `RamosEliel`

## Metodologia

- **Arquitectura**: Domain-Driven Design (DDD) con microservicios
- **Desarrollo**: Extreme Programming (XP), integracion continua
- **Comunicacion**: REST sincrono + RabbitMQ asincrono
- **Patrones**: Repository, Service Layer, middleware de logging/metricas

## Flujo de Trabajo Git

Para instrucciones completas paso a paso, ver `docs/GIT_WORKFLOW.md`. Incluye:
- Setup inicial para Santiago (crear repo, invitar colaborador)
- Setup inicial para Eliel (clonar, configurar)
- Flujo por tarea: crear rama, commitear, subir, mergear a main
- Convenciones de commits y nomenclatura de ramas
- Resolucion de conflictos
- Comandos de emergencia y cheatsheet
