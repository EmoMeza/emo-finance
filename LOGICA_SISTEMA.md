# 🧠 Lógica del Sistema - Emo Finance

> **Documento de Referencia para la Implementación de la Versión 1.0**
>
> Este documento detalla la lógica completa del sistema de gestión financiera, incluyendo el comportamiento de categorías, gastos, períodos y cálculos. Es la fuente de verdad para el desarrollo.

---

## 📋 Tabla de Contenidos

1. [Conceptos Fundamentales](#conceptos-fundamentales)
2. [Las 4 Categorías Principales](#las-4-categorías-principales)
3. [Sistema de Gastos](#sistema-de-gastos)
4. [Sistema de Aportes](#sistema-de-aportes)
5. [Períodos y su Gestión](#períodos-y-su-gestión)
6. [Flujo del Usuario Primerizo](#flujo-del-usuario-primerizo)
7. [Flujo de Períodos Subsecuentes](#flujo-de-períodos-subsecuentes)
8. [Cálculos y Fórmulas](#cálculos-y-fórmulas)
9. [Visualización de Datos](#visualización-de-datos)
10. [Modelo de Datos](#modelo-de-datos)

---

## 🎯 Conceptos Fundamentales

### Objetivo Principal
**Permitir al usuario saber cuánto puede gastar en cada área de su vida sin quebrar.**

La aplicación no solo registra gastos, sino que ayuda a **planificar** y **simular** diferentes escenarios antes de tomar decisiones financieras.

### Principio de Funcionamiento
- El usuario define **metas** para cada categoría
- El sistema calcula automáticamente el **líquido disponible**
- Los **gastos fijos** se copian automáticamente cada período
- Los **gastos variables** se registran según necesidad
- Los **aportes** pueden aumentar el presupuesto disponible

---

## 📊 Las 4 Categorías Principales

### 1. 💵 Ahorro
**Propósito**: Dinero destinado a ser ahorrado mensualmente.

**Características**:
- Tiene una **meta mensual** definida por el usuario
- Se resta del sueldo para calcular el líquido
- Puede tener gastos fijos y variables:
  - **Gastos Variables**: Cuando saco dinero del ahorro por emergencia (valor negativo en ahorro)
  - **Aportes/Ingresos**: Cuando agrego dinero extra al ahorro (valor positivo)
- **No afecta el líquido directamente**, solo se registra como meta

**Ejemplo**:
```
Meta de Ahorro: $250,000
- Gasto variable (emergencia médica): -$50,000
- Aporte (venta de artículo): +$30,000
= Total real ahorrado: $230,000
```

### 2. 🏠 Arriendo
**Propósito**: Presupuesto para vivienda y gastos relacionados.

**Características**:
- Tiene una **meta/presupuesto** definida
- Se resta del sueldo para calcular el líquido
- Puede tener:
  - **Gastos Fijos**: Arriendo mensual, gastos comunes, servicios básicos
  - **Gastos Variables**: Compras para el hogar (pala, basurero, reparaciones)
  - **Aportes**: Dinero que aporta tu pareja u otra persona

**Cálculo del Total**:
```
Gastos Fijos: $380,000 (arriendo) + $40,000 (gastos comunes) = $420,000
+ Gasto Fijo: $30,000 (luz, agua, gas) = $450,000
+ Gasto Variable: $20,000 (comida del mes) = $470,000
- Aporte (pareja): $170,000
= Total Arriendo Real: $300,000
```

**Visualización**:
- Meta/Presupuesto: $450,000
- Gastos Totales: $470,000
- Aportes: -$170,000
- **Total Real: $300,000** (esto es lo que se resta del sueldo)

### 3. 💳 Crédito Usable
**Propósito**: Límite autoimpuesto para gastos con tarjeta de crédito.

**Características**:
- **Meta de Crédito Total**: Cuánto quieres gastar en total con crédito este período
- **Período de Crédito**: Del 25 del mes anterior al 24 del mes actual
- Puede tener:
  - **Gastos Fijos Permanentes**: Netflix, Spotify (se copian cada período)
  - **Gastos Fijos Temporales**: Compra en cuotas (ej: 3/5 cuotas restantes)
  - **Gastos Variables**: Compras ocasionales durante el período

**Cálculo del Crédito Usable Real**:
```
Meta de Crédito Total: $200,000
- Gastos Fijos Permanentes:
  - Netflix: $20,000
  - Claude AI: $10,000
- Gastos Fijos Temporales:
  - Juego en cuotas (2/5): $5,000
= Crédito Usable Inicial: $165,000

Durante el período:
- Gasto Variable (pizza): $15,000
- Gasto Variable (compras online): $30,000
= Crédito Usable Restante: $120,000 (dinámico)
```

**Importante**:
- El crédito del período anterior se paga al inicio del nuevo período mensual
- El crédito del período actual NO se resta del líquido (solo es un límite)
- El total gastado en crédito se registra para usarse en el próximo período mensual

### 4. 💸 Liquidez
**Propósito**: Dinero disponible en efectivo o transferencia para gastos del día a día.

**Características**:
- **NO tiene meta**, se calcula automáticamente
- Es el resultado de: `Sueldo - Ahorro - Arriendo - Crédito Período Anterior`
- Puede tener:
  - **Gastos Fijos**: Locomoción (no se puede pagar con crédito)
  - **Gastos Variables**: Chocolates, salidas, compras en efectivo
  - **Aportes**: Dinero extra de otro trabajo, venta de algo, reembolsos

**Cálculo**:
```
Sueldo: $1,000,000
- Ahorro Meta: $250,000
- Arriendo Total Real: $300,000
- Crédito Período Anterior: $220,000
= Liquidez Inicial: $230,000

Durante el período:
- Gasto Fijo (locomoción): $40,000
- Gasto Variable (salidas): $50,000
+ Aporte (venta de celular): $100,000
= Liquidez Disponible: $240,000 (dinámico)
```

---

## 🏷️ Sistema de Gastos

### Tipos de Gastos

#### 1. Gastos Fijos
**Definición**: Gastos que se repiten en el tiempo.

**Subtipos**:

**A. Permanentes**
- Se copian automáticamente cada período
- Continúan hasta que el usuario los desactive
- **Ejemplos**: Netflix, Spotify, arriendo, gastos comunes

**B. Temporales (Con Cuotas)**
- Tienen un número de períodos definidos
- Se copian solo mientras queden períodos restantes
- Cuando llegan a 0 períodos, dejan de copiarse
- Se mantiene registro histórico de que se pagaron
- **Ejemplos**:
  - Compra en 5 cuotas de un juego
  - Crédito de consumo en 12 cuotas
  - Curso en 3 pagos

**Campos**:
```typescript
{
  nombre: string
  monto: number
  categoria_id: string
  es_permanente: boolean
  periodos_restantes?: number  // Solo si no es permanente
  descripcion?: string
}
```

**Comportamiento en Cambio de Período**:
```
Período 1:
- Gasto Fijo: "Juego en cuotas" - $5,000 (permanente: false, períodos: 5)

Período 2 (auto-copiado):
- Gasto Fijo: "Juego en cuotas" - $5,000 (permanente: false, períodos: 4)

Período 3:
- Gasto Fijo: "Juego en cuotas" - $5,000 (permanente: false, períodos: 3)

...

Período 6:
- (Ya no se copia, períodos llegó a 0)
- Se mantiene registro en períodos 1-5 para historial
```

#### 2. Gastos Variables
**Definición**: Gastos únicos del período, no planificados.

**Características**:
- No se copian al siguiente período
- Se registran según necesidad
- Pueden ser de cualquier categoría
- **Ejemplos**:
  - Pizza del viernes
  - Compra de dulces
  - Regalo de cumpleaños
  - Emergencia médica (si se saca del ahorro)

**Campos**:
```typescript
{
  nombre: string
  monto: number
  categoria_id: string
  fecha: datetime
  descripcion?: string
}
```

---

## 💰 Sistema de Aportes

### Definición
Los **aportes** son ingresos adicionales que aumentan el presupuesto disponible de una categoría.

### Características
- Son montos **positivos** que se suman (o restan del gasto total)
- Pueden ser **fijos** o **variables**
- Pueden aplicar a cualquier categoría

### Tipos de Aportes

#### 1. Aportes Fijos
**Ejemplos**:
- Aporte mensual de tu pareja para arriendo: $170,000
- Ingreso extra de trabajo secundario: $100,000
- Mesada de familiares: $50,000

**Comportamiento**: Se copian automáticamente cada período (como gastos fijos permanentes)

#### 2. Aportes Variables
**Ejemplos**:
- Venta de un celular usado: $100,000 (a liquidez)
- Reembolso de un gasto: $20,000
- Dinero encontrado/ganado: $10,000

**Comportamiento**: Se registran una sola vez en el período actual

### Modelo de Datos

Los aportes son técnicamente **gastos con monto negativo** o una entidad separada.

**Opción Recomendada: Entidad Separada**
```typescript
{
  nombre: string
  monto: number  // Siempre positivo
  categoria_id: string
  es_fijo: boolean
  fecha: datetime
  descripcion?: string
}
```

**Cálculo en Categoría**:
```
Total Categoría = Suma(Gastos Fijos) + Suma(Gastos Variables) - Suma(Aportes)
```

---

## 📅 Períodos y su Gestión

### Tipos de Períodos

#### 1. Período Mensual Estándar
**Fechas**: Día 1 al último día del mes (1-31, 1-30, 1-28/29)

**Propósito**:
- Gestión de Ahorro, Arriendo y Liquidez
- Ciclo de ingresos (llegada del sueldo)

**Características**:
- Se crea automáticamente el día 1 del mes
- Se cierra automáticamente el último día del mes
- Copia gastos fijos permanentes y temporales (con períodos > 0)

#### 2. Período de Crédito
**Fechas**: Día 25 del mes anterior al 24 del mes actual (25-24)

**Propósito**:
- Gestión de gastos con tarjeta de crédito
- Seguimiento del ciclo de facturación

**Características**:
- Se crea automáticamente el día 25 del mes
- Se cierra automáticamente el día 24 del mes siguiente
- El total gastado se usa como "crédito a pagar" en el próximo período mensual
- Funciona en **paralelo** con el período mensual

### Relación Entre Períodos

```
Período Crédito 1: Nov 25 - Dic 24 → Total Gastado: $220,000
                                            ↓
Período Mensual 1: Ene 1 - Ene 31 → Crédito Anterior: $220,000
                                    (se resta del líquido)
                                            ↓
Período Crédito 2: Dic 25 - Ene 24 → Total Gastado: $200,000
                                            ↓
Período Mensual 2: Feb 1 - Feb 28 → Crédito Anterior: $200,000
                                    (se resta del líquido)
```

---

## 🆕 Flujo del Usuario Primerizo

### Primera Vez que Usa la Aplicación

**Paso 1: El sistema auto-crea períodos vacíos**
```
Al hacer login y no tener períodos:
- Se crea Período Mensual Actual (con valores en 0)
- Se crea Período de Crédito Actual (con valores en 0)
```

**Paso 2: Se abre automáticamente el modal de configuración**

**Paso 3: Usuario llena el formulario inicial**

**Campos**:
```typescript
{
  // Datos del Período Mensual
  sueldo: 1000000,

  // Metas de Categorías
  meta_ahorro: 250000,
  meta_arriendo: 450000,
  meta_credito_total: 200000,

  // SOLO PRIMERA VEZ: Deuda del período de crédito anterior
  credito_periodo_anterior: 220000
}
```

**Paso 4: Usuario desglosa sus gastos fijos**

Para **Crédito**:
```
Meta Total: $200,000
Desglose:
- ✅ Gasto Fijo Permanente: Netflix $20,000
- ✅ Gasto Fijo Permanente: Claude AI $10,000
- ✅ Gasto Fijo Temporal: Juego (cuota 2/5) $5,000

Crédito Usable Inicial: $200,000 - $35,000 = $165,000
```

Para **Arriendo**:
```
Meta/Presupuesto: $450,000
Desglose:
- ✅ Gasto Fijo: Arriendo $380,000
- ✅ Gasto Fijo: Gastos comunes $40,000
- ✅ Gasto Fijo: Luz, agua, gas $30,000
- ✅ Gasto Variable: Comida del mes $20,000
- ✅ Aporte Fijo: Aporte pareja $170,000 (negativo)

Total Arriendo Real: $470,000 - $170,000 = $300,000
```

**Paso 5: Cálculo de Liquidez**

```
Liquidez = Sueldo - Ahorro - Arriendo Real - Crédito Anterior
Liquidez = $1,000,000 - $250,000 - $300,000 - $220,000
Liquidez = $230,000
```

**Paso 6: Usuario confirma y se guarda todo**

Lo que se guarda:
```
✅ Período Mensual actualizado con sueldo y metas
✅ Período de Crédito actualizado con total_gastado (crédito anterior)
✅ Gastos Fijos creados en sus respectivas categorías
✅ Aportes creados
✅ Dashboard se actualiza con toda la información
```

---

## 🔄 Flujo de Períodos Subsecuentes

### Cambio Automático de Período (Día 1 del Mes)

**Proceso Automático**:

1. **Cerrar Período Anterior**
   ```
   - Marcar Período Mensual Anterior como CERRADO
   - Mantener todos sus datos para historial
   ```

2. **Crear Nuevo Período Mensual**
   ```
   - Copiar sueldo del período anterior
   - Copiar metas de categorías (ahorro, arriendo, crédito_total)
   - Estado: ACTIVO
   ```

3. **Obtener Crédito del Período Anterior**
   ```
   - Buscar el Período de Crédito que terminó justo antes
   - Obtener su total_gastado
   - Este valor será el "crédito_anterior" para cálculos
   ```

4. **Copiar Gastos Fijos**
   ```
   Para cada Gasto Fijo del período anterior:

   SI es_permanente == true:
     → Crear nuevo gasto fijo idéntico en nuevo período

   SI es_permanente == false Y periodos_restantes > 0:
     → Crear nuevo gasto fijo con periodos_restantes - 1

   SI es_permanente == false Y periodos_restantes == 0:
     → NO copiar (ya terminó)
   ```

5. **Copiar Aportes Fijos**
   ```
   Para cada Aporte con es_fijo == true:
     → Crear nuevo aporte en nuevo período
   ```

6. **NO Copiar Gastos Variables**
   ```
   Los gastos variables se quedan en el período anterior
   (son únicos de ese período)
   ```

### Edición Durante el Período

**El usuario puede en cualquier momento**:
- Editar sueldo
- Editar metas de categorías
- Agregar/eliminar/editar gastos fijos
- Agregar gastos variables
- Agregar/eliminar aportes

**Los cambios se reflejan de inmediato**:
- Recálculo automático de líquido
- Actualización de crédito usable disponible
- Actualización de visualizaciones

---

## 🧮 Cálculos y Fórmulas

### Fórmula de Liquidez

```typescript
liquidez = sueldo - meta_ahorro - total_arriendo_real - credito_periodo_anterior

Donde:
- sueldo: Ingreso mensual del usuario
- meta_ahorro: Meta de ahorro definida
- total_arriendo_real: Gastos - Aportes de categoría Arriendo
- credito_periodo_anterior: total_gastado del período de crédito que terminó
```

### Fórmula de Total de Categoría

```typescript
total_categoria =
  suma(gastos_fijos) +
  suma(gastos_variables) -
  suma(aportes)

// Para categorías con meta (Ahorro, Arriendo, Crédito)
disponible = meta - total_categoria
```

### Fórmula de Crédito Usable Real

```typescript
credito_usable_real =
  meta_credito_total -
  suma(gastos_fijos_credito) -
  suma(gastos_variables_credito) +
  suma(aportes_credito)  // Si aplica

// Este valor es dinámico y cambia con cada gasto variable
```

### Porcentaje de Uso

```typescript
porcentaje_uso = (total_categoria / meta) * 100

// Para Liquidez (que no tiene meta)
porcentaje_liquido_usado = (gastos_liquidez / liquidez_inicial) * 100
```

---

## 📊 Visualización de Datos

### Dashboard Principal

**Header**:
```
┌─────────────────────────────────────────┐
│ Sueldo del Período: $1,000,000          │
│ [Editar Período]                        │
└─────────────────────────────────────────┘
```

**Grid de 4 Categorías**:

Cada tarjeta muestra:
```
┌─────────────────────────────────────────┐
│ 💵 AHORRO                     [👁️ Ver]  │
├─────────────────────────────────────────┤
│ Meta: $250,000                          │
│ Gastado: $0                             │
│ Disponible: $250,000                    │
│ [████████████████████░░] 80%            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🏠 ARRIENDO                   [👁️ Ver]  │
├─────────────────────────────────────────┤
│ Presupuesto: $450,000                   │
│ Gastos: $470,000                        │
│ Aportes: -$170,000                      │
│ Total Real: $300,000                    │
│ [████████████░░░░░░░░] 66%              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 💳 CRÉDITO USABLE            [👁️ Ver]  │
├─────────────────────────────────────────┤
│ Meta: $200,000                          │
│ Gastos Fijos: $35,000                   │
│ Gastos Variables: $45,000               │
│ Disponible: $120,000                    │
│ [████████████████░░░░] 60%              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 💸 LIQUIDEZ (Calculado)      [👁️ Ver]  │
├─────────────────────────────────────────┤
│ Inicial: $230,000                       │
│ Gastado: $90,000                        │
│ Aportes: +$100,000                      │
│ Disponible: $240,000                    │
│ [██████████████████░░] 104%             │
└─────────────────────────────────────────┘
```

### Vista Detallada de Categoría (Al hacer clic en 👁️ Ver)

**Modal con pestañas**:

**Pestaña: Resumen**
```
📊 Resumen de Arriendo
──────────────────────────────────────
Presupuesto/Meta:      $450,000
Total Gastos Fijos:    $450,000
Total Gastos Variables: $20,000
Total Aportes:         -$170,000
──────────────────────────────────────
TOTAL REAL:            $300,000
Diferencia con meta:   -$150,000 ✅
```

**Pestaña: Gastos Fijos**
```
🔄 Gastos Fijos Permanentes
──────────────────────────────────────
✅ Arriendo                  $380,000
✅ Gastos comunes            $40,000
✅ Luz, agua, gas            $30,000
──────────────────────────────────────
Total:                       $450,000

[+ Agregar Gasto Fijo]
```

**Pestaña: Gastos Variables**
```
📝 Gastos Variables del Período
──────────────────────────────────────
- Comida del mes (05/01)     $20,000
──────────────────────────────────────
Total:                       $20,000

[+ Agregar Gasto Variable]
```

**Pestaña: Aportes**
```
💰 Aportes del Período
──────────────────────────────────────
✅ Aporte pareja (fijo)      $170,000
──────────────────────────────────────
Total:                       $170,000

[+ Agregar Aporte]
```

---

## 💾 Modelo de Datos

### Colecciones MongoDB

#### 1. `users`
```typescript
{
  _id: ObjectId
  username: string
  email: string
  password_hash: string
  created_at: datetime
  updated_at: datetime
}
```

#### 2. `periods`
```typescript
{
  _id: ObjectId
  user_id: ObjectId
  tipo_periodo: "mensual_estandar" | "ciclo_credito"
  fecha_inicio: datetime
  fecha_fin: datetime
  sueldo: float  // Solo para períodos mensuales
  estado: "activo" | "cerrado" | "proyectado"

  // Solo para períodos de crédito
  total_gastado: float  // Suma de todos los gastos del período

  created_at: datetime
  updated_at: datetime
}
```

#### 3. `categories`
```typescript
{
  _id: ObjectId
  user_id: ObjectId
  nombre: string  // "Ahorro", "Arriendo", "Crédito", "Liquidez"
  slug: string  // "ahorro", "arriendo", "credito", "liquidez"
  icono: string  // Emoji
  color: string  // Hex color
  tiene_meta: boolean  // true para ahorro/arriendo/credito, false para liquidez
  meta_default: float  // Meta por defecto
  created_at: datetime
  updated_at: datetime
}
```

#### 4. `expenses` (Gastos Fijos y Variables)
```typescript
{
  _id: ObjectId
  user_id: ObjectId
  period_id: ObjectId
  categoria_id: ObjectId

  nombre: string
  monto: float
  descripcion: string?

  // Tipo de gasto
  tipo: "fijo" | "variable"

  // Solo para gastos fijos
  es_permanente: boolean?
  periodos_restantes: int?  // null si es permanente

  fecha_registro: datetime
  created_at: datetime
  updated_at: datetime
}
```

#### 5. `aportes`
```typescript
{
  _id: ObjectId
  user_id: ObjectId
  period_id: ObjectId
  categoria_id: ObjectId

  nombre: string
  monto: float  // Siempre positivo
  descripcion: string?

  es_fijo: boolean  // true = se copia cada período

  fecha_registro: datetime
  created_at: datetime
  updated_at: datetime
}
```

### Índices Recomendados

```javascript
// periods
db.periods.createIndex({ user_id: 1, estado: 1, tipo_periodo: 1 })
db.periods.createIndex({ user_id: 1, fecha_inicio: -1 })

// categories
db.categories.createIndex({ user_id: 1, slug: 1 })

// expenses
db.expenses.createIndex({ period_id: 1, categoria_id: 1 })
db.expenses.createIndex({ user_id: 1, tipo: 1 })

// aportes
db.aportes.createIndex({ period_id: 1, categoria_id: 1 })
db.aportes.createIndex({ user_id: 1, es_fijo: 1 })
```

---

## ✅ Checklist de Implementación

### Backend

- [ ] Actualizar modelo `Period` con `total_gastado`
- [ ] Crear modelo `Expense` con tipos fijo/variable y permanente/temporal
- [ ] Crear modelo `Aporte` con flag es_fijo
- [ ] Implementar CRUD de Expenses
- [ ] Implementar CRUD de Aportes
- [ ] Crear endpoint para obtener desglose de categoría
- [ ] Implementar lógica de copia automática de gastos fijos
- [ ] Implementar lógica de copia automática de aportes fijos
- [ ] Implementar job/tarea para cierre/apertura automática de períodos
- [ ] Actualizar cálculo de liquidez con nueva fórmula
- [ ] Crear endpoint de resumen de categoría (gastos + aportes)

### Frontend

- [ ] Crear componente de vista detallada de categoría (modal)
- [ ] Crear formulario de agregar gasto fijo (con opción permanente/temporal)
- [ ] Crear formulario de agregar gasto variable
- [ ] Crear formulario de agregar aporte (fijo/variable)
- [ ] Implementar visualización de desglose en tarjetas de categoría
- [ ] Actualizar cálculo de liquidez en dashboard
- [ ] Implementar indicadores dinámicos (crédito usable real)
- [ ] Crear vista de configuración de período (editar metas)
- [ ] Implementar flujo de primer uso con campo de crédito anterior
- [ ] Agregar pestañas en modal de categoría (resumen/fijos/variables/aportes)

### Testing

- [ ] Tests de cálculo de liquidez
- [ ] Tests de cálculo de total de categoría
- [ ] Tests de copia de gastos fijos (permanentes y temporales)
- [ ] Tests de cierre/apertura de períodos
- [ ] Tests de detección de primer uso
- [ ] Tests de validaciones de negocio

---

## 📝 Notas Importantes

1. **Automatización vs. Control Manual**
   - Los períodos se crean/cierran automáticamente
   - El usuario puede editar en cualquier momento
   - No se requiere confirmación para cambios de período

2. **Historial y Auditoría**
   - Todos los períodos cerrados se mantienen
   - Los gastos fijos temporales que terminan quedan en historial
   - Se puede generar reportes de períodos pasados

3. **Validaciones Clave**
   - No permitir sueldo <= 0 en ediciones
   - Permitir sueldo = 0 en creación automática
   - Validar que períodos_restantes no sea negativo
   - Validar que aportes sean > 0

4. **Performance**
   - Usar índices para queries frecuentes
   - Cachear cálculos complejos si es necesario
   - Paginación en listados de gastos

---

**Versión del Documento**: 1.0
**Última Actualización**: 2025-01-19
**Próxima Revisión**: Antes de iniciar desarrollo de v1.0
