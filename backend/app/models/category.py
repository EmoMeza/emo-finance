from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum
from app.models.common import PyObjectId


class TipoCategoria(str, Enum):
    """
    Las 4 categorías principales según LOGICA_SISTEMA.md
    """
    AHORRO = "ahorro"
    ARRIENDO = "arriendo"
    CREDITO = "credito"
    LIQUIDEZ = "liquidez"


class CategoryBase(BaseModel):
    """
    Modelo base de Category según LOGICA_SISTEMA.md

    Las 4 categorías son fijas del sistema:
    1. 💵 Ahorro - Dinero destinado a ser ahorrado
    2. 🏠 Arriendo - Presupuesto para vivienda y gastos relacionados
    3. 💳 Crédito Usable - Límite autoimpuesto para gastos con tarjeta
    4. 💸 Liquidez - Dinero disponible en efectivo (calculado automáticamente)
    """
    nombre: str = Field(..., description="Nombre de la categoría")
    slug: TipoCategoria = Field(..., description="Identificador único de la categoría")
    icono: str = Field(..., description="Emoji representativo")
    color: str = Field(..., description="Color en formato hex")
    tiene_meta: bool = Field(
        ...,
        description="Indica si la categoría tiene meta definida (true para ahorro/arriendo/credito, false para liquidez)"
    )
    descripcion: Optional[str] = Field(
        default=None,
        description="Descripción del propósito de la categoría"
    )


class CategoryCreate(CategoryBase):
    """Esquema para crear una nueva categoría"""
    pass


class CategoryUpdate(BaseModel):
    """
    Esquema para actualizar una categoría
    Solo permite editar nombre, icono, color y descripción
    """
    nombre: Optional[str] = None
    icono: Optional[str] = None
    color: Optional[str] = None
    descripcion: Optional[str] = None


class CategoryInDB(CategoryBase):
    """
    Modelo completo de la categoría en MongoDB
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
                "nombre": "Ahorro",
                "slug": "ahorro",
                "icono": "💵",
                "color": "#10b981",
                "tiene_meta": True,
                "descripcion": "Dinero destinado a ser ahorrado mensualmente"
            }
        }


class CategoryResponse(BaseModel):
    """
    Esquema de respuesta para endpoints de API
    """
    id: str = Field(alias="_id")
    user_id: str
    nombre: str
    slug: TipoCategoria
    icono: str
    color: str
    tiene_meta: bool
    descripcion: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# Datos por defecto de las 4 categorías según LOGICA_SISTEMA.md
DEFAULT_CATEGORIES = [
    {
        "nombre": "Ahorro",
        "slug": TipoCategoria.AHORRO,
        "icono": "💵",
        "color": "#10b981",
        "tiene_meta": True,
        "descripcion": "Dinero destinado a ser ahorrado mensualmente"
    },
    {
        "nombre": "Arriendo",
        "slug": TipoCategoria.ARRIENDO,
        "icono": "🏠",
        "color": "#f59e0b",
        "tiene_meta": True,
        "descripcion": "Presupuesto para vivienda y gastos relacionados"
    },
    {
        "nombre": "Crédito Usable",
        "slug": TipoCategoria.CREDITO,
        "icono": "💳",
        "color": "#3b82f6",
        "tiene_meta": True,
        "descripcion": "Límite autoimpuesto para gastos con tarjeta de crédito"
    },
    {
        "nombre": "Liquidez",
        "slug": TipoCategoria.LIQUIDEZ,
        "icono": "💸",
        "color": "#8b5cf6",
        "tiene_meta": False,
        "descripcion": "Dinero disponible en efectivo o transferencia (calculado automáticamente)"
    }
]
