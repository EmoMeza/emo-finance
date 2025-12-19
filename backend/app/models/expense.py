from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from enum import Enum
from app.models.common import PyObjectId


class TipoGasto(str, Enum):
    """
    Tipo de gasto según LOGICA_SISTEMA.md

    FIJO: Gastos que se repiten en el tiempo
    - Permanentes: Se copian automáticamente cada período (ej: Netflix, Spotify)
    - Temporales: Tienen número de períodos definidos (ej: compra en 5 cuotas)

    VARIABLE: Gastos únicos del período, no se copian (ej: pizza, regalo)
    """
    FIJO = "fijo"
    VARIABLE = "variable"


class ExpenseBase(BaseModel):
    """
    Modelo base de Expense según LOGICA_SISTEMA.md

    Campos principales:
    - nombre: Descripción del gasto
    - monto: Valor del gasto (siempre positivo)
    - categoria_id: A qué categoría pertenece (ahorro, arriendo, credito, liquidez)
    - tipo: Si es fijo o variable
    - es_permanente: Solo para gastos fijos (true = se copia siempre, false = temporal con cuotas)
    - periodos_restantes: Solo para gastos fijos temporales (ej: 3 cuotas restantes de 5)
    - descripcion: Notas adicionales opcionales
    """
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre/descripción del gasto")
    monto: float = Field(..., gt=0, description="Monto del gasto (siempre positivo)")
    categoria_id: PyObjectId = Field(..., description="ID de la categoría a la que pertenece")
    tipo: TipoGasto = Field(..., description="Tipo de gasto: fijo o variable")

    # Campos específicos para gastos fijos
    es_permanente: Optional[bool] = Field(
        default=None,
        description="Solo para gastos fijos: true = permanente (Netflix), false = temporal (cuotas)"
    )
    periodos_restantes: Optional[int] = Field(
        default=None,
        ge=0,
        description="Solo para gastos fijos temporales: número de períodos que faltan (ej: 3/5 cuotas)"
    )

    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Notas adicionales sobre el gasto"
    )

    @field_validator('es_permanente', 'periodos_restantes')
    @classmethod
    def validate_fixed_expense_fields(cls, v, info):
        """
        Validar que es_permanente y periodos_restantes solo se usen con gastos fijos
        """
        if info.data.get('tipo') == TipoGasto.VARIABLE and v is not None:
            raise ValueError(f"{info.field_name} solo aplica para gastos fijos")
        return v

    @field_validator('periodos_restantes')
    @classmethod
    def validate_periodos_restantes(cls, v, info):
        """
        Validar lógica de periodos_restantes:
        - Si es_permanente = true, periodos_restantes debe ser None
        - Si es_permanente = false, periodos_restantes debe ser >= 0
        """
        if info.data.get('tipo') == TipoGasto.FIJO:
            es_permanente = info.data.get('es_permanente')
            if es_permanente is True and v is not None:
                raise ValueError("Gastos permanentes no deben tener periodos_restantes")
            if es_permanente is False and v is None:
                raise ValueError("Gastos temporales deben tener periodos_restantes definido")
        return v


class ExpenseCreate(ExpenseBase):
    """
    Esquema para crear un nuevo gasto
    """
    pass


class ExpenseUpdate(BaseModel):
    """
    Esquema para actualizar un gasto
    Permite editar nombre, monto, descripción
    """
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    monto: Optional[float] = Field(default=None, gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=500)

    # No se permite cambiar tipo, es_permanente, periodos_restantes después de crear
    # Solo se decrementan periodos_restantes automáticamente al copiar


class ExpenseInDB(ExpenseBase):
    """
    Modelo completo del gasto en MongoDB
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
            "example_variable": {
                "user_id": "507f1f77bcf86cd799439011",
                "periodo_id": "507f1f77bcf86cd799439012",
                "categoria_id": "507f1f77bcf86cd799439013",
                "nombre": "Pizza del viernes",
                "monto": 15000,
                "tipo": "variable",
                "descripcion": "Cena con amigos"
            },
            "example_fijo_permanente": {
                "user_id": "507f1f77bcf86cd799439011",
                "periodo_id": "507f1f77bcf86cd799439012",
                "categoria_id": "507f1f77bcf86cd799439013",
                "nombre": "Netflix",
                "monto": 20000,
                "tipo": "fijo",
                "es_permanente": True,
                "descripcion": "Suscripción mensual"
            },
            "example_fijo_temporal": {
                "user_id": "507f1f77bcf86cd799439011",
                "periodo_id": "507f1f77bcf86cd799439012",
                "categoria_id": "507f1f77bcf86cd799439013",
                "nombre": "Juego en cuotas",
                "monto": 5000,
                "tipo": "fijo",
                "es_permanente": False,
                "periodos_restantes": 3,
                "descripcion": "Cuota 3 de 5"
            }
        }


class ExpenseResponse(BaseModel):
    """
    Esquema de respuesta para endpoints de API
    """
    id: str = Field(alias="_id")
    user_id: str
    periodo_id: str
    categoria_id: str
    nombre: str
    monto: float
    tipo: TipoGasto
    es_permanente: Optional[bool]
    periodos_restantes: Optional[int]
    descripcion: Optional[str]
    fecha_registro: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
