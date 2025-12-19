from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum
from app.models.common import PyObjectId


class TipoPeriodo(str, Enum):
    """
    Tipo de período según LOGICA_SISTEMA.md
    - MENSUAL_ESTANDAR: Del 1 al último día del mes (gestión de Ahorro, Arriendo, Liquidez)
    - CICLO_CREDITO: Del 25 al 24 (gestión de Crédito Usable)
    """
    MENSUAL_ESTANDAR = "mensual_estandar"
    CICLO_CREDITO = "ciclo_credito"


class EstadoPeriodo(str, Enum):
    """
    Estado del período
    - ACTIVO: Período actual en uso
    - CERRADO: Período finalizado (se mantiene para historial)
    - PROYECTADO: Período futuro para simulaciones (opcional)
    """
    ACTIVO = "activo"
    CERRADO = "cerrado"
    PROYECTADO = "proyectado"


class MetasCategorias(BaseModel):
    """
    Metas/presupuestos para cada categoría
    Según LOGICA_SISTEMA.md:
    - ahorro: Meta mensual de ahorro
    - arriendo: Presupuesto para vivienda
    - credito_usable: Meta de crédito total del período
    """
    ahorro: float = Field(default=0, ge=0, description="Meta mensual de ahorro")
    arriendo: float = Field(default=0, ge=0, description="Presupuesto para arriendo y gastos relacionados")
    credito_usable: float = Field(default=0, ge=0, description="Meta de crédito total del período")


class PeriodBase(BaseModel):
    """
    Modelo base de Period según LOGICA_SISTEMA.md
    """
    tipo_periodo: TipoPeriodo
    fecha_inicio: datetime
    fecha_fin: datetime
    sueldo: Optional[float] = Field(default=0, ge=0, description="Ingreso mensual (solo para períodos mensuales)")
    metas_categorias: MetasCategorias = Field(default_factory=MetasCategorias)
    estado: EstadoPeriodo = EstadoPeriodo.ACTIVO

    # Solo para períodos de crédito
    total_gastado: Optional[float] = Field(
        default=0,
        ge=0,
        description="Suma total de gastos del período de crédito (se usa como deuda en siguiente período mensual)"
    )


class PeriodCreate(PeriodBase):
    """Esquema para crear un nuevo período"""
    pass


class PeriodUpdate(BaseModel):
    """
    Esquema para actualizar un período
    Permite editar sueldo, metas y estado
    """
    sueldo: Optional[float] = Field(default=None, ge=0)
    metas_categorias: Optional[MetasCategorias] = None
    estado: Optional[EstadoPeriodo] = None
    total_gastado: Optional[float] = Field(default=None, ge=0)


class PeriodInDB(PeriodBase):
    """
    Modelo completo del período en MongoDB
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "tipo_periodo": "mensual_estandar",
                "fecha_inicio": "2025-01-01T00:00:00",
                "fecha_fin": "2025-01-31T23:59:59",
                "sueldo": 1000000,
                "metas_categorias": {
                    "ahorro": 250000,
                    "arriendo": 450000,
                    "credito_usable": 200000
                },
                "estado": "activo",
                "total_gastado": 0
            }
        }


class PeriodResponse(BaseModel):
    """
    Esquema de respuesta para endpoints de API
    """
    id: str = Field(alias="_id")
    user_id: str
    tipo_periodo: TipoPeriodo
    fecha_inicio: datetime
    fecha_fin: datetime
    sueldo: float
    metas_categorias: MetasCategorias
    estado: EstadoPeriodo
    total_gastado: float
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
