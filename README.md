# Emo Finance WIP

Aplicación web de gestión de finanzas personales construida con Angular y FastAPI.

## Descripción

Emo Finance es una aplicación full-stack para el seguimiento y control de finanzas personales. Permite a los usuarios registrar sus ingresos y gastos, categorizarlos, y obtener una visión clara de su situación financiera.

## Stack Tecnológico

- **Frontend:** Angular (TypeScript)
- **Backend:** FastAPI (Python)
- **Base de Datos:** MongoDB
- **Containerización:** Docker & Docker Compose

## Características

### Versión Actual (v1.0)
- Sistema de autenticación de usuarios (registro/login con JWT)
- Gestión de usuarios
- Registro de ingresos y gastos
- Categorización de transacciones

### Roadmap Futuro
- Presupuestos mensuales por categoría
- Metas de ahorro
- Reportes y visualización de datos con gráficas
- Dashboard con estadísticas en tiempo real
- Exportación de datos (CSV, PDF)

## Estructura del Proyecto

```
emo-finance/
├── frontend/          # Aplicación Angular
├── backend/           # API FastAPI
├── docker-compose.yml # Orquestación de contenedores
└── README.md
```

## Requisitos Previos

- Docker
- Docker Compose
- Node.js (para desarrollo local del frontend)
- Python 3.11+ (para desarrollo local del backend)

## Instalación y Uso

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

## Variables de Entorno

Crear archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# MongoDB
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=emo_finance

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Backend
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=4200
```

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios que te gustaría realizar.

## Licencia

[Especificar licencia]

## Autor

[Tu nombre/organización]