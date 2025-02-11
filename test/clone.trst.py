import os
import aiohttp
from pyrogram import Client
from dotenv import load_dotenv
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
bot_token = "7586638113:AAHHszj6xuFdCcxj_mK7Dl0giYxhrUJjklA"

app = Client("Megaclonebot", api_id=API_ID, api_hash=API_HASH, bot_token=bot_token)

async def main():
    await app.start()
    print("Bot démarré avec succès !")
    await app.stop()

app.run(main())
