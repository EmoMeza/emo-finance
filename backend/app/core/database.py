from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = None
database = None


async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(settings.MONGO_URI)
    database = client[settings.MONGO_DB_NAME]
    print(f"Connected to MongoDB: {settings.MONGO_DB_NAME}")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


def get_database():
    return database
