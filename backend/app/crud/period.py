from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.models.period import (
    PeriodCreate,
    PeriodUpdate,
    PeriodInDB,
    EstadoPeriodo,
    TipoPeriodo
)


class PeriodCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.periods

    async def create(self, user_id: str, period_data: PeriodCreate) -> PeriodInDB:
        """Crear un nuevo período"""
        period_dict = period_data.model_dump()
        period_dict["user_id"] = ObjectId(user_id)
        period_dict["created_at"] = datetime.utcnow()
        period_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(period_dict)
        period_dict["_id"] = result.inserted_id

        return PeriodInDB(**period_dict)

    async def get_by_id(self, period_id: str, user_id: str) -> Optional[PeriodInDB]:
        """Obtener un período por ID"""
        period = await self.collection.find_one({
            "_id": ObjectId(period_id),
            "user_id": ObjectId(user_id)
        })

        return PeriodInDB(**period) if period else None

    async def get_active_period(self, user_id: str, tipo_periodo: Optional[TipoPeriodo] = None) -> Optional[PeriodInDB]:
        """Obtener el período activo del usuario"""
        query = {
            "user_id": ObjectId(user_id),
            "estado": EstadoPeriodo.ACTIVO
        }

        if tipo_periodo:
            query["tipo_periodo"] = tipo_periodo

        period = await self.collection.find_one(query)
        return PeriodInDB(**period) if period else None

    async def get_all(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        estado: Optional[EstadoPeriodo] = None,
        tipo_periodo: Optional[TipoPeriodo] = None
    ) -> List[PeriodInDB]:
        """Obtener todos los períodos del usuario con filtros"""
        query = {"user_id": ObjectId(user_id)}

        if estado:
            query["estado"] = estado
        if tipo_periodo:
            query["tipo_periodo"] = tipo_periodo

        cursor = self.collection.find(query).sort("fecha_inicio", -1).skip(skip).limit(limit)
        periods = await cursor.to_list(length=limit)

        return [PeriodInDB(**period) for period in periods]

    async def update(self, period_id: str, user_id: str, update_data: PeriodUpdate) -> Optional[PeriodInDB]:
        """Actualizar un período"""
        update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}

        if not update_dict:
            return await self.get_by_id(period_id, user_id)

        update_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(period_id), "user_id": ObjectId(user_id)},
            {"$set": update_dict},
            return_document=True
        )

        return PeriodInDB(**result) if result else None

    async def close_period(self, period_id: str, user_id: str) -> Optional[PeriodInDB]:
        """Cerrar un período"""
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(period_id), "user_id": ObjectId(user_id)},
            {"$set": {"estado": EstadoPeriodo.CERRADO, "updated_at": datetime.utcnow()}},
            return_document=True
        )

        return PeriodInDB(**result) if result else None

    async def delete(self, period_id: str, user_id: str) -> bool:
        """Eliminar un período"""
        result = await self.collection.delete_one({
            "_id": ObjectId(period_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    async def count(self, user_id: str) -> int:
        """Contar períodos del usuario"""
        return await self.collection.count_documents({"user_id": ObjectId(user_id)})

    async def has_active_period(self, user_id: str, tipo_periodo: TipoPeriodo) -> bool:
        """Verificar si el usuario tiene un período activo de cierto tipo"""
        count = await self.collection.count_documents({
            "user_id": ObjectId(user_id),
            "estado": EstadoPeriodo.ACTIVO,
            "tipo_periodo": tipo_periodo
        })

        return count > 0

    def calculate_liquido(self, sueldo: float, metas: dict) -> float:
        """Calcular el líquido disponible"""
        return sueldo - metas.get("ahorro", 0) - metas.get("arriendo", 0) - metas.get("credito_usable", 0)
