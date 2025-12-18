from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.models.expense import ExpenseCreate, ExpenseUpdate, ExpenseInDB, TipoGasto, EstadoGasto


class ExpenseCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.expenses

    async def create(self, user_id: str, expense_data: ExpenseCreate) -> ExpenseInDB:
        """Crear un nuevo gasto"""
        expense_dict = expense_data.model_dump()
        expense_dict["user_id"] = ObjectId(user_id)
        expense_dict["periodo_id"] = ObjectId(expense_data.periodo_id)
        expense_dict["categoria_id"] = ObjectId(expense_data.categoria_id)

        if expense_data.plantilla_id:
            expense_dict["plantilla_id"] = ObjectId(expense_data.plantilla_id)

        expense_dict["created_at"] = datetime.utcnow()
        expense_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(expense_dict)
        expense_dict["_id"] = result.inserted_id

        return ExpenseInDB(**expense_dict)

    async def get_by_id(self, expense_id: str, user_id: str) -> Optional[ExpenseInDB]:
        """Obtener un gasto por ID"""
        expense = await self.collection.find_one({
            "_id": ObjectId(expense_id),
            "user_id": ObjectId(user_id)
        })

        return ExpenseInDB(**expense) if expense else None

    async def get_by_period(
        self,
        user_id: str,
        periodo_id: str,
        tipo: Optional[TipoGasto] = None,
        estado: Optional[EstadoGasto] = None
    ) -> List[ExpenseInDB]:
        """Obtener gastos de un período"""
        query = {
            "user_id": ObjectId(user_id),
            "periodo_id": ObjectId(periodo_id)
        }

        if tipo:
            query["tipo"] = tipo
        if estado:
            query["estado"] = estado

        cursor = self.collection.find(query).sort("fecha", -1)
        expenses = await cursor.to_list(length=1000)

        return [ExpenseInDB(**expense) for expense in expenses]

    async def get_by_category(
        self,
        user_id: str,
        categoria_id: str,
        periodo_id: Optional[str] = None
    ) -> List[ExpenseInDB]:
        """Obtener gastos de una categoría"""
        query = {
            "user_id": ObjectId(user_id),
            "categoria_id": ObjectId(categoria_id)
        }

        if periodo_id:
            query["periodo_id"] = ObjectId(periodo_id)

        cursor = self.collection.find(query).sort("fecha", -1)
        expenses = await cursor.to_list(length=1000)

        return [ExpenseInDB(**expense) for expense in expenses]

    async def update(self, expense_id: str, user_id: str, update_data: ExpenseUpdate) -> Optional[ExpenseInDB]:
        """Actualizar un gasto"""
        update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}

        if not update_dict:
            return await self.get_by_id(expense_id, user_id)

        update_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(expense_id), "user_id": ObjectId(user_id)},
            {"$set": update_dict},
            return_document=True
        )

        return ExpenseInDB(**result) if result else None

    async def mark_as_paid(self, expense_id: str, user_id: str) -> Optional[ExpenseInDB]:
        """Marcar un gasto como pagado"""
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(expense_id), "user_id": ObjectId(user_id)},
            {"$set": {"estado": EstadoGasto.PAGADO, "updated_at": datetime.utcnow()}},
            return_document=True
        )

        return ExpenseInDB(**result) if result else None

    async def delete(self, expense_id: str, user_id: str) -> bool:
        """Eliminar un gasto"""
        result = await self.collection.delete_one({
            "_id": ObjectId(expense_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    async def get_total_by_period(self, user_id: str, periodo_id: str) -> float:
        """Obtener el total gastado en un período"""
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "periodo_id": ObjectId(periodo_id),
                    "estado": {"$in": [EstadoGasto.PAGADO, EstadoGasto.PROYECTADO]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$valor"}
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0.0

    async def get_total_by_category(self, user_id: str, periodo_id: str, categoria_id: str) -> float:
        """Obtener el total gastado en una categoría de un período"""
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "periodo_id": ObjectId(periodo_id),
                    "categoria_id": ObjectId(categoria_id),
                    "estado": {"$in": [EstadoGasto.PAGADO, EstadoGasto.PROYECTADO]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$valor"}
                }
            }
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0.0
