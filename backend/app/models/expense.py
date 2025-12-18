from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum


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


class TipoGasto(str, Enum):
    FIJO = "fijo"
    VARIABLE = "variable"


class EstadoGasto(str, Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    PROYECTADO = "proyectado"


class MetodoPago(str, Enum):
    CREDITO = "credito"
    DEBITO = "debito"
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"


class ExpenseBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    valor: float = Field(..., gt=0, description="Monto del gasto")
    fecha: datetime = Field(..., description="Fecha del gasto")
    categoria_id: str = Field(..., description="ID de la categoría")
    subcategoria_nombre: Optional[str] = Field(None, max_length=100)
    tipo: TipoGasto = Field(..., description="Tipo de gasto (fijo o variable)")
    metodo_pago: MetodoPago = Field(..., description="Método de pago utilizado")
    estado: EstadoGasto = Field(default=EstadoGasto.PENDIENTE)
    notas: Optional[str] = Field(None, max_length=500)

    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v):
        if v <= 0:
            raise ValueError('El valor debe ser mayor a 0')
        return round(v, 2)


class ExpenseCreate(ExpenseBase):
    """Schema para crear un gasto"""
    periodo_id: str = Field(..., description="ID del período al que pertenece")
    plantilla_id: Optional[str] = Field(None, description="ID de la plantilla (si es gasto fijo)")


class ExpenseUpdate(BaseModel):
    """Schema para actualizar un gasto"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    valor: Optional[float] = Field(None, gt=0)
    fecha: Optional[datetime] = None
    subcategoria_nombre: Optional[str] = Field(None, max_length=100)
    metodo_pago: Optional[MetodoPago] = None
    estado: Optional[EstadoGasto] = None
    notas: Optional[str] = Field(None, max_length=500)

    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El valor debe ser mayor a 0')
        return round(v, 2) if v else v


class ExpenseInDB(ExpenseBase):
    """Modelo de gasto en la base de datos"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="ID del usuario propietario")
    periodo_id: PyObjectId = Field(..., description="ID del período")
    plantilla_id: Optional[PyObjectId] = Field(None, description="ID de plantilla si es gasto fijo")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class ExpenseResponse(BaseModel):
    """Schema de respuesta de gasto"""
    id: str = Field(alias="_id")
    user_id: str
    periodo_id: str
    plantilla_id: Optional[str] = None
    nombre: str
    valor: float
    fecha: datetime
    categoria_id: str
    subcategoria_nombre: Optional[str]
    tipo: TipoGasto
    metodo_pago: MetodoPago
    estado: EstadoGasto
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "periodo_id": "507f1f77bcf86cd799439013",
                "plantilla_id": None,
                "nombre": "Supermercado",
                "valor": 45000,
                "fecha": "2025-01-15T10:30:00",
                "categoria_id": "507f1f77bcf86cd799439014",
                "subcategoria_nombre": "Comida",
                "tipo": "variable",
                "metodo_pago": "debito",
                "estado": "pagado",
                "notas": "Compra mensual",
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T10:30:00"
            }
        }
    }
