"""
Script de inicialización de la base de datos.
Crea el usuario admin inicial si no existe ningún usuario.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import get_password_hash
from app.models.user import UserRole
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def init_db(db: AsyncIOMotorDatabase) -> None:
    """
    Inicializa la base de datos creando el usuario admin si no existe ningún usuario.

    Credenciales del admin inicial:
    - Username: admin
    - Password: adminpass
    - Role: admin
    """
    try:
        # Verificar si existe algún usuario
        users_count = await db.users.count_documents({})

        if users_count == 0:
            logger.info("No se encontraron usuarios. Creando usuario admin inicial...")

            # Crear usuario admin
            admin_user = {
                "email": "admin@emo-finance.com",
                "username": "admin",
                "first_name": "Admin",
                "last_name": "System",
                "hashed_password": get_password_hash("adminpass"),
                "role": UserRole.ADMIN.value,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            result = await db.users.insert_one(admin_user)
            logger.info(f"✅ Usuario admin creado exitosamente con ID: {result.inserted_id}")
            logger.info("📝 Credenciales iniciales - Username: admin, Password: adminpass")
            logger.warning("⚠️  IMPORTANTE: Cambie la contraseña del admin después del primer login")
        else:
            logger.info(f"Base de datos ya inicializada ({users_count} usuarios encontrados)")

    except Exception as e:
        logger.error(f"Error inicializando la base de datos: {e}")
        raise
