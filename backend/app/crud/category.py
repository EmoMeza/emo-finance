from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.models.category import CategoryCreate, CategoryUpdate, CategoryInDB, TipoCategoria


class CategoryCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.categories

    async def create(self, user_id: str, category_data: CategoryCreate) -> CategoryInDB:
        """Crear una nueva categoría"""
        category_dict = category_data.model_dump()
        category_dict["user_id"] = ObjectId(user_id)
        category_dict["created_at"] = datetime.utcnow()
        category_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(category_dict)
        category_dict["_id"] = result.inserted_id

        return CategoryInDB(**category_dict)

    async def get_by_id(self, category_id: str, user_id: str) -> Optional[CategoryInDB]:
        """Obtener una categoría por ID"""
        category = await self.collection.find_one({
            "_id": ObjectId(category_id),
            "user_id": ObjectId(user_id)
        })

        return CategoryInDB(**category) if category else None

    async def get_by_type(self, user_id: str, tipo: TipoCategoria) -> Optional[CategoryInDB]:
        """Obtener categoría por tipo"""
        category = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "tipo": tipo
        })

        return CategoryInDB(**category) if category else None

    async def get_all(self, user_id: str, tipo: Optional[TipoCategoria] = None) -> List[CategoryInDB]:
        """Obtener todas las categorías del usuario"""
        query = {"user_id": ObjectId(user_id)}

        if tipo:
            query["tipo"] = tipo

        cursor = self.collection.find(query).sort("tipo", 1)
        categories = await cursor.to_list(length=100)

        return [CategoryInDB(**cat) for cat in categories]

    async def update(self, category_id: str, user_id: str, update_data: CategoryUpdate) -> Optional[CategoryInDB]:
        """Actualizar una categoría"""
        update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}

        if not update_dict:
            return await self.get_by_id(category_id, user_id)

        update_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(category_id), "user_id": ObjectId(user_id)},
            {"$set": update_dict},
            return_document=True
        )

        return CategoryInDB(**result) if result else None

    async def delete(self, category_id: str, user_id: str) -> bool:
        """Eliminar una categoría"""
        result = await self.collection.delete_one({
            "_id": ObjectId(category_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    async def initialize_default_categories(self, user_id: str) -> List[CategoryInDB]:
        """Inicializar las 4 categorías predeterminadas para un nuevo usuario"""
        default_categories = [
            {
                "nombre": "Ahorro",
                "tipo": TipoCategoria.AHORRO,
                "color": "#48bb78",
                "icono": "💵",
                "subcategorias": []
            },
            {
                "nombre": "Arriendo",
                "tipo": TipoCategoria.ARRIENDO,
                "color": "#667eea",
                "icono": "🏠",
                "subcategorias": [
                    {"nombre": "Arriendo Base", "color": "#764ba2"},
                    {"nombre": "Luz", "color": "#f6ad55"},
                    {"nombre": "Agua", "color": "#4299e1"},
                    {"nombre": "Gas", "color": "#fc8181"},
                    {"nombre": "Internet", "color": "#9f7aea"},
                    {"nombre": "Gastos Comunes", "color": "#38b2ac"}
                ]
            },
            {
                "nombre": "Crédito Usable",
                "tipo": TipoCategoria.CREDITO,
                "color": "#f56565",
                "icono": "💳",
                "subcategorias": [
                    {"nombre": "Suscripciones", "color": "#ed8936"},
                    {"nombre": "Compras", "color": "#e53e3e"}
                ]
            },
            {
                "nombre": "Líquido",
                "tipo": TipoCategoria.LIQUIDO,
                "color": "#4299e1",
                "icono": "💸",
                "subcategorias": [
                    {"nombre": "Locomoción", "color": "#38b2ac"},
                    {"nombre": "Comida", "color": "#48bb78"},
                    {"nombre": "Entretenimiento", "color": "#9f7aea"}
                ]
            }
        ]

        created_categories = []
        for cat_data in default_categories:
            cat_dict = cat_data.copy()
            cat_dict["user_id"] = ObjectId(user_id)
            cat_dict["created_at"] = datetime.utcnow()
            cat_dict["updated_at"] = datetime.utcnow()

            result = await self.collection.insert_one(cat_dict)
            cat_dict["_id"] = result.inserted_id
            created_categories.append(CategoryInDB(**cat_dict))

        return created_categories
