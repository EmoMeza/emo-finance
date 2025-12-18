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

1. **💵 Ahorro**: Cuánto quieres ahorrar cada mes
2. **🏠 Arriendo**: Presupuesto para vivienda (arriendo, luz, agua, gas, internet)
3. **💳 Crédito Usable**: Límite autoimpuesto para tarjeta de crédito
4. **💸 Líquido**: Dinero disponible en efectivo/transferencia (calculado automáticamente)

### 🔄 Gastos Fijos y Variables

- **Gastos Fijos**: Se repiten cada mes (Netflix, arriendo, gym)
  - Se generan automáticamente al inicio del período
  - Edita el valor del mes sin afectar la plantilla

- **Gastos Variables**: Únicos del período (compras ocasionales)
  - Registro rápido y simple
  - Se descuentan al instante de tu presupuesto

### 📅 Manejo de Períodos Especiales

- **Período Mensual**: 1-31 de cada mes (para arriendo, ahorro, líquido)
- **Período de Crédito**: 25 del mes anterior - 24 del mes actual
- Ambos funcionan en paralelo automáticamente

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
Situación: Meta de $300k en crédito, gastos fijos son $50k (suscripciones)
Acción: La app muestra "Disponible: $250k"
Resultado: Sé exactamente cuánto puedo gastar sin pasarme
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
- [x] Modelo de datos: Períodos
- [x] Modelo de datos: Categorías
- [x] Modelo de datos: Gastos
- [x] Modelo de datos: Plantillas de gastos fijos
- [x] CRUD de períodos (create, read, update, delete, close)
- [x] CRUD de categorías (create, read, update, delete, init defaults)
- [x] CRUD de gastos (create, read, update, delete, mark as paid)
- [x] CRUD de plantillas (create, read, update, delete, toggle)
- [x] Cálculo automático de líquido

### ✅ Completado (v0.2 - Endpoints API)
- [x] Endpoints de períodos (create, read, update, delete, close, get active)
- [x] Endpoints de categorías (create, read, update, delete, init defaults)
- [x] Endpoints de gastos (create, read, update, delete, mark as paid)
- [x] Endpoints de plantillas (create, read, update, delete, toggle)
- [x] Validaciones de negocio (suma de metas, períodos activos, etc.)
- [x] Documentación automática (Swagger/OpenAPI)

### ✅ Completado (v0.3 - Frontend Services & Dashboard)
- [x] Period service con signals reactivos
- [x] Category service con inicialización de defaults
- [x] Expense service con filtros y cálculos
- [x] ExpenseTemplate service con toggle activo/inactivo
- [x] Dashboard principal con visualización de las 4 categorías
- [x] Indicadores en tiempo real (ahorro, arriendo, crédito, líquido)
- [x] Barras de progreso por categoría
- [x] Manejo de estados (loading, error, sin período)
- [x] Formato de moneda chileno (CLP)

### 🚧 En Desarrollo (v0.4 - CRUD Components)
- [ ] Componente de creación de períodos
- [ ] Componente de registro de gastos
- [ ] Componente de gestión de plantillas
- [ ] Simulador de presupuesto interactivo
- [ ] Integración completa end-to-end

### 📋 Roadmap Futuro

**v0.3 - Gastos Fijos**
- [ ] CRUD de plantillas de gastos recurrentes
- [ ] Generación automática al inicio de período
- [ ] Edición de gastos sin afectar plantilla
- [ ] Vista de calendario de recurrentes

**v0.4 - Simulador**
- [ ] Simulador interactivo de presupuesto
- [ ] Sliders para ajustar metas en tiempo real
- [ ] Visualización del impacto en líquido
- [ ] Comparación con períodos anteriores
- [ ] Sugerencias basadas en historial

**v0.5 - Reportes**
- [ ] Comparación entre períodos
- [ ] Gráficos de evolución de gastos
- [ ] Estadísticas de cumplimiento de metas
- [ ] Proyección de próximo período
- [ ] Exportación de reportes (PDF/CSV)

**v0.6 - UX Avanzada**
- [ ] Alertas inteligentes de presupuesto
- [ ] Modo oscuro
- [ ] PWA (Progressive Web App)
- [ ] Notificaciones push
- [ ] Onboarding para nuevos usuarios

**v1.0 - Funcionalidades Avanzadas**
- [ ] Múltiples cuentas bancarias
- [ ] Importación de movimientos bancarios
- [ ] Presupuestos compartidos (parejas/familia)
- [ ] Metas de ahorro a largo plazo
- [ ] Integración con APIs bancarias

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
│   │   │   ├── expenses.py     # Gestión de gastos
│   │   │   └── expense_templates.py  # Plantillas de gastos fijos
│   │   ├── core/               # Configuración y utilidades
│   │   │   ├── config.py       # Variables de entorno
│   │   │   ├── database.py     # Conexión a MongoDB
│   │   │   └── security.py     # JWT, hashing
│   │   ├── crud/               # Operaciones de base de datos
│   │   │   ├── user.py
│   │   │   ├── period.py       # CRUD de períodos
│   │   │   ├── category.py     # CRUD de categorías
│   │   │   ├── expense.py      # CRUD de gastos
│   │   │   └── expense_template.py  # CRUD de plantillas
│   │   ├── models/             # Modelos Pydantic
│   │   │   ├── user.py
│   │   │   ├── period.py       # Modelo de períodos
│   │   │   ├── category.py     # Modelo de categorías
│   │   │   ├── expense.py      # Modelo de gastos
│   │   │   └── expense_template.py  # Modelo de plantillas
│   │   └── schemas/            # Schemas de request/response
│   │       └── auth.py
│   └── requirements.txt
│
├── PRODUCT_SPEC.md              # Especificación completa del producto
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

- **[PRODUCT_SPEC.md](PRODUCT_SPEC.md)**: Especificación completa del producto
  - Modelo de datos detallado
  - Endpoints de API propuestos
  - Reglas de negocio
  - Roadmap de desarrollo
  - Consideraciones técnicas

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