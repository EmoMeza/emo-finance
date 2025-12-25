from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.aporte import (
    AporteCreate,
    AporteUpdate,
    AporteInDB
)


class AporteCRUD:
    """
    CRUD operations para Aportes según LOGICA_SISTEMA.md

    Los aportes son ingresos adicionales que se RESTAN del total de gastos
    de una categoría, aumentando el presupuesto disponible.

    Fórmula: total_categoria = gastos - aportes
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["aportes"]

    async def create(self, user_id: str, periodo_id: str, aporte: AporteCreate) -> AporteInDB:
        """
        Crear un nuevo aporte
        """
        aporte_dict = aporte.model_dump(exclude_none=True)
        aporte_dict["user_id"] = ObjectId(user_id)
        aporte_dict["periodo_id"] = ObjectId(periodo_id)
        aporte_dict["fecha_registro"] = datetime.utcnow()
        aporte_dict["created_at"] = datetime.utcnow()
        aporte_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(aporte_dict)
        aporte_dict["_id"] = result.inserted_id

        return AporteInDB(**aporte_dict)

    async def get_by_id(self, user_id: str, aporte_id: str) -> Optional[AporteInDB]:
        """
        Obtener aporte por ID
        """
        aporte = await self.collection.find_one({
            "_id": ObjectId(aporte_id),
            "user_id": ObjectId(user_id)
        })

        return AporteInDB(**aporte) if aporte else None

    async def get_by_periodo(
        self,
        user_id: str,
        periodo_id: str,
        es_fijo: Optional[bool] = None,
        categoria_id: Optional[str] = None
    ) -> List[AporteInDB]:
        """
        Obtener todos los aportes de un período

        Filtros opcionales:
        - es_fijo: True para aportes fijos, False para variables
        - categoria_id: ID de la categoría
        """
        query = {
            "user_id": ObjectId(user_id),
            "periodo_id": ObjectId(periodo_id)
        }

        if es_fijo is not None:
            query["es_fijo"] = es_fijo

        if categoria_id:
            query["categoria_id"] = categoria_id  # Comparar como string, no como ObjectId

        cursor = self.collection.find(query)
        aportes = await cursor.to_list(length=None)

        return [AporteInDB(**ap) for ap in aportes]

    async def get_by_categoria(
        self,
        user_id: str,
        periodo_id: str,
        categoria_id: str
    ) -> List[AporteInDB]:
        """
        Obtener todos los aportes de una categoría en un período específico
        """
        return await self.get_by_periodo(
            user_id=user_id,
            periodo_id=periodo_id,
            categoria_id=categoria_id
        )

    async def get_fijos(self, user_id: str, periodo_id: str) -> List[AporteInDB]:
        """
        Obtener todos los aportes fijos de un período
        (Se copian automáticamente al siguiente período)
        """
        return await self.get_by_periodo(
            user_id=user_id,
            periodo_id=periodo_id,
            es_fijo=True
        )

    async def update(self, user_id: str, aporte_id: str, aporte_update: AporteUpdate) -> Optional[AporteInDB]:
        """
        Actualizar un aporte
        Solo permite editar nombre, monto y descripción
        """
        update_data = aporte_update.model_dump(exclude_none=True)

        if not update_data:
            return await self.get_by_id(user_id, aporte_id)

        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(aporte_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )

        return AporteInDB(**result) if result else None

    async def delete(self, user_id: str, aporte_id: str) -> bool:
        """
        Eliminar un aporte
        """
        result = await self.collection.delete_one({
            "_id": ObjectId(aporte_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    async def calculate_total_by_categoria(
        self,
        user_id: str,
        periodo_id: str,
        categoria_id: str
    ) -> float:
        """
        Calcular el total de aportes de una categoría en un período
        Este valor se RESTA del total de gastos
        """
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "periodo_id": ObjectId(periodo_id),
                    "categoria_id": categoria_id  # Comparar como string, no como ObjectId
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$monto"}
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)

        return result[0]["total"] if result else 0.0

    async def calculate_total_periodo(self, user_id: str, periodo_id: str) -> float:
        """
        Calcular el total de aportes de todo el período
        """
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "periodo_id": ObjectId(periodo_id)
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$monto"}
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)

        return result[0]["total"] if result else 0.0
