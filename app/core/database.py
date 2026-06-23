from motor.motor_asyncio import AsyncIOMotorClient
from .config import setting

client = AsyncIOMotorClient(setting.MONGODB_URL)

db = client[setting.MONGODB_DB_NAME]