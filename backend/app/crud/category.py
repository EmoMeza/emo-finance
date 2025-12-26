from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryInDB,
    DEFAULT_CATEGORIES,
    TipoCategoria
)


class CategoryCRUD:
    """
    CRUD operations para Categories según LOGICA_SISTEMA.md

    Las 4 categorías son fijas del sistema y se crean automáticamente
    para cada usuario nuevo.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["categories"]

    async def create(self, user_id: str, category: CategoryCreate) -> CategoryInDB:
        """
        Crear una nueva categoría
        """
        category_dict = category.model_dump(exclude_none=True)
        category_dict["user_id"] = ObjectId(user_id)
        category_dict["created_at"] = datetime.utcnow()
        category_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(category_dict)
        category_dict["_id"] = result.inserted_id

        return CategoryInDB(**category_dict)

    async def get_by_id(self, user_id: str, category_id: str) -> Optional[CategoryInDB]:
        """
        Obtener categoría por ID
        """
        category = await self.collection.find_one({
            "_id": ObjectId(category_id),
            "user_id": ObjectId(user_id)
        })

        return CategoryInDB(**category) if category else None

    async def get_by_slug(self, user_id: str, slug: TipoCategoria) -> Optional[CategoryInDB]:
        """
        Obtener categoría por slug (ahorro, arriendo, credito, liquidez)
        """
        category = await self.collection.find_one({
            "slug": slug,
            "user_id": ObjectId(user_id)
        })

        return CategoryInDB(**category) if category else None

    async def get_all(self, user_id: str) -> List[CategoryInDB]:
        """
        Obtener todas las categorías del usuario
        Deberían ser siempre 4 (las fijas del sistema)
        """
        cursor = self.collection.find({"user_id": ObjectId(user_id)})
        categories = await cursor.to_list(length=None)

        return [CategoryInDB(**cat) for cat in categories]

    async def update(self, user_id: str, category_id: str, category_update: CategoryUpdate) -> Optional[CategoryInDB]:
        """
        Actualizar una categoría
        Solo permite editar nombre, icono, color y descripción
        """
        update_data = category_update.model_dump(exclude_none=True)

        if not update_data:
            return await self.get_by_id(user_id, category_id)

        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(category_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )

        return CategoryInDB(**result) if result else None

    async def delete(self, user_id: str, category_id: str) -> bool:
        """
        Eliminar una categoría
        NOTA: En producción, probablemente NO se deberían eliminar las 4 categorías fijas
        """
        result = await self.collection.delete_one({
            "_id": ObjectId(category_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    async def init_default_categories(self, user_id: str) -> List[CategoryInDB]:
        """
        Inicializar las 4 categorías por defecto para un usuario nuevo

        Según LOGICA_SISTEMA.md:
        1. 💵 Ahorro
        2. 🏠 Arriendo
        3. 💳 Crédito Usable
        4. 💸 Liquidez

        Esta función se debe llamar cuando un usuario se registra por primera vez.
        """
        # Verificar si ya existen categorías para este usuario
        existing = await self.get_all(user_id)
        if existing:
            return existing

        # Crear las 4 categorías por defecto
        created_categories = []

        for cat_data in DEFAULT_CATEGORIES:
            category_dict = cat_data.copy()
            # Convertir el enum TipoCategoria a string para MongoDB
            if isinstance(category_dict["slug"], TipoCategoria):
                category_dict["slug"] = category_dict["slug"].value
            category_dict["user_id"] = ObjectId(user_id)
            category_dict["created_at"] = datetime.utcnow()
            category_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.insert_one(category_dict)
            category_dict["_id"] = result.inserted_id

            created_categories.append(CategoryInDB(**category_dict))

        return created_categories

    async def check_and_init_if_needed(self, user_id: str) -> List[CategoryInDB]:
        """
        Verificar si el usuario tiene las 4 categorías, si no las tiene, las crea
        Útil para llamar en login o en get de categorías
        """
        categories = await self.get_all(user_id)

        if len(categories) < 4:
            # Falta alguna categoría, inicializar todas
            await self.collection.delete_many({"user_id": ObjectId(user_id)})
            categories = await self.init_default_categories(user_id)

        return categories
