from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
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


class TipoCategoria(str, Enum):
    AHORRO = "ahorro"
    ARRIENDO = "arriendo"
    CREDITO = "credito"
    LIQUIDO = "liquido"


class Subcategoria(BaseModel):
    """Subcategoría dentro de una categoría principal"""
    nombre: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, pattern="^#[0-9A-Fa-f]{6}$")
    descripcion: Optional[str] = Field(default=None, max_length=200)


class CategoryBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    tipo: TipoCategoria = Field(..., description="Tipo de categoría principal")
    color: str = Field(default="#667eea", pattern="^#[0-9A-Fa-f]{6}$")
    icono: Optional[str] = Field(default=None, max_length=10)
    subcategorias: List[Subcategoria] = Field(default_factory=list)


class CategoryCreate(CategoryBase):
    """Schema para crear una categoría"""
    pass


class CategoryUpdate(BaseModel):
    """Schema para actualizar una categoría"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icono: Optional[str] = Field(None, max_length=10)
    subcategorias: Optional[List[Subcategoria]] = None


class CategoryInDB(CategoryBase):
    """Modelo de categoría en la base de datos"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="ID del usuario propietario")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class CategoryResponse(BaseModel):
    """Schema de respuesta de categoría"""
    id: str = Field(alias="_id")
    user_id: str
    nombre: str
    tipo: TipoCategoria
    color: str
    icono: Optional[str]
    subcategorias: List[Subcategoria]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "nombre": "Arriendo",
                "tipo": "arriendo",
                "color": "#667eea",
                "icono": "🏠",
                "subcategorias": [
                    {
                        "nombre": "Arriendo Base",
                        "color": "#764ba2",
                        "descripcion": "Pago mensual de arriendo"
                    },
                    {
                        "nombre": "Luz",
                        "color": "#f6ad55",
                        "descripcion": "Cuenta de luz"
                    }
                ],
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
        }
    }
