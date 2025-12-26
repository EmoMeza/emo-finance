from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserCreate, UserUpdate, UserInDB
from app.core.security import get_password_hash


class UserCRUD:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users

    async def create(self, user: UserCreate) -> UserInDB:
        """
        Create a new user in the database.
        """
        user_dict = user.model_dump()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        user_dict["is_active"] = True
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id

        return UserInDB(**user_dict)

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """
        Get a user by ID.
        """
        if not ObjectId.is_valid(user_id):
            return None

        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return UserInDB(**user)
        return None

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get a user by email.
        """
        user = await self.collection.find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None

    async def get_by_username(self, username: str) -> Optional[UserInDB]:
        """
        Get a user by username.
        """
        user = await self.collection.find_one({"username": username})
        if user:
            return UserInDB(**user)
        return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """
        Get all users with pagination.
        """
        cursor = self.collection.find().skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        return [UserInDB(**user) for user in users]

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """
        Alias for get_all. Get all users with pagination.
        """
        return await self.get_all(skip=skip, limit=limit)

    async def update(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """
        Update a user by ID.
        """
        if not ObjectId.is_valid(user_id):
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_by_id(user_id)

        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            return None

        return await self.get_by_id(user_id)

    async def delete(self, user_id: str) -> bool:
        """
        Delete a user by ID.
        """
        if not ObjectId.is_valid(user_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def exists_by_email(self, email: str) -> bool:
        """
        Check if a user with the given email exists.
        """
        count = await self.collection.count_documents({"email": email})
        return count > 0

    async def exists_by_username(self, username: str) -> bool:
        """
        Check if a user with the given username exists.
        """
        count = await self.collection.count_documents({"username": username})
        return count > 0
