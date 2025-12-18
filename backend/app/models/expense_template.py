from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from .expense import MetodoPago


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


class ExpenseTemplateBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    valor: float = Field(..., gt=0, description="Monto del gasto fijo")
    categoria_id: str = Field(..., description="ID de la categoría")
    subcategoria_nombre: Optional[str] = Field(None, max_length=100)
    dia_cargo: int = Field(..., ge=1, le=31, description="Día del mes en que se cobra")
    metodo_pago: MetodoPago = Field(..., description="Método de pago utilizado")
    activa: bool = Field(default=True, description="Si la plantilla está activa")
    notas: Optional[str] = Field(None, max_length=500)

    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v):
        if v <= 0:
            raise ValueError('El valor debe ser mayor a 0')
        return round(v, 2)

    @field_validator('dia_cargo')
    @classmethod
    def validate_dia(cls, v):
        if v < 1 or v > 31:
            raise ValueError('El día debe estar entre 1 y 31')
        return v


class ExpenseTemplateCreate(ExpenseTemplateBase):
    """Schema para crear una plantilla de gasto fijo"""
    pass


class ExpenseTemplateUpdate(BaseModel):
    """Schema para actualizar una plantilla de gasto fijo"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    valor: Optional[float] = Field(None, gt=0)
    subcategoria_nombre: Optional[str] = Field(None, max_length=100)
    dia_cargo: Optional[int] = Field(None, ge=1, le=31)
    metodo_pago: Optional[MetodoPago] = None
    activa: Optional[bool] = None
    notas: Optional[str] = Field(None, max_length=500)

    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El valor debe ser mayor a 0')
        return round(v, 2) if v else v

    @field_validator('dia_cargo')
    @classmethod
    def validate_dia(cls, v):
        if v is not None and (v < 1 or v > 31):
            raise ValueError('El día debe estar entre 1 y 31')
        return v


class ExpenseTemplateInDB(ExpenseTemplateBase):
    """Modelo de plantilla en la base de datos"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="ID del usuario propietario")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class ExpenseTemplateResponse(BaseModel):
    """Schema de respuesta de plantilla"""
    id: str = Field(alias="_id")
    user_id: str
    nombre: str
    valor: float
    categoria_id: str
    subcategoria_nombre: Optional[str]
    dia_cargo: int
    metodo_pago: MetodoPago
    activa: bool
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "nombre": "Netflix",
                "valor": 9990,
                "categoria_id": "507f1f77bcf86cd799439013",
                "subcategoria_nombre": "Suscripciones",
                "dia_cargo": 15,
                "metodo_pago": "credito",
                "activa": True,
                "notas": "Plan estándar",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    }
