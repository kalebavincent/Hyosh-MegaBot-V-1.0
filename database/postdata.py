import motor.motor_asyncio
from datetime import datetime
from config import *
from typing import List, Optional
from models.postmodel import Post

dbClient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = dbClient[DB_NAME]
posts_collection = db["posts"]


# -------------------- CRUD Async --------------------

async def create_post(post: Post) -> str:
    """Insère un post dans la base de données et retourne son ID."""
    post_dict = post.model_dump()
    result = await posts_collection.insert_one(post_dict)
    return str(result.inserted_id)

async def get_post_by_id(post_id: int) -> Optional[Post]:
    """Récupère un post spécifique par son ID."""
    post = await posts_collection.find_one({"id": post_id})
    return Post(**post) if post else None


# async def get_post_by_unique_id(unique_id: str) -> Optional[Post]:
#     """Récupère un post spécifique par son ID."""
#     post = await posts_collection.find_one({"id": unique_id})
#     return Post(**post) if post else None

async def get_all_posts() -> List[Post]:
    """Récupère tous les posts de la collection."""
    posts = await posts_collection.find().to_list(None)  
    return [Post(**post) for post in posts]

async def update_post(post_id: int, new_data: dict) -> bool:
    """Met à jour un post existant par son ID."""
    result = await posts_collection.update_one({"id": post_id}, {"$set": new_data})
    return result.modified_count > 0

async def update_post_by_unique_id(unique_id: str, new_data: dict) -> bool:
    """Met à jour un post existant par son Unique ID."""
    result = await posts_collection.update_one({"unique_id": unique_id}, {"$set": new_data})
    return result.modified_count > 0

async def delete_post(post_id: int) -> bool:
    """Supprime un post par son ID."""
    result = await posts_collection.delete_one({"id": post_id})
    return result.deleted_count > 0

async def delete_posts_by_author(author_id: int) -> int:
    """Supprime tous les posts d'un auteur spécifique et retourne le nombre supprimé."""
    result = await posts_collection.delete_many({"author.id": author_id})
    return result.deleted_count

async def get_post_by_unique_id(unique_id: str) -> Optional[Post]:
    """
    Récupère un post à partir de son unique_id.

    :param unique_id: L'identifiant unique du post.
    :return: Objet Post si trouvé, sinon None.
    """
    try:
        # Rechercher le post en base de données en utilisant unique_id
        post = await posts_collection.find_one({"unique_id": unique_id})

        return Post(**post) if post else None

    except Exception as e:
        print(f"❌ Erreur lors de la récupération du post avec unique_id {unique_id} : {e}")
        return None

