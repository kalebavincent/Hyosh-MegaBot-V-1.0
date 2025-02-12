import motor.motor_asyncio
from datetime import datetime
import asyncio
from config import *
from typing import List, Optional

# Connexion à MongoDB
dbClient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
db = dbClient[DB_NAME]
user_data = db['users']

# ------------------------------------
# CREATION DE NOUVEAUX DOCUMENTS AVEC VERIFICATION
# ------------------------------------

async def user_exists(user_id):
    return await user_data.find_one({"_id": user_id}) is not None

async def bot_exists(user_id, bot_id):
    return await user_data.find_one({"_id": user_id, "bots.id": bot_id}) is not None

async def channel_exists(user_id, channel_id):
    return await user_data.find_one({"_id": user_id, "channels.id": channel_id}) is not None

async def create_user(user_id, lang):
    if await user_exists(user_id):
        print(f"✅ L'utilisateur {user_id} existe déjà.")
        return
    user = new_user(user_id, lang)
    user["settings"] = default_settings(user_id)
    await user_data.insert_one(user)
    print(f"✅ Utilisateur {user_id} créé avec succès.")

async def create_bot(user_id, bot_id, bot_token, bot_name):
    if await bot_exists(user_id, bot_id):
        print(f"✅ Le bot {bot_id} existe déjà pour l'utilisateur {user_id}.")
        return
    bot = new_bot(bot_id, bot_token, bot_name)
    await user_data.update_one(
        {"_id": user_id},
        {"$push": {"bots": bot}},
    )
    print(f"✅ Bot {bot_id} ajouté pour l'utilisateur {user_id}.")

# ------------------------------------
# FONCTION POUR ASSOCIER UN BOT À UN CANAL
# ------------------------------------
async def assign_bot_to_channel(user_id, channel_id, bot_id):
    """Associe un bot à un canal en ajoutant son ID à la liste des bots du canal."""
    channel_id = int(channel_id)

    # Vérifier si le bot est déjà associé au canal
    user = await user_data.find_one({"_id": user_id, "channels.id": channel_id})
    if user:
        channel = next((c for c in user["channels"] if c["id"] == channel_id), None)
        if channel and bot_id in channel.get("bots", []):
            print(f"✅ Le bot {bot_id} est déjà associé au canal {channel_id}.")
            return
        
        # Ajouter le bot au canal
        await user_data.update_one(
            {"_id": user_id, "channels.id": channel_id},
            {"$push": {"channels.$.bots": bot_id}}
        )
        print(f"✅ Bot {bot_id} ajouté au canal {channel_id} pour l'utilisateur {user_id}.")
    else:
        print(f"❌ Le canal {channel_id} n'existe pas pour l'utilisateur {user_id}.")

# ------------------------------------
# CRÉATION DE CANAL AVEC BOT ASSOCIÉ
# ------------------------------------
async def create_channel(user_id, channel_id, channel_name, bot_id=None, vus=0, reactions=0, likes=0, shares=0, admins=[]):
    """Crée un nouveau canal et associe un bot si spécifié."""
    if await channel_exists(user_id, int(channel_id)):
        print(f"✅ Le canal {channel_id} existe déjà pour l'utilisateur {user_id}.")
        await assign_bot_to_channel(user_id, channel_id, bot_id)
        return

    channel = new_channel(channel_id, channel_name, vus, reactions, likes, shares, admins)
    
    # Ajouter le canal à la liste des canaux de l'utilisateur
    await user_data.update_one(
        {"_id": user_id},
        {"$push": {"channels": channel}}
    )
    print(f"✅ Canal {channel_id} ajouté pour l'utilisateur {user_id}.")

    # Si un bot est spécifié, l'associer au canal
    if bot_id:
        await assign_bot_to_channel(user_id, channel_id, bot_id)


async def update_user_settings(user_id, field, value):
    await user_data.update_one(
        {"_id": user_id},
        {"$set": {f"settings.{field}": value}}
    )
    

# ------------------------------------
# LIRE LES DOCUMENTS
# ------------------------------------

async def get_user(user_id):
    return await user_data.find_one({"_id": user_id})

async def get_bots(user_id):
    user = await get_user(user_id)
    return user.get("bots", [])


async def get_channels(user_id):
    user = await get_user(user_id)
    return user.get("channels", []) if user else []

async def get_channels_of_bot(user_id, bot_id):
    user = await get_user(user_id)
    bot = next((bot for bot in user.get("bots", []) if bot["id"] == bot_id), None)
    return bot["channels"] if bot else []

async def get_posts(user_id):
    user = await get_user(user_id)
    return user.get("posts", []) if user else []
# ------------------------------------
# METTRE A JOUR LES DOCUMENTS
# ------------------------------------

async def update_user(user_id, field, value):
    await user_data.update_one(
        {"_id": user_id},
        {"$set": {field: value}}
    )

async def update_bot(user_id, bot_id, new_token):
    await user_data.update_one(
        {"_id": user_id, "bots.id": bot_id},
        {"$set": {"bots.$.token": new_token}}
    )

async def update_channel(user_id, channel_id, field, value):
    channel_id = int(channel_id)
    
    await user_data.update_one(
        {"_id": user_id, "channels.id": channel_id},
        {"$set": {f"channels.$.{field}": value}}
    )
    


async def get_all_bot_tokens():
    users = await user_data.find().to_list(None)
    all_bot_tokens = {}

    for user in users:
        user_id = user["_id"]
        bots = user.get("bots", [])
        bot_data = [{"id": bot["id"], "token": bot["token"]} for bot in bots if "id" in bot and "token" in bot]

        if bot_data:
            all_bot_tokens[user_id] = bot_data

    return all_bot_tokens

async def get_channels_by_bot(user_id, bot_id):
    user = await get_user(user_id)
    if not user:
        return []

    channels = user.get("channels", [])
    
    # Filtrer les canaux où bot_id est présent dans la liste bots
    bot_channels = [channel for channel in channels if bot_id in channel.get("bots", [])]
    
    return bot_channels

async def get_unassigned_channels(user_id):
    """Retourne la liste des canaux d'un utilisateur qui ne sont associés à aucun bot."""
    
    user = await get_user(user_id)
    if not user:
        return []

    channels = user.get("channels", [])
    
    # Filtrer les canaux où la liste "bots" est vide ou absente
    unassigned_channels = [channel for channel in channels if not channel.get("bots")]

    return unassigned_channels



async def get_user_settings(client, query: str):
    user_id = query.from_user.id
    user_data = await get_user(user_id)
    return user_data.get("settings", {})


# ------------------------------------
# SUPPRIMER LES DOCUMENTS
# ------------------------------------

async def delete_user(user_id):
    await user_data.delete_one({"_id": user_id})
    print(f"✅ Utilisateur {user_id} supprimé.")

async def delete_bot(user_id, bot_id):
    await user_data.update_one(
        {"_id": user_id},
        {"$pull": {"bots": {"id": bot_id}}}
    )
    print(f"✅ Bot {bot_id} supprimé de l'utilisateur {user_id}.")

async def delete_channel(user_id, channel_id):
    channel_id = int(channel_id)
    await user_data.update_one(
        {"_id": user_id},
        {"$pull": {"channels": {"id": channel_id}}}
    )
    print(f"✅ Canal {channel_id} supprimé de l'utilisateur {user_id}.")

# ------------------------------------
# FONCTIONS D'ASSISTANCE (STRUCTURES DE BASE)
# ------------------------------------

def new_user(id, lang):
    return {
        "_id": id,
        "lang": lang,
        "created_at": datetime.now(),
        "bots": [],
        "channels": [],
        "settings": {},
        "posts": []
    }

def new_bot(id, token, name):
    return {
        "id": id,
        "token": token,
        "name": name
    }

def new_channel(id, name, vus, reactions, likes, shares, admins):
    return {
        "id": id,
        "name": name,
        "vus": vus,
        "reactions": reactions,
        "likes": likes,
        "shares": shares,
        "admins": admins,
        "bots": []
    }
    
def default_settings(id):
    return {
        "id": 1,
        "format_format": "normal",
        "protected_msg": False,
        "notifications": True,
        "auto_delete": False,
        "link_preview": False,
        "default_reaction": False,
        "default_reaction_emoji": "👍",
        "delay_time": 0,
        "schedule_time": 0,
    }


