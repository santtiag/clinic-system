# Pruebas Unitarias de Microservicios

Documentación de las pruebas unitarias implementadas para los 6 microservicios backend del Sistema Clínico (excluyendo el frontend).

**Fecha de ejecución:** 7 de junio de 2026  
**Resultado global:** 12/12 pruebas exitosas (100%)  
**Framework:** pytest 7.4+ con pytest-asyncio  
**Estrategia:** pruebas aisladas con mocks (`AsyncMock`, `MagicMock`, `SimpleNamespace`) — sin PostgreSQL, RabbitMQ ni datos reales.

---

## Resumen ejecutivo

| Microservicio | Pruebas | Resultado |
|---------------|---------|-----------|
| identity-service | 2 | 2/2 PASSED |
| scheduling-service | 2 | 2/2 PASSED |
| billing-service | 2 | 2/2 PASSED |
| medical-record-service | 2 | 2/2 PASSED |
| reporting-service | 2 | 2/2 PASSED |
| admin-panel | 2 | 2/2 PASSED |
| **Total** | **12** | **100%** |

### Advertencias observadas (no fallos)

Durante la ejecución aparecieron **warnings** de deprecación en código de producción, no en las pruebas:

- `datetime.datetime.utcnow()` en `admin-panel/src/application/services.py` (líneas 27 y 63). Python recomienda usar `datetime.now(datetime.UTC)` en su lugar.
- En `admin-panel`, el manejo de errores usa bloques `try/except Exception` genéricos que silencian fallos de servicios externos y devuelven `None` en los campos afectados. Las pruebas validan explícitamente este comportamiento.

Estas advertencias **no impidieron** que las pruebas pasaran; son deuda técnica a corregir en el código de producción.

---

## Infraestructura de testing

Cada microservicio incluye:

```
services/<servicio>/
├── pytest.ini              # asyncio_mode = auto, pythonpath = .
├── requirements-dev.txt    # pytest, pytest-asyncio
└── tests/
    ├── __init__.py
    └── test_services.py
```

**Ejecución individual:**

```bash
cd services/identity-service
pip install -r requirements-dev.txt
pytest -v
```

**Ejecución de todos los servicios:**

```bash
./scripts/run-tests.sh
```

---

## 1. Identity Service

**Archivo:** `services/identity-service/tests/test_services.py`  
**Capa probada:** `AuthService` y utilidades de seguridad (`hash_password`, `verify_password`).

### 1.1 `test_register_patient_conflict_username`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Verificar que el registro de paciente rechaza usernames duplicados antes de crear el usuario en base de datos. |
| **Qué valida** | Regla de negocio: no se puede registrar un paciente si el username ya existe. |
| **Cómo se hizo** | Se instancia `AuthService` con un repositorio mockeado (`AsyncMock`). `get_by_username` devuelve un usuario existente. Se envía un `PatientRegister` válido y se espera `HTTPException` con código **409** y mensaje `"Username already exists"`. Se verifica que `create` nunca fue llamado. |
| **Resultado** | **PASSED** |

### 1.2 `test_hash_and_verify_password`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Confirmar que el módulo de seguridad hashea contraseñas y las verifica correctamente. |
| **Qué valida** | Funciones puras de `src/infrastructure/security.py` (bcrypt/passlib). |
| **Cómo se hizo** | Se hashea `"securepass123"`, se verifica que `verify_password` acepta la contraseña original y rechaza `"wrongpassword"`. No requiere base de datos ni mocks. |
| **Resultado** | **PASSED** |

---

## 2. Scheduling Service

**Archivo:** `services/scheduling-service/tests/test_services.py`  
**Capa probada:** `SchedulingService`.

### 2.1 `test_book_appointment_slot_unavailable`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Impedir agendar una cita en un slot que no está disponible. |
| **Qué valida** | Regla de negocio de disponibilidad antes de reservar. |
| **Cómo se hizo** | Se mockea `AvailabilityRepository.get_by_id` para devolver un slot con `is_available=False`. Al llamar `book_appointment`, se espera `HTTPException 409` con `"Slot not available"`. Se verifica que `mark_booked` no se ejecutó. |
| **Resultado** | **PASSED** |

### 2.2 `test_update_appointment_status_forbidden_for_patient`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Restringir el cambio de estado de citas solo a personal médico (`doctor`, `admin`, `staff`). |
| **Qué valida** | Control de autorización por rol en `update_appointment_status`. |
| **Cómo se hizo** | Se invoca `update_appointment_status` con `user_role="patient"`. Se espera `HTTPException 403` con `"Only medical staff can update status"`. Se verifica que el repositorio de citas no fue consultado. |
| **Resultado** | **PASSED** |

---

## 3. Billing Service

**Archivo:** `services/billing-service/tests/test_services.py`  
**Capa probada:** `BillingService`.

### 3.1 `test_process_payment_invoice_not_found`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Manejar correctamente el intento de pago sobre una factura inexistente. |
| **Qué valida** | Gestión de error 404 en el flujo de pagos. |
| **Cómo se hizo** | `InvoiceRepository.get_by_id` devuelve `None`. Al procesar el pago, se espera `HTTPException 404` con `"Invoice not found"`. Se verifica que no se creó ningún pago. |
| **Resultado** | **PASSED** |

### 3.2 `test_process_payment_marks_invoice_paid_when_full_amount`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Confirmar que un pago igual o mayor al monto de la factura la marca como pagada. |
| **Qué valida** | Transición de estado `PENDING` → `PAID` cuando el monto cubre la deuda. |
| **Cómo se hizo** | Se mockea una factura pendiente de `50.00`. Se procesa un pago de `50.0` en efectivo. Se verifica que `payments.create` fue llamado una vez y que `invoices.update_status` recibió `(invoice_id, InvoiceStatus.PAID)`. |
| **Resultado** | **PASSED** |

---

## 4. Medical Record Service

**Archivo:** `services/medical-record-service/tests/test_services.py`  
**Capa probada:** `MedicalRecordService`.

### 4.1 `test_add_evolution_creates_note_for_existing_record`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Verificar que agregar una evolución clínica usa el expediente del paciente y crea la nota correctamente. |
| **Qué valida** | Orquestación entre `MedicalRecordRepository` y `EvolutionRepository`. |
| **Cómo se hizo** | Se mockea `get_or_create_by_patient` (devuelve un registro) y `evolutions.create` (devuelve la nota). Se llama `add_evolution` y se comprueba que los repositorios recibieron los parámetros correctos (`patient_id`, `record_id`, `doctor_id`, observaciones) y que el resultado es la nota creada. |
| **Resultado** | **PASSED** |

### 4.2 `test_get_patient_history_returns_record_and_evolutions`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Validar la estructura de respuesta al consultar el historial de un paciente. |
| **Qué valida** | Formato del dict retornado por `get_patient_history`. |
| **Cómo se hizo** | Se mockean registro y lista de 2 evoluciones. El resultado debe contener `record_id`, `patient_id` y `evolutions` con los valores esperados. |
| **Resultado** | **PASSED** |

---

## 5. Reporting Service

**Archivo:** `services/reporting-service/tests/test_services.py`  
**Capa probada:** `ReportingService` (agregación de datos vía HTTP a otros servicios).

### 5.1 `test_income_report_filters_by_doctor`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Comprobar que el reporte de ingresos filtra facturas por `doctor_id`. |
| **Qué valida** | Lógica de filtrado y cálculo de `total_income` y `count`. |
| **Cómo se hizo** | Se reemplaza `_fetch_billing_invoices` con un mock que devuelve 2 facturas de doctores distintos (100 y 200). Al filtrar por `doctor_a`, el resultado debe tener `count=1`, `total_income=100.0` y una sola factura del doctor correcto. |
| **Resultado** | **PASSED** |

### 5.2 `test_appointment_stats_groups_by_status`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Verificar el agrupamiento de citas por estado para estadísticas. |
| **Qué valida** | Uso de `Counter` sobre la lista de citas del scheduling-service. |
| **Cómo se hizo** | Se mockea `_fetch_scheduling_appointments` con 3 citas (2 `programada`, 1 `completada`). El resultado debe tener `total=3`, `by_status["programada"]=2` y `by_status["completada"]=1`. |
| **Resultado** | **PASSED** |

---

## 6. Admin Panel

**Archivo:** `services/admin-panel/tests/test_services.py`  
**Capa probada:** `AdminDashboardService`.

### 6.1 `test_dashboard_summary_aggregates_users`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Validar que el dashboard resume correctamente los conteos de usuarios por rol. |
| **Qué valida** | Agregación de totales: usuarios, pacientes y doctores. |
| **Cómo se hizo** | Se reemplaza `_get` con una función que devuelve 4 usuarios (2 patient, 1 doctor, 1 admin) desde identity-service y listas vacías en los demás endpoints. Se espera `total=4`, `patients=2`, `doctors=1`. |
| **Resultado** | **PASSED** |

### 6.2 `test_dashboard_summary_handles_service_errors`

| Aspecto | Detalle |
|---------|---------|
| **Objetivo** | Confirmar que el dashboard no falla cuando servicios externos no responden. |
| **Qué valida** | Resiliencia: bloques `try/except` que devuelven `None` en campos afectados. |
| **Cómo se hizo** | Se mockea `_get` para que identity-service y billing fallen con `RuntimeError`, mientras scheduling y reporting responden con datos válidos. Se verifica: `users.total=None`, `appointments.total=1`, `billing.pending_invoices=None`, `billing.total_income=500`. |
| **Resultado** | **PASSED** (con 4 warnings de `datetime.utcnow()` deprecado) |

---

## Técnicas comunes utilizadas

### Mocking de repositorios

Los servicios con capa de persistencia (`identity`, `scheduling`, `billing`, `medical-record`) reemplazan los repositorios reales después de instanciar el servicio:

```python
service = AuthService(session_mock)
service._repo = AsyncMock()
```

Esto evita conexiones a PostgreSQL y permite controlar exactamente qué devuelve cada operación.

### Mocking de clientes HTTP

`reporting-service` y `admin-panel` consumen otros microservicios vía `httpx`. Las pruebas reemplazan métodos internos (`_fetch_billing_invoices`, `_get`) en lugar de levantar servidores HTTP reales.

### Aserciones de efectos secundarios

Además del resultado, varias pruebas verifican que operaciones **no deseadas** no ocurrieron:

- `create.assert_not_awaited()` — no crear usuario si hay conflicto.
- `mark_booked.assert_not_awaited()` — no reservar slot no disponible.
- `get_by_id.assert_not_awaited()` — no consultar BD si el rol no tiene permiso.

### Datos de prueba

Todos los IDs se generan con `uuid4()`. Los objetos de dominio/ORM se simulan con `SimpleNamespace` o `MagicMock` para no depender de modelos SQLAlchemy completos.

---

## Salida de ejecución de referencia

```
identity-service          2 passed
scheduling-service        2 passed
billing-service           2 passed
medical-record-service    2 passed
reporting-service         2 passed
admin-panel               2 passed, 4 warnings
─────────────────────────────────────────
Total                     12 passed (100%)
```

---

## Próximos pasos sugeridos

1. **Corregir deprecaciones:** reemplazar `datetime.utcnow()` por `datetime.now(datetime.UTC)` en `admin-panel` y otros servicios que lo usen.
2. **Ampliar cobertura:** agregar pruebas de caminos felices (registro exitoso, agendamiento exitoso, etc.).
3. **Integrar en CI:** ejecutar `./scripts/run-tests.sh` en un pipeline de GitHub Actions antes de merge a `main`.
4. **Refinar manejo de errores:** en `admin-panel`, considerar logging estructurado en los `except Exception` en lugar de silenciar fallos sin traza.
