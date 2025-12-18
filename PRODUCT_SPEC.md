# Emo Finance - Especificación del Producto

## Visión General

Emo Finance es una aplicación de gestión financiera personal enfocada en el control de gastos mensuales y la planificación presupuestaria. A diferencia de apps de inversión o trading, se centra en ayudar al usuario a entender cuánto puede gastar en diferentes áreas de su vida.

## Problema que Resuelve

**Caso de uso inicial**: Un usuario necesita arrendar un lugar para vivir pero no sabe cuánto puede permitirse gastar en arriendo sin comprometer otras áreas de su presupuesto (ahorro, gastos cotidianos, uso de crédito).

**Solución**: Una herramienta que permite "jugar" con diferentes asignaciones presupuestarias y ver el impacto inmediato en la liquidez disponible.

---

## Conceptos Clave

### 1. Categorías Principales de Asignación

El usuario divide su sueldo en 4 categorías principales:

#### **Ahorro**
- Cantidad que el usuario quiere ahorrar cada mes
- Es una meta autoimpuesta
- Se resta del sueldo total

#### **Arriendo**
- Presupuesto para gastos relacionados con vivienda
- Incluye: arriendo base, gastos comunes, luz, agua, gas, internet
- Puede tener gastos fijos (arriendo base) y variables (cuenta de luz)
- Período: 1-31 de cada mes

#### **Crédito Usable**
- Límite autoimpuesto de gasto en tarjeta de crédito
- Período especial: finaliza el 24 de cada mes
- Incluye gastos fijos (suscripciones mensuales) y variables
- Muestra saldo disponible: Meta - Gastos Fijos - Gastos Variables
- Ejemplo: Meta $200.000, Gastos Fijos $50.000 → Disponible $150.000

#### **Líquido** (Calculado)
- **NO es asignable por el usuario**
- Fórmula: `Sueldo - Ahorro - Crédito Usable - Arriendo`
- Representa dinero disponible para gastos en efectivo/transferencia
- También puede tener gastos fijos (ej: locomoción)

### 2. Períodos

Existen dos tipos de períodos que corren en paralelo:

- **Período Mensual Estándar**: 1-31 de cada mes (Arriendo, Ahorro, Líquido)
- **Período de Crédito**: 25 del mes anterior - 24 del mes actual

### 3. Gastos Fijos vs Variables

- **Gastos Fijos**: Se repiten cada período (ej: Netflix, arriendo base)
- **Gastos Variables**: Únicos del período actual (ej: compra ocasional)

---

## Modelo de Datos

### Colecciones en MongoDB

#### **users**
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "hashed_password": "...",
  "is_active": true,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### **periods**
Registra cada período financiero del usuario.

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "tipo_periodo": "mensual_estandar" | "ciclo_credito",
  "fecha_inicio": ISODate,
  "fecha_fin": ISODate,
  "sueldo": 1500000,
  "metas_categorias": {
    "ahorro": 200000,
    "arriendo": 400000,
    "credito_usable": 300000
    // líquido se calcula: 1500000 - 200000 - 400000 - 300000 = 600000
  },
  "estado": "activo" | "cerrado" | "proyectado",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Campos**:
- `tipo_periodo`: Identifica si es período estándar (1-31) o ciclo de crédito (25-24)
- `sueldo`: Ingreso total del período
- `metas_categorias`: Cuánto quiere asignar a cada categoría (excepto líquido)
- `estado`:
  - `activo`: Período en curso
  - `cerrado`: Período finalizado
  - `proyectado`: Período futuro para planificación

#### **categories**
Categorías configuradas por el usuario.

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "nombre": "Arriendo",
  "tipo": "ahorro" | "arriendo" | "credito" | "liquido",
  "color": "#667eea",
  "icono": "🏠",
  "subcategorias": [
    {
      "nombre": "Arriendo Base",
      "color": "#764ba2"
    },
    {
      "nombre": "Luz",
      "color": "#f6ad55"
    },
    {
      "nombre": "Agua",
      "color": "#4299e1"
    }
  ],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Campos**:
- `tipo`: Define a qué categoría principal pertenece
- `subcategorias`: Divisiones dentro de la categoría (opcional)

#### **expense_templates**
Plantillas para gastos fijos recurrentes.

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "nombre": "Netflix",
  "valor": 9990,
  "categoria_id": ObjectId,
  "subcategoria_nombre": "Suscripciones",
  "dia_cargo": 15,
  "metodo_pago": "credito" | "debito" | "efectivo" | "transferencia",
  "activa": true,
  "notas": "Plan estándar",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Campos**:
- `dia_cargo`: Día del mes en que se cobra
- `activa`: Si está activa, se crea automáticamente en cada período
- Al inicio de cada período, se crean gastos desde estas plantillas

#### **expenses**
Gastos reales del usuario.

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "periodo_id": ObjectId,
  "plantilla_id": ObjectId | null,
  "nombre": "Supermercado",
  "valor": 45000,
  "fecha": ISODate,
  "categoria_id": ObjectId,
  "subcategoria_nombre": "Comida",
  "tipo": "fijo" | "variable",
  "metodo_pago": "credito" | "debito" | "efectivo" | "transferencia",
  "estado": "pendiente" | "pagado" | "proyectado",
  "notas": "Compra mensual",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Campos**:
- `plantilla_id`: Si viene de un gasto fijo, referencia a la plantilla
- `tipo`:
  - `fijo`: Gasto recurrente (generado desde plantilla)
  - `variable`: Gasto único del período
- `estado`:
  - `pendiente`: Gasto registrado pero no pagado
  - `pagado`: Gasto confirmado
  - `proyectado`: Gasto planificado para el futuro

---

## Flujo de Datos y Lógica de Negocio

### 1. Inicio de Período

Al comenzar un nuevo período (automático o manual):

1. Se crea un nuevo documento en `periods` con estado `activo`
2. El usuario ingresa su sueldo del período
3. El usuario asigna metas a: Ahorro, Arriendo, Crédito Usable
4. El sistema calcula Líquido automáticamente
5. Se generan automáticamente gastos desde `expense_templates` activas
6. Los gastos generados se marcan como `tipo: "fijo"` y `estado: "proyectado"`

### 2. Registro de Gastos

**Gasto Variable**:
```
Usuario → Crear gasto → Seleccionar categoría → Ingresar valor → Guardar
```
- Se descuenta del presupuesto de la categoría
- Actualiza saldo disponible en tiempo real

**Gasto Fijo (desde plantilla)**:
- Ya está creado al inicio del período
- Usuario puede marcar como `pagado` cuando se ejecute
- Puede editar el valor si varió (ej: cuenta de luz)
- Editar NO afecta la plantilla

### 3. Cálculos en Tiempo Real

**Saldo Disponible por Categoría**:
```
Meta Categoría - Σ(Gastos Fijos) - Σ(Gastos Variables)
```

**Líquido Disponible**:
```
Sueldo - Meta Ahorro - Meta Arriendo - Meta Crédito
```

**Ajuste de Metas**:
- Usuario puede modificar metas durante el período
- El sistema muestra impacto inmediato en Líquido
- Cambios se registran en historial del período

### 4. Cierre de Período

Al finalizar un período:
1. Estado cambia a `cerrado`
2. Se genera reporte de:
   - Gasto real vs Meta en cada categoría
   - Porcentaje de cumplimiento
   - Líquido sobrante/faltante
3. Se puede crear automáticamente el siguiente período con:
   - Mismas metas (o ajustadas según historial)
   - Plantillas de gastos fijos

---

## Funcionalidades Core

### 1. Dashboard Principal

**Vista del Período Actual**:
- Indicador de sueldo total
- 4 cards de categorías principales mostrando:
  - Meta asignada
  - Gastado hasta ahora
  - Disponible
  - Barra de progreso visual
- Líquido destacado (calculado automáticamente)
- Días restantes del período

### 2. Simulador de Asignación

**Modo "Jugar con Presupuesto"**:
- Sliders o inputs para ajustar metas
- Visualización en tiempo real del impacto
- Comparación con período anterior
- Sugerencias basadas en histórico
- Botón "Aplicar cambios" para guardar

**Ejemplo de Interfaz**:
```
Sueldo: $1.500.000

Ahorro:          [=======>   ] $200.000
Arriendo:        [=========> ] $400.000
Crédito Usable:  [=====>     ] $300.000
-----------------------------------
Líquido (auto):  [======>    ] $600.000
```

### 3. Gestión de Gastos

**Vistas**:
- Lista de gastos del período (agrupados por categoría)
- Calendario de gastos
- Filtros: por categoría, tipo, método de pago, estado

**Acciones**:
- Agregar gasto variable
- Marcar gasto fijo como pagado
- Editar valor de gasto fijo (sin cambiar plantilla)
- Eliminar gasto
- Ver detalle y notas

### 4. Gastos Fijos (Plantillas)

**Gestión de Recurrentes**:
- Lista de todas las plantillas activas
- Crear nueva plantilla
- Editar plantilla (afecta futuros períodos)
- Desactivar plantilla (no se generará en próximos períodos)
- Ver historial de un gasto fijo

### 5. Historial y Reportes

**Comparación de Períodos**:
- Tabla/gráfico de últimos N períodos
- Evolución de gastos por categoría
- Tendencias de ahorro
- Períodos con mayor/menor gasto

**Estadísticas**:
- Promedio de gasto por categoría
- Categoría con mayor variación
- Cumplimiento de metas (%)
- Proyección de próximo período

### 6. Alertas y Notificaciones

- "Has gastado el 80% de tu Crédito Usable"
- "Te quedan $50.000 disponibles en Arriendo"
- "Próximo gasto fijo: Netflix - $9.990 (15 de Mayo)"
- "Se aproxima el cierre del período de crédito (24 de Mayo)"

---

## Reglas de Negocio

### 1. Categorías

- Un usuario DEBE tener las 4 categorías principales
- Líquido NUNCA puede ser asignado manualmente
- La suma Ahorro + Arriendo + Crédito NO puede exceder Sueldo
- Si se aumenta una categoría, debe ajustarse otra u otras

### 2. Períodos

- Solo puede haber UN período `activo` de cada tipo por usuario
- Un período NO puede tener fecha_fin < fecha_inicio
- El sueldo debe ser mayor a 0
- Al cerrar un período, no se puede reabrir (pero sí consultar)

### 3. Gastos

- Un gasto debe pertenecer a un período y una categoría
- Un gasto tipo `fijo` debe tener `plantilla_id`
- No se puede eliminar un gasto si está `pagado` (solo marcar como anulado)
- Fecha del gasto debe estar dentro del rango del período

### 4. Plantillas

- Una plantilla solo puede pertenecer a una categoría
- `dia_cargo` debe estar entre 1-31
- Al desactivar plantilla, no afecta gastos ya generados
- Al editar plantilla, solo afecta futuros períodos

---

## Endpoints API Propuestos

### Períodos

```
GET    /api/v1/periods                    # Listar períodos del usuario
GET    /api/v1/periods/active             # Obtener período activo
GET    /api/v1/periods/{id}               # Detalle de período
POST   /api/v1/periods                    # Crear nuevo período
PUT    /api/v1/periods/{id}               # Actualizar período (ajustar metas)
POST   /api/v1/periods/{id}/close         # Cerrar período
GET    /api/v1/periods/{id}/summary       # Resumen y estadísticas
```

### Categorías

```
GET    /api/v1/categories                 # Listar categorías del usuario
POST   /api/v1/categories                 # Crear categoría personalizada
PUT    /api/v1/categories/{id}            # Actualizar categoría
DELETE /api/v1/categories/{id}            # Eliminar (solo si no tiene gastos)
```

### Gastos

```
GET    /api/v1/expenses                   # Listar gastos (filtros: periodo, categoria, tipo)
GET    /api/v1/expenses/{id}              # Detalle de gasto
POST   /api/v1/expenses                   # Crear gasto variable
PUT    /api/v1/expenses/{id}              # Actualizar gasto
DELETE /api/v1/expenses/{id}              # Eliminar gasto
PATCH  /api/v1/expenses/{id}/mark-paid    # Marcar como pagado
```

### Plantillas de Gastos Fijos

```
GET    /api/v1/expense-templates          # Listar plantillas del usuario
GET    /api/v1/expense-templates/{id}     # Detalle de plantilla
POST   /api/v1/expense-templates          # Crear plantilla
PUT    /api/v1/expense-templates/{id}     # Actualizar plantilla
PATCH  /api/v1/expense-templates/{id}/toggle # Activar/desactivar
DELETE /api/v1/expense-templates/{id}     # Eliminar plantilla
```

### Dashboard y Estadísticas

```
GET    /api/v1/dashboard                  # Dashboard del período activo
GET    /api/v1/dashboard/simulate         # Simular cambios en asignación (query params)
GET    /api/v1/stats/comparison           # Comparación entre períodos
GET    /api/v1/stats/trends               # Tendencias de gasto
```

---

## Consideraciones Técnicas

### 1. Frontend (Angular)

**Estructura de Carpetas**:
```
src/app/
├── global_components/
│   ├── navbar/
│   ├── sidebar/
│   └── card/
├── pages/
│   ├── home/              # Dashboard principal
│   ├── profile/
│   ├── login/
│   ├── periods/           # Gestión de períodos
│   ├── expenses/          # Lista y gestión de gastos
│   ├── templates/         # Gastos fijos
│   ├── simulator/         # Simulador de asignación
│   └── reports/           # Reportes e historial
├── services/
│   ├── auth.service.ts
│   ├── period.service.ts
│   ├── expense.service.ts
│   ├── category.service.ts
│   └── template.service.ts
└── guards/
    └── auth.guard.ts
```

**Estado/Signals**:
- Usar Angular Signals para reactividad
- Estado global del período activo
- Cálculos en tiempo real (líquido disponible)

### 2. Backend (FastAPI)

**Estructura de Carpetas**:
```
backend/app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── auth.py
│           ├── periods.py
│           ├── expenses.py
│           ├── categories.py
│           ├── templates.py
│           └── dashboard.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
├── crud/
│   ├── period.py
│   ├── expense.py
│   ├── category.py
│   └── template.py
├── models/
│   ├── user.py
│   ├── period.py
│   ├── expense.py
│   ├── category.py
│   └── template.py
└── schemas/
    ├── period.py
    ├── expense.py
    ├── category.py
    └── template.py
```

### 3. Base de Datos (MongoDB)

**Índices Necesarios**:
```javascript
// users
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "username": 1 }, { unique: true })

// periods
db.periods.createIndex({ "user_id": 1, "estado": 1 })
db.periods.createIndex({ "user_id": 1, "fecha_inicio": -1 })

// expenses
db.expenses.createIndex({ "user_id": 1, "periodo_id": 1 })
db.expenses.createIndex({ "user_id": 1, "categoria_id": 1 })
db.expenses.createIndex({ "fecha": -1 })

// expense_templates
db.expense_templates.createIndex({ "user_id": 1, "activa": 1 })

// categories
db.categories.createIndex({ "user_id": 1, "tipo": 1 })
```

### 4. Validaciones Importantes

- Suma de asignaciones ≤ Sueldo
- Fechas de gastos dentro del período
- Usuario solo puede ver/editar sus propios datos
- Gastos fijos solo pueden editarse en valor, no en plantilla
- No permitir eliminar categorías con gastos asociados

---

## Roadmap de Desarrollo

### Fase 1: Core Funcional (MVP)
- [x] Sistema de autenticación
- [ ] Modelo de datos (períodos, gastos, categorías)
- [ ] CRUD de períodos
- [ ] CRUD de gastos
- [ ] Dashboard básico con las 4 categorías
- [ ] Cálculo automático de líquido

### Fase 2: Gastos Fijos y Plantillas
- [ ] CRUD de plantillas de gastos fijos
- [ ] Generación automática de gastos al inicio de período
- [ ] Edición de gastos fijos sin afectar plantilla
- [ ] Vista de calendario de gastos recurrentes

### Fase 3: Simulador y Optimización
- [ ] Simulador de asignación presupuestaria
- [ ] Ajuste de metas en tiempo real
- [ ] Comparación visual del impacto
- [ ] Sugerencias basadas en historial

### Fase 4: Reportes y Análisis
- [ ] Comparación entre períodos
- [ ] Gráficos de evolución de gastos
- [ ] Estadísticas de cumplimiento de metas
- [ ] Proyección de próximo período
- [ ] Exportación de reportes (PDF/Excel)

### Fase 5: Mejoras UX
- [ ] Alertas y notificaciones inteligentes
- [ ] Modo oscuro
- [ ] PWA (Progressive Web App)
- [ ] Optimizaciones de performance
- [ ] Onboarding para nuevos usuarios

### Fase 6: Funcionalidades Avanzadas (Futuro)
- [ ] Múltiples cuentas bancarias
- [ ] Importación de movimientos bancarios
- [ ] Compartir presupuesto con pareja/familia
- [ ] Metas de ahorro a largo plazo
- [ ] Integración con APIs bancarias

---

## Consideraciones de Seguridad

1. **Autenticación**: JWT tokens con expiración
2. **Autorización**: Validar user_id en todas las operaciones
3. **Datos sensibles**: No almacenar información bancaria real
4. **Rate limiting**: Prevenir abuso de API
5. **HTTPS**: Obligatorio en producción
6. **Validación**: Input validation en frontend Y backend
7. **CORS**: Configurado solo para dominios autorizados

---

## Métricas de Éxito

### KPIs Técnicos
- Tiempo de carga < 2 segundos
- 99.9% uptime
- Respuesta de API < 200ms

### KPIs de Producto
- Usuario crea primer período en < 5 minutos
- 80% de usuarios registran al menos 5 gastos/mes
- Usuario usa simulador de presupuesto al menos 1 vez/mes
- Tasa de retención > 60% a 30 días

---

## Preguntas Abiertas / Para Discusión

1. ¿Permitir múltiples divisas?
2. ¿Manejar ingresos adicionales (no solo sueldo)?
3. ¿Categorías compartidas entre usuarios (parejas)?
4. ¿Exportar datos a formato estándar (CSV, Excel)?
5. ¿Integración con bancos para importar movimientos?
6. ¿Modo "ahorro para meta específica" (ej: vacaciones)?
7. ¿Recordatorios de gastos fijos próximos a vencer?

---

## Conclusión

Esta especificación define una aplicación de gestión financiera personal simple pero poderosa, enfocada en resolver un problema real: **saber cuánto puedo gastar en cada área de mi vida**.

El diseño permite flexibilidad para "jugar" con el presupuesto mientras mantiene claridad sobre el impacto de cada decisión en la liquidez disponible.

---

**Documento creado**: 2025-01-XX
**Última actualización**: 2025-01-XX
**Versión**: 1.0
