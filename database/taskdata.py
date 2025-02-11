import motor.motor_asyncio
from typing import List, Optional
from datetime import datetime
from config import DB_NAME, DB_URI
from models.taskmodel import Task
from database.postdata import delete_post

dbClient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = dbClient[DB_NAME]
tasks_collection = db["tasks"]


# -------------------- CRUD Async --------------------

async def create_task_for_user(task: Task) -> str:
    """Insère une tâche dans la base de données et retourne son ID."""
    task_dict = task.model_dump()  
    result = await tasks_collection.insert_one(task_dict)
    return str(result.inserted_id)

async def get_task_by_id(task_id: int) -> Optional[Task]:
    """Récupère une tâche spécifique par son ID."""
    task = await tasks_collection.find_one({"id": task_id})
    return Task(**task) if task else None

async def get_all_tasks() -> List[Task]:
    """Récupère toutes les tâches de la collection."""
    tasks = await tasks_collection.find().to_list(None)
    return [Task(**task) for task in tasks]

async def update_task(task_id: int, new_data: dict) -> bool:
    """Met à jour une tâche existante par son ID."""
    result = await tasks_collection.update_one({"id": task_id}, {"$set": new_data})
    return result.modified_count > 0

async def delete_task(task_id: int) -> bool:
    """Supprime une tâche par son ID ainsi que tous les posts associés à cette tâche."""
    task = await get_task_by_id(task_id)
    if not task:
        print("Tâche non trouvée.")
        return False
    
    for post_id in task.posts_id:
        await delete_post(post_id)
        print(f"Post {post_id} supprimé.")
    
    result = await tasks_collection.delete_one({"id": task_id})
    
    if result.deleted_count > 0:
        print(f"Tâche {task_id} supprimée avec succès.")
        return True
    else:
        print("Erreur lors de la suppression de la tâche.")
        return False


async def delete_tasks_by_user(user_id: int) -> int:
    """Supprime toutes les tâches d'un utilisateur spécifique et retourne le nombre supprimé."""
    result = await tasks_collection.delete_many({"user_id": user_id})
    return result.deleted_count

async def get_tasks_by_user(user_id: int) -> List[Task]:
    """Récupère toutes les tâches d'un utilisateur spécifique."""
    tasks = await tasks_collection.find({"user_id": user_id}).to_list(None)
    return [Task(**task) for task in tasks]

async def get_tasks_by_channel(channel_id: int) -> List[Task]:
    """Récupère toutes les tâches associées à un canal spécifique."""
    tasks = await tasks_collection.find({"channels_id": channel_id}).to_list(None)
    return [Task(**task) for task in tasks]










