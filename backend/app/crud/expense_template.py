from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.models.expense_template import ExpenseTemplateCreate, ExpenseTemplateUpdate, ExpenseTemplateInDB


class ExpenseTemplateCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.expense_templates

    async def create(self, user_id: str, template_data: ExpenseTemplateCreate) -> ExpenseTemplateInDB:
        """Crear una nueva plantilla de gasto fijo"""
        template_dict = template_data.model_dump()
        template_dict["user_id"] = ObjectId(user_id)
        template_dict["categoria_id"] = ObjectId(template_data.categoria_id)
        template_dict["created_at"] = datetime.utcnow()
        template_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(template_dict)
        template_dict["_id"] = result.inserted_id

        return ExpenseTemplateInDB(**template_dict)

    async def get_by_id(self, template_id: str, user_id: str) -> Optional[ExpenseTemplateInDB]:
        """Obtener una plantilla por ID"""
        template = await self.collection.find_one({
            "_id": ObjectId(template_id),
            "user_id": ObjectId(user_id)
        })

        return ExpenseTemplateInDB(**template) if template else None

    async def get_all(self, user_id: str, activa: Optional[bool] = None) -> List[ExpenseTemplateInDB]:
        """Obtener todas las plantillas del usuario"""
        query = {"user_id": ObjectId(user_id)}

        if activa is not None:
            query["activa"] = activa

        cursor = self.collection.find(query).sort("nombre", 1)
        templates = await cursor.to_list(length=100)

        return [ExpenseTemplateInDB(**template) for template in templates]

    async def get_active_templates(self, user_id: str) -> List[ExpenseTemplateInDB]:
        """Obtener solo las plantillas activas"""
        return await self.get_all(user_id, activa=True)

    async def update(self, template_id: str, user_id: str, update_data: ExpenseTemplateUpdate) -> Optional[ExpenseTemplateInDB]:
        """Actualizar una plantilla"""
        update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}

        if not update_dict:
            return await self.get_by_id(template_id, user_id)

        update_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(template_id), "user_id": ObjectId(user_id)},
            {"$set": update_dict},
            return_document=True
        )

        return ExpenseTemplateInDB(**result) if result else None

    async def toggle_active(self, template_id: str, user_id: str) -> Optional[ExpenseTemplateInDB]:
        """Activar/desactivar una plantilla"""
        template = await self.get_by_id(template_id, user_id)

        if not template:
            return None

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(template_id), "user_id": ObjectId(user_id)},
            {"$set": {"activa": not template.activa, "updated_at": datetime.utcnow()}},
            return_document=True
        )

        return ExpenseTemplateInDB(**result) if result else None

    async def delete(self, template_id: str, user_id: str) -> bool:
        """Eliminar una plantilla"""
        result = await self.collection.delete_one({
            "_id": ObjectId(template_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0
