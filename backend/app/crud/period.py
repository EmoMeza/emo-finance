from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, date

from app.models.period import (
    PeriodCreate,
    PeriodUpdate,
    PeriodInDB,
    EstadoPeriodo,
    TipoPeriodo,
    MetasCategorias
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
        """Obtener el período activo del usuario, creándolo automáticamente si no existe"""
        query = {
            "user_id": ObjectId(user_id),
            "estado": EstadoPeriodo.ACTIVO
        }

        if tipo_periodo:
            query["tipo_periodo"] = tipo_periodo

        period = await self.collection.find_one(query)

        # Si no existe período activo, crear uno automáticamente
        if not period:
            # Si se pide período mensual, crear ambos (mensual y crédito)
            if not tipo_periodo or tipo_periodo == TipoPeriodo.MENSUAL_ESTANDAR:
                await self._create_both_periods(user_id)
                # Volver a buscar el período mensual recién creado
                period = await self.collection.find_one(query)
            else:
                # Si se pide período de crédito específicamente
                period = await self._create_current_period(user_id, TipoPeriodo.CICLO_CREDITO)

        return PeriodInDB(**period) if period else None

    async def _create_current_period(self, user_id: str, tipo_periodo: TipoPeriodo) -> dict:
        """Crear automáticamente el período del mes/ciclo actual con valores en 0"""
        from datetime import timedelta
        today = date.today()

        if tipo_periodo == TipoPeriodo.MENSUAL_ESTANDAR:
            # Período mensual estándar: día 1 al último día del mes
            fecha_inicio = datetime(today.year, today.month, 1, 0, 0, 0)
            # Calcular último día del mes
            if today.month == 12:
                fecha_fin = datetime(today.year, 12, 31, 23, 59, 59)
            else:
                next_month = datetime(today.year, today.month + 1, 1, 0, 0, 0)
                fecha_fin = next_month - timedelta(seconds=1)
        else:
            # Período de crédito: día 25 del mes anterior al 24 del mes actual
            if today.day >= 25:
                # Si estamos después del día 25, el período va del 25 de este mes al 24 del siguiente
                fecha_inicio = datetime(today.year, today.month, 25, 0, 0, 0)
                if today.month == 12:
                    fecha_fin = datetime(today.year + 1, 1, 24, 23, 59, 59)
                else:
                    fecha_fin = datetime(today.year, today.month + 1, 24, 23, 59, 59)
            else:
                # Si estamos antes del día 25, el período va del 25 del mes pasado al 24 de este mes
                if today.month == 1:
                    fecha_inicio = datetime(today.year - 1, 12, 25, 0, 0, 0)
                else:
                    fecha_inicio = datetime(today.year, today.month - 1, 25, 0, 0, 0)
                fecha_fin = datetime(today.year, today.month, 24, 23, 59, 59)

        # Crear período directamente como dict para evitar validaciones de Pydantic
        # (permitimos sueldo = 0 para períodos sin configurar)
        period_dict = {
            "tipo_periodo": tipo_periodo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "sueldo": 0,  # Se permite 0 en la creación automática
            "metas_categorias": {
                "ahorro": 0,
                "arriendo": 0,
                "credito_usable": 0
            },
            "total_gastado": 0,  # Inicialmente en 0
            "estado": EstadoPeriodo.ACTIVO,
            "user_id": ObjectId(user_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = await self.collection.insert_one(period_dict)
        period_dict["_id"] = result.inserted_id

        return period_dict

    async def _create_both_periods(self, user_id: str):
        """Crear ambos períodos (mensual y crédito) para un usuario nuevo"""
        # Crear período mensual estándar
        await self._create_current_period(user_id, TipoPeriodo.MENSUAL_ESTANDAR)

        # Crear período de crédito
        await self._create_current_period(user_id, TipoPeriodo.CICLO_CREDITO)

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

    def calculate_liquido(self, sueldo: float, metas: dict, deuda_credito_anterior: float = 0) -> float:
        """Calcular el líquido disponible, restando ahorro, arriendo, deuda anterior y crédito usable actual"""
        return sueldo - metas.get("ahorro", 0) - metas.get("arriendo", 0) - deuda_credito_anterior 

    async def get_previous_credit_period(self, user_id: str) -> Optional[PeriodInDB]:
        """Obtener el período de crédito anterior (el que debe pagarse)"""
        # Buscar el período de crédito activo
        credit_period = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "tipo_periodo": TipoPeriodo.CICLO_CREDITO,
            "estado": EstadoPeriodo.ACTIVO
        })

        if not credit_period:
            return None

        # El período anterior es el que terminó justo antes del actual
        # Buscar el período de crédito cerrado más reciente
        previous_period = await self.collection.find_one(
            {
                "user_id": ObjectId(user_id),
                "tipo_periodo": TipoPeriodo.CICLO_CREDITO,
                "estado": EstadoPeriodo.CERRADO,
                "fecha_fin": {"$lt": credit_period["fecha_inicio"]}
            },
            sort=[("fecha_fin", -1)]
        )

        return PeriodInDB(**previous_period) if previous_period else None
