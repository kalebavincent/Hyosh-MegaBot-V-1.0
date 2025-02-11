# -*- coding: utf-8 -*-

import aiohttp, asyncio, warnings, pytz
from datetime import datetime, timedelta
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import *
from aiohttp import web
from plugins import web_server
import pyrogram.utils
import pyromod
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
from utils.clone import start_all_bots
from database.userdata import *
from dotenv import load_dotenv
load_dotenv()
MIN_CHANNEL_ID = int(os.environ.get("MIN_CHANNEL_ID"))
pyrogram.utils.MIN_CHANNEL_ID =MIN_CHANNEL_ID

# Setting SUPPORT_CHAT directly here
SUPPORT_CHAT = int("-1002175858655")  



class Bot(Client):

    def __init__(self):
        super().__init__(
            name="HyoshMegaBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN, 
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

        self.start_time = time.time()

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = BOT_UPTIME     

        await start_all_bots()  

        if WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()       
            await web.TCPSite(app, "0.0.0.0", 8080).start()     
        print(f"{me.first_name} Is Started.....✨️")

        # Calcul du temps de fonctionnement
        uptime_seconds = int(time.time() - self.start_time)
        uptime_string = str(timedelta(seconds=uptime_seconds))
 
        for chat_id in [LOG_CHANNEL, SUPPORT_CHAT]:
            try:
                curr = datetime.now(timezone("UTC"))
                date = curr.strftime('%d %B, %Y')
                time_str = curr.strftime('%I:%M:%S %p')
                
                # Envoi du message avec l'uptime
                await self.send_message(
                    chat_id=chat_id,
                    text= (
                        "**Mega ᴇsᴛ ʀᴇᴅᴇᴍᴀʀʀᴇᴇ ᴇɴᴄᴏʀᴇ !**\n\n"
                        f"ᴊᴇ ɴ'ᴀɪ ᴘᴀs ᴅᴏʀᴍɪs ᴅᴇᴘᴜɪs​ : `{uptime_string}`"
                    ),
                    protect_content=True, 
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/hyoshmangavf")
                        ]] 
                    )
                )

            except Exception as e:
                print(f"Failed to send message in chat {chat_id}: {e}")


Bot().run()