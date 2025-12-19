from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum


class TipoPeriodo(str, Enum):
    MENSUAL_ESTANDAR = "mensual_estandar"
    CICLO_CREDITO = "ciclo_credito"


class EstadoPeriodo(str, Enum):
    ACTIVO = "activo"
    CERRADO = "cerrado"
    PROYECTADO = "proyectado"


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ], serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class MetasCategorias(BaseModel):
    """Metas de asignación por categoría"""
    ahorro: float = Field(..., ge=0, description="Meta de ahorro mensual")
    arriendo: float = Field(..., ge=0, description="Presupuesto para arriendo y gastos de vivienda")
    credito_usable: float = Field(..., ge=0, description="Límite autoimpuesto de crédito")

    @field_validator('ahorro', 'arriendo', 'credito_usable')
    @classmethod
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError('El monto debe ser mayor o igual a 0')
        return v


class PeriodBase(BaseModel):
    tipo_periodo: TipoPeriodo = Field(..., description="Tipo de período (mensual o ciclo crédito)")
    fecha_inicio: datetime = Field(..., description="Fecha de inicio del período")
    fecha_fin: datetime = Field(..., description="Fecha de fin del período")
    sueldo: float = Field(..., ge=0, description="Sueldo o ingreso total del período")
    metas_categorias: MetasCategorias = Field(..., description="Metas de asignación por categoría")
    estado: EstadoPeriodo = Field(default=EstadoPeriodo.ACTIVO, description="Estado del período")
    total_gastado: float = Field(default=0, ge=0, description="Total gastado en este período (usado para períodos de crédito)")

    @field_validator('fecha_fin')
    @classmethod
    def validate_dates(cls, v, info):
        if 'fecha_inicio' in info.data and v <= info.data['fecha_inicio']:
            raise ValueError('fecha_fin debe ser posterior a fecha_inicio')
        return v


class PeriodCreate(PeriodBase):
    """Schema para crear un período"""
    pass


class PeriodUpdate(BaseModel):
    """Schema para actualizar un período"""
    sueldo: Optional[float] = Field(None, gt=0)
    metas_categorias: Optional[MetasCategorias] = None
    estado: Optional[EstadoPeriodo] = None
    total_gastado: Optional[float] = Field(None, ge=0)

    @field_validator('sueldo')
    @classmethod
    def validate_sueldo_update(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El sueldo debe ser mayor a 0 al actualizar')
        return v


class PeriodInDB(PeriodBase):
    """Modelo de período en la base de datos"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="ID del usuario propietario")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class PeriodResponse(BaseModel):
    """Schema de respuesta de período"""
    id: str = Field(alias="_id")
    user_id: str
    tipo_periodo: TipoPeriodo
    fecha_inicio: datetime
    fecha_fin: datetime
    sueldo: float
    metas_categorias: MetasCategorias
    estado: EstadoPeriodo
    total_gastado: float = Field(default=0, description="Total gastado en este período")
    liquido_calculado: float = Field(..., description="Líquido calculado automáticamente")
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True
    }


class PeriodSummary(BaseModel):
    """Resumen de un período con estadísticas"""
    id: str = Field(alias="_id")
    tipo_periodo: TipoPeriodo
    fecha_inicio: datetime
    fecha_fin: datetime
    sueldo: float
    metas_categorias: MetasCategorias
    liquido_calculado: float
    estado: EstadoPeriodo

    # Estadísticas
    total_gastado: float = Field(default=0)
    gasto_por_categoria: Dict[str, float] = Field(default_factory=dict)
    porcentaje_cumplimiento: Dict[str, float] = Field(default_factory=dict)
    dias_restantes: int = Field(default=0)

    model_config = {
        "populate_by_name": True
    }
