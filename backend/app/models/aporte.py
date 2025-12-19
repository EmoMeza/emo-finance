from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.common import PyObjectId


class AporteBase(BaseModel):
    """
    Modelo base de Aporte según LOGICA_SISTEMA.md

    Los aportes son ingresos adicionales que aumentan el presupuesto disponible
    de una categoría. Son montos POSITIVOS que se RESTAN del total de gastos.

    Fórmula de categoría: total_categoria = gastos_fijos + gastos_variables - aportes

    Ejemplos:
    - Aporte de pareja para arriendo: $170,000 (reduce el total real de arriendo)
    - Venta de celular usado: $100,000 (aumenta liquidez disponible)
    - Reembolso de un gasto: $20,000
    - Ingreso extra de trabajo secundario: $100,000

    Tipos:
    - Fijo: Se copia automáticamente cada período (ej: aporte mensual de pareja)
    - Variable: Se registra una sola vez en el período actual (ej: venta de celular)
    """
    nombre: str = Field(..., min_length=1, max_length=200, description="Descripción del aporte")
    monto: float = Field(..., gt=0, description="Monto del aporte (siempre positivo)")
    categoria_id: PyObjectId = Field(..., description="ID de la categoría a la que se aporta")
    es_fijo: bool = Field(
        ...,
        description="true = se copia cada período (aporte mensual), false = único del período (venta ocasional)"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Notas adicionales sobre el aporte"
    )


class AporteCreate(AporteBase):
    """
    Esquema para crear un nuevo aporte
    """
    pass


class AporteUpdate(BaseModel):
    """
    Esquema para actualizar un aporte
    Permite editar nombre, monto, descripción
    """
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    monto: Optional[float] = Field(default=None, gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=500)

    # No se permite cambiar es_fijo después de crear


class AporteInDB(AporteBase):
    """
    Modelo completo del aporte en MongoDB
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    periodo_id: PyObjectId = Field(..., description="ID del período al que pertenece")
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example_fijo": {
                "user_id": "507f1f77bcf86cd799439011",
                "periodo_id": "507f1f77bcf86cd799439012",
                "categoria_id": "507f1f77bcf86cd799439013",
                "nombre": "Aporte pareja para arriendo",
                "monto": 170000,
                "es_fijo": True,
                "descripcion": "Aporte mensual para gastos de vivienda"
            },
            "example_variable": {
                "user_id": "507f1f77bcf86cd799439011",
                "periodo_id": "507f1f77bcf86cd799439012",
                "categoria_id": "507f1f77bcf86cd799439014",
                "nombre": "Venta celular usado",
                "monto": 100000,
                "es_fijo": False,
                "descripcion": "Venta única, no se repite"
            }
        }


class AporteResponse(BaseModel):
    """
    Esquema de respuesta para endpoints de API
    """
    id: str = Field(alias="_id")
    user_id: str
    periodo_id: str
    categoria_id: str
    nombre: str
    monto: float
    es_fijo: bool
    descripcion: Optional[str]
    fecha_registro: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
