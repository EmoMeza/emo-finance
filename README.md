# 💰 Emo Finance

> **"¿Cuánto puedo permitirme gastar en arriendo sin quebrar?"**

Una aplicación web de gestión financiera personal enfocada en **presupuestos inteligentes** y **control de gastos mensuales**. No es una app de trading ni inversiones, es tu compañero para entender **cuánto puedes gastar en cada área de tu vida**.

---

## 🎯 ¿Por Qué Emo Finance?

### El Problema Real

Imagina esta situación común:
- Necesitas arrendar un departamento
- Ves opciones de $300.000, $400.000, $500.000
- **¿Cuál puedes realmente permitirte sin sacrificar tu ahorro o quedarte sin liquidez?**

La mayoría de las apps financieras te muestran cuánto gastaste, pero **no te ayudan a planificar cuánto PUEDES gastar**.

### La Solución: Presupuesto Interactivo

Emo Finance te permite **"jugar" con tu presupuesto** en tiempo real:

```
Tu Sueldo: $1.500.000
┌─────────────────────────────────────┐
│ 💵 Ahorro          $200.000  (13%)  │
│ 🏠 Arriendo        $400.000  (27%)  │
│ 💳 Crédito Usable  $300.000  (20%)  │
├─────────────────────────────────────┤
│ 💸 Líquido         $600.000  (40%)  │ ← Calculado automáticamente
└─────────────────────────────────────┘
```

**¿Quieres ver qué pasa si aumentas el arriendo a $450k?**
→ Mueves el slider, y al instante ves que tu líquido baja a $550k.

**¿Es sostenible? ¿Cómo se compara con el mes pasado?**
→ La app te lo muestra inmediatamente.

---

## ✨ Características Principales

### 🎮 Simulador de Presupuesto
- Ajusta en tiempo real cuánto asignas a cada categoría
- Visualiza el impacto inmediato en tu liquidez disponible
- Compara con períodos anteriores
- Toma decisiones informadas **antes** de comprometerte

### 📊 4 Categorías Fundamentales

1. **💵 Ahorro**: Meta de ahorro mensual. Puede tener gastos (emergencias) y aportes (ingresos extra)
2. **🏠 Arriendo**: Presupuesto para vivienda (arriendo, servicios, comida). Puede tener gastos y aportes (de pareja u otros)
3. **💳 Crédito Usable**: Límite autoimpuesto para tarjeta de crédito. Incluye gastos fijos (suscripciones, cuotas) y variables
4. **💸 Líquido**: Dinero disponible calculado como: `Sueldo - Ahorro - Arriendo - Crédito Período Anterior`

### 🔄 Gastos y Aportes

- **Gastos Fijos**: Se repiten en el tiempo
  - **Permanentes**: Se copian cada período hasta desactivarlos (Netflix, arriendo, gym)
  - **Temporales**: Tienen períodos definidos, se copian hasta terminar (compra en 5 cuotas)
  - Se copian automáticamente al nuevo período

- **Gastos Variables**: Únicos del período actual (compras ocasionales)
  - Registro rápido durante el mes
  - No se copian al siguiente período

- **Aportes**: Ingresos adicionales que aumentan el presupuesto
  - **Aportes Fijos**: Se copian cada período (aporte mensual de pareja)
  - **Aportes Variables**: Únicos del período (venta de artículo, reembolso)

### 📅 Manejo de Períodos Duales

- **Período Mensual**: Día 1 al último día del mes
  - Gestiona: Ahorro, Arriendo y Liquidez
  - Se crea automáticamente cada mes
  - El crédito del período anterior se paga aquí

- **Período de Crédito**: Día 25 del mes anterior al 24 del mes actual
  - Gestiona: Gastos con tarjeta de crédito
  - Funciona en paralelo con el período mensual
  - El total gastado se usa en el próximo período mensual

**Ejemplo de Flujo**:
```
Nov 25 - Dic 24: Período Crédito → Gasté $220,000
Ene 1 - Ene 31: Período Mensual → Resto $220,000 del líquido
Dic 25 - Ene 24: Período Crédito → Gasté $200,000
Feb 1 - Feb 28: Período Mensual → Resto $200,000 del líquido
```

### 📈 Reportes e Historial

- Compara períodos mes a mes
- Evolución de gastos por categoría
- Cumplimiento de metas de ahorro
- Identifica tendencias de gasto

---

## 💡 Casos de Uso

### 1. Buscar Arriendo
```
Situación: Veo departamentos de $300k, $400k y $500k
Acción: Simulo cada escenario en la app
Resultado: Veo que con $400k me queda $600k líquido, suficiente para vivir cómodamente
```

### 2. Aumentar Ahorro
```
Situación: Quiero ahorrar más para vacaciones
Acción: Subo ahorro de $200k a $300k en el simulador
Resultado: Veo que tengo que reducir crédito o arriendo para compensar
```

### 3. Control de Gastos de Crédito
```
Situación: Meta de $300k en crédito
Gastos Fijos: Netflix $20k, Spotify $10k, Juego en cuotas $5k
Acción: La app calcula "Crédito Usable Real: $265k"
Resultado: Sé exactamente cuánto puedo gastar en variables sin pasarme
```

### 4. Planificación Mensual
```
Situación: Inicio de mes, llega el sueldo
Acción: Registro el monto y defino metas por categoría
Resultado: La app me muestra si es realista o debo ajustar
```

---

## 🎨 Diseño Mobile-First

- **Responsive**: Funciona perfectamente en móvil, tablet y desktop
- **Touch-friendly**: Botones y áreas táctiles de mínimo 44x44px
- **Navbar fijo**: Navegación siempre accesible en la parte superior
- **Menú hamburguesa**: En móvil, menú lateral deslizable
- **Optimizado para iOS/Android**: Sin zooms indeseados, inputs optimizados

## 🛠️ Stack Tecnológico

### Frontend
- **Angular 17+** con Standalone Components
- **TypeScript** para type safety
- **Angular Signals** para reactividad
- **SCSS** para estilos modulares
- **RxJS** para manejo de streams

### Backend
- **FastAPI** (Python 3.11+) - API REST moderna y rápida
- **Motor** - Driver async de MongoDB
- **Pydantic** - Validación de datos
- **JWT** - Autenticación segura con tokens
- **Bcrypt** - Hashing de contraseñas

### Base de Datos
- **MongoDB** - Base de datos NoSQL flexible
- Índices optimizados para queries frecuentes
- Esquema diseñado para escalabilidad

### DevOps
- **Docker & Docker Compose** - Containerización
- **CORS** configurado para desarrollo y producción
- **Hot reload** en desarrollo

---

## 📦 Estado del Proyecto

### ✅ Completado (v0.1 - MVP Auth)
- [x] Sistema de autenticación completo (JWT)
- [x] Registro de usuarios con validaciones
- [x] Login con email o username
- [x] Guards de rutas (protección de páginas)
- [x] HTTP Interceptor para tokens automáticos
- [x] Navbar responsive mobile-first
- [x] Páginas: Login, Home, Profile
- [x] Estructura de carpetas organizada (pages, services, guards, global_components)

### ✅ Completado (v0.2 - Core Financiero - Modelos y CRUD)
- [x] Modelo de datos: Períodos (mensual y crédito)
- [x] Modelo de datos: Categorías (4 principales)
- [x] Auto-creación de períodos al primer login
- [x] CRUD de períodos (create, read, update, delete, close)
- [x] CRUD de categorías (create, read, update, delete, init defaults)
- [x] Cálculo automático de líquido (sueldo - ahorro - arriendo - crédito anterior)

### ✅ Completado (v0.2 - Endpoints API)
- [x] Endpoints de períodos (create, read, update, delete, close, get active)
- [x] Endpoints de categorías (create, read, update, delete, init defaults)
- [x] Validaciones de negocio (períodos activos, etc.)
- [x] Documentación automática (Swagger/OpenAPI)

### ✅ Completado (v0.3 - Frontend Services & Dashboard)
- [x] Period service con signals reactivos
- [x] Category service con inicialización de defaults
- [x] Dashboard principal con visualización de las 4 categorías
- [x] Indicadores en tiempo real (ahorro, arriendo, crédito, líquido)
- [x] Barras de progreso por categoría
- [x] Manejo de estados (loading, error, sin período)
- [x] Modal de configuración de período (primera vez y edición)
- [x] Campo especial para crédito anterior (solo primera vez)
- [x] Cálculo en tiempo real de liquidez en modal
- [x] Formato de moneda chileno (CLP)

### 🚧 En Desarrollo (v1.0 - Sistema Completo de Gastos y Aportes)

**Objetivo**: Implementar la lógica completa del sistema según [LOGICA_SISTEMA.md](LOGICA_SISTEMA.md)

**Backend**:
- [ ] Modelo de Gastos (fijos permanentes, fijos temporales, variables)
- [ ] Modelo de Aportes (fijos y variables)
- [ ] CRUD de Gastos con tipos y períodos restantes
- [ ] CRUD de Aportes
- [ ] Lógica de copia automática de gastos/aportes fijos
- [ ] Endpoint de desglose de categoría
- [ ] Actualización de cálculo de liquidez con nueva fórmula
- [ ] Job para cierre/apertura automática de períodos

**Frontend**:
- [ ] Vista detallada de categoría (modal con pestañas)
- [ ] Formulario de agregar gasto fijo (permanente/temporal)
- [ ] Formulario de agregar gasto variable
- [ ] Formulario de agregar aporte (fijo/variable)
- [ ] Visualización de desglose en tarjetas
- [ ] Indicador de crédito usable real (dinámico)
- [ ] Actualización de cálculos con gastos y aportes

### 📋 Roadmap Futuro

**v1.1 - Simulador Interactivo**
- [ ] Simulador de presupuesto en tiempo real
- [ ] Sliders para ajustar metas
- [ ] Visualización del impacto en líquido
- [ ] Comparación con períodos anteriores

**v1.2 - Reportes y Estadísticas**
- [ ] Comparación entre períodos
- [ ] Gráficos de evolución de gastos
- [ ] Estadísticas de cumplimiento de metas
- [ ] Proyección de próximo período
- [ ] Exportación de reportes (PDF/CSV)
- [ ] Historial completo de períodos cerrados

**v1.3 - UX Avanzada**
- [ ] Alertas inteligentes de presupuesto
- [ ] Modo oscuro
- [ ] PWA (Progressive Web App)
- [ ] Notificaciones push (recordatorios de gastos fijos)
- [ ] Onboarding mejorado para nuevos usuarios
- [ ] Tutorial interactivo

**v2.0 - Funcionalidades Avanzadas**
- [ ] Múltiples fuentes de ingreso
- [ ] Importación de movimientos bancarios
- [ ] Presupuestos compartidos (parejas/familia)
- [ ] Metas de ahorro a largo plazo con proyecciones
- [ ] Integración con APIs bancarias chilenas

---

## 📁 Estructura del Proyecto

```
emo-finance/
├── frontend/                      # Aplicación Angular
│   ├── src/app/
│   │   ├── global_components/     # Componentes reutilizables
│   │   │   └── navbar/           # Navbar responsive
│   │   ├── pages/                # Páginas de la aplicación
│   │   │   ├── login/           # Página de login
│   │   │   ├── home/            # Dashboard principal
│   │   │   └── profile/         # Perfil de usuario
│   │   ├── services/            # Servicios y lógica de negocio
│   │   │   ├── auth.service.ts         # Autenticación
│   │   │   └── auth.interceptor.ts     # Interceptor HTTP
│   │   └── guards/              # Guards de rutas
│   │       └── auth.guard.ts           # Protección de rutas
│   └── src/styles.scss          # Estilos globales mobile-first
│
├── backend/                      # API FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/    # Endpoints de la API
│   │   │   ├── auth.py         # Autenticación (login/register)
│   │   │   ├── periods.py      # Gestión de períodos
│   │   │   ├── categories.py   # Gestión de categorías
│   │   │   ├── expenses.py     # Gestión de gastos (fijos/variables) [PRÓXIMAMENTE]
│   │   │   └── aportes.py      # Gestión de aportes [PRÓXIMAMENTE]
│   │   ├── core/               # Configuración y utilidades
│   │   │   ├── config.py       # Variables de entorno
│   │   │   ├── database.py     # Conexión a MongoDB
│   │   │   └── security.py     # JWT, hashing
│   │   ├── crud/               # Operaciones de base de datos
│   │   │   ├── user.py
│   │   │   ├── period.py       # CRUD de períodos
│   │   │   ├── category.py     # CRUD de categorías
│   │   │   ├── expense.py      # CRUD de gastos [PRÓXIMAMENTE]
│   │   │   └── aporte.py       # CRUD de aportes [PRÓXIMAMENTE]
│   │   ├── models/             # Modelos Pydantic
│   │   │   ├── user.py
│   │   │   ├── period.py       # Modelo de períodos
│   │   │   ├── category.py     # Modelo de categorías
│   │   │   ├── expense.py      # Modelo de gastos [PRÓXIMAMENTE]
│   │   │   └── aporte.py       # Modelo de aportes [PRÓXIMAMENTE]
│   │   └── schemas/            # Schemas de request/response
│   │       └── auth.py
│   └── requirements.txt
│
├── LOGICA_SISTEMA.md            # 🧠 Lógica completa del sistema (REFERENCIA PRINCIPAL)
├── PRODUCT_SPEC.md              # Especificación del producto (legacy)
├── docker-compose.yml           # Orquestación de contenedores
└── README.md
```

---

## 🚀 Instalación y Uso

### Requisitos Previos

- **Docker** y **Docker Compose**
- **Node.js 18+** (para desarrollo local del frontend)
- **Python 3.11+** (para desarrollo local del backend)
- **MongoDB** (incluido en Docker Compose)

### Usando Docker Compose (Recomendado)

```bash
# Clonar el repositorio
git clone <repository-url>
cd emo-finance

# Levantar todos los servicios
docker-compose up -d

# La aplicación estará disponible en:
# Frontend: http://localhost:4200
# Backend API: http://localhost:8000
# Documentación API: http://localhost:8000/docs
```

### Desarrollo Local

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
ng serve
```

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# MongoDB
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=emo_finance

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Backend
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=4200
```

---

## 📚 Documentación Adicional

- **[LOGICA_SISTEMA.md](LOGICA_SISTEMA.md)**: 🧠 **DOCUMENTO PRINCIPAL** - Lógica completa del sistema
  - Explicación detallada de las 4 categorías
  - Sistema de gastos (fijos permanentes, temporales, variables)
  - Sistema de aportes (fijos y variables)
  - Flujo de períodos duales (mensual + crédito)
  - Fórmulas y cálculos
  - Modelo de datos completo
  - Checklist de implementación para v1.0

- **[PRODUCT_SPEC.md](PRODUCT_SPEC.md)**: Especificación del producto (legacy)
  - Referencia histórica del diseño inicial
  - Algunas secciones pueden estar desactualizadas

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Este es un proyecto en desarrollo activo.

### Cómo Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Áreas de Contribución

- **Backend**: Implementación de modelos de períodos, gastos y categorías
- **Frontend**: Componentes de dashboard, simulador de presupuesto
- **UX/UI**: Mejoras de diseño mobile-first
- **Testing**: Tests unitarios e integración
- **Documentación**: Mejoras al README y documentación técnica

---

## 📝 Licencia

MIT License - ver archivo LICENSE para más detalles

---

## 👨‍💻 Autor

Desarrollado con ☕ para resolver un problema real de gestión financiera personal.

---

## 🙏 Agradecimientos

- Inspirado en la necesidad de entender **cuánto puedo gastar** en lugar de solo ver **cuánto gasté**
- Diseñado para ser simple, intuitivo y mobile-first
- Construido con tecnologías modernas y escalables