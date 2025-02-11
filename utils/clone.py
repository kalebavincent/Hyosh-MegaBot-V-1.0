import asyncio
import aiohttp
from pyrogram import Client
from config import *
from database.userdata import get_all_bot_tokens

ACTIVE_BOTS = {} 

async def is_valid_token(token: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return "id" in data.get("result", {})
                return False
    except Exception as e:
        return False


async def create_bot_clone(user_id: int, bot_id: str, bot_token: str):
    """Crée et démarre un clone du bot avec vérification du token, et retourne ses informations."""
    
    if bot_id in ACTIVE_BOTS:
        return None

    if not await is_valid_token(bot_token):
        return None

    bot = Client(f"bot_{bot_id}", api_id=API_ID, api_hash=API_HASH, bot_token=bot_token, plugins=dict(root=CLONEPLUGINPATH))
    try:
        await bot.start()
        
        bot_info = await bot.get_me()

        ACTIVE_BOTS[bot_id] = bot
        
        return {
            "bot_id": bot_info.id,
            "bot_username": bot_info.username,
            "bot_name": bot_info.first_name,
            "bot_token": bot_token
        }
    except Exception as e:
        return None



async def stop_bot_clone(bot_id: str):
    bot = ACTIVE_BOTS.get(bot_id)
    if bot:
        await bot.stop()
        del ACTIVE_BOTS[bot_id]
    else:
        pass

async def start_all_bots():
    all_bot_tokens = await get_all_bot_tokens()

    tasks = []  

    for user_id, bots in all_bot_tokens.items():
        for bot in bots:
            bot_id = bot["id"]
            bot_token = bot["token"]

            if bot_id in ACTIVE_BOTS:
                continue

            if not await is_valid_token(bot_token):
                continue

            bot_client = Client(
                name=f"bot_{bot_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=bot_token,
                plugins={"root": CLONEPLUGINPATH}  
            )

            tasks.append(start_bot(bot_id, bot_client))  

    await asyncio.gather(*tasks)  

async def start_bot(bot_id, bot_client):
    try:
        await bot_client.start()
        ACTIVE_BOTS[bot_id] = bot_client
    except Exception as e:
        pass