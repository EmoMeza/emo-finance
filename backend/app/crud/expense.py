from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseInDB,
    TipoGasto
)


class ExpenseCRUD:
    """
    CRUD operations para Expenses según LOGICA_SISTEMA.md

    Maneja gastos fijos (permanentes y temporales) y gastos variables
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["expenses"]

    async def create(self, user_id: str, periodo_id: str, expense: ExpenseCreate) -> ExpenseInDB:
        """
        Crear un nuevo gasto
        """
        expense_dict = expense.model_dump(exclude_none=True)
        expense_dict["user_id"] = ObjectId(user_id)
        expense_dict["periodo_id"] = ObjectId(periodo_id)
        expense_dict["fecha_registro"] = datetime.utcnow()
        expense_dict["created_at"] = datetime.utcnow()
        expense_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(expense_dict)
        expense_dict["_id"] = result.inserted_id

        return ExpenseInDB(**expense_dict)

    async def get_by_id(self, user_id: str, expense_id: str) -> Optional[ExpenseInDB]:
        """
        Obtener gasto por ID
        """
        expense = await self.collection.find_one({
            "_id": ObjectId(expense_id),
            "user_id": ObjectId(user_id)
        })

        return ExpenseInDB(**expense) if expense else None

    async def get_by_periodo(
        self,
        user_id: str,
        periodo_id: str,
        tipo: Optional[TipoGasto] = None,
        categoria_id: Optional[str] = None
    ) -> List[ExpenseInDB]:
        """
        Obtener todos los gastos de un período

        Filtros opcionales:
        - tipo: TipoGasto.FIJO o TipoGasto.VARIABLE
        - categoria_id: ID de la categoría
        """
        query = {
            "user_id": ObjectId(user_id),
            "periodo_id": ObjectId(periodo_id)
        }

        if tipo:
            query["tipo"] = tipo

        if categoria_id:
            query["categoria_id"] = categoria_id  # Comparar como string, no como ObjectId

        cursor = self.collection.find(query)
        expenses = await cursor.to_list(length=None)

        return [ExpenseInDB(**exp) for exp in expenses]

    async def get_by_categoria(
        self,
        user_id: str,
        periodo_id: str,
        categoria_id: str
    ) -> List[ExpenseInDB]:
        """
        Obtener todos los gastos de una categoría en un período específico
        """
        return await self.get_by_periodo(
            user_id=user_id,
            periodo_id=periodo_id,
            categoria_id=categoria_id
        )

    async def get_fijos_permanentes(self, user_id: str, periodo_id: str) -> List[ExpenseInDB]:
        """
        Obtener todos los gastos fijos permanentes de un período
        (Se copian automáticamente al siguiente período)
        """
        cursor = self.collection.find({
            "user_id": ObjectId(user_id),
            "periodo_id": ObjectId(periodo_id),
            "tipo": TipoGasto.FIJO,
            "es_permanente": True
        })
        expenses = await cursor.to_list(length=None)

        return [ExpenseInDB(**exp) for exp in expenses]

    async def get_fijos_temporales_activos(self, user_id: str, periodo_id: str) -> List[ExpenseInDB]:
        """
        Obtener todos los gastos fijos temporales con períodos restantes > 0
        (Se copian decrementando periodos_restantes)
        """
        cursor = self.collection.find({
            "user_id": ObjectId(user_id),
            "periodo_id": ObjectId(periodo_id),
            "tipo": TipoGasto.FIJO,
            "es_permanente": False,
            "periodos_restantes": {"$gt": 0}
        })
        expenses = await cursor.to_list(length=None)

        return [ExpenseInDB(**exp) for exp in expenses]

    async def update(self, user_id: str, expense_id: str, expense_update: ExpenseUpdate) -> Optional[ExpenseInDB]:
        """
        Actualizar un gasto
        Solo permite editar nombre, monto y descripción
        """
        update_data = expense_update.model_dump(exclude_none=True)

        if not update_data:
            return await self.get_by_id(user_id, expense_id)

        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(expense_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )

        return ExpenseInDB(**result) if result else None

    async def delete(self, user_id: str, expense_id: str) -> bool:
        """
        Eliminar un gasto
        """
        result = await self.collection.delete_one({
            "_id": ObjectId(expense_id),
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
        Calcular el total de gastos de una categoría en un período
        Suma de todos los gastos (fijos + variables)
        """
        # DEBUG: Log de búsqueda
        print(f"DEBUG EXPENSE: Buscando gastos con user_id={user_id}, periodo_id={periodo_id}, categoria_id={categoria_id}")

        # Primero verificar cuántos gastos hay en total para este período
        total_count = await self.collection.count_documents({"periodo_id": ObjectId(periodo_id)})
        print(f"DEBUG EXPENSE: Total gastos en periodo {periodo_id}: {total_count}")

        # Ver un ejemplo de gasto para comparar
        sample = await self.collection.find_one({"periodo_id": ObjectId(periodo_id)})
        if sample:
            print(f"DEBUG EXPENSE: Ejemplo de gasto: user_id={sample.get('user_id')} (tipo: {type(sample.get('user_id'))}), categoria_id={sample.get('categoria_id')} (tipo: {type(sample.get('categoria_id'))}), monto={sample.get('monto')}")

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

        print(f"DEBUG EXPENSE: Resultado agregación: {result}")

        return result[0]["total"] if result else 0.0

    async def calculate_total_periodo(self, user_id: str, periodo_id: str) -> float:
        """
        Calcular el total de gastos de todo el período
        (Útil para períodos de crédito -> total_gastado)
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
