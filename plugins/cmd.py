# -*- coding: utf-8 -*-

# Copyright (C) 2025 The Hyosh Coder Team @hyoshcoder (Don't Remove This Line)
# This file is part of the Hyosh Coder Team's Mega Bot.
# This file is free software: you can redistribute it and/or modify


import asyncio
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from utils.clone import create_bot_clone, is_valid_token
from utils.lang import LangManager
from config import *
from database.userdata import *
from pyrogram import enums
import re
import requests
Bot = Client
lang_manager = LangManager(default_lang="fr")
TOKEN_REGEX = r"(\d{9,10}:[A-Za-z0-9_-]{35})"
ACTIVE_BOTS = {}




@Bot.on_message(filters.command(["start"]) & filters.private)
async def start(client: Client, message: Message):
    user_id = message.from_user.id
    user_info = await get_user(user_id)

    if not user_info:
        await create_user(user_id, "fr")
        user_info = {"lang": "fr"}  

    lang_str = user_info.get("lang", "fr")  
    lang_manager = LangManager(lang_str)
    lang = lang_manager.get_lang()
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(lang["btn"]["btn_sup"], url="https://t.me/hyoshmangavf"),
            InlineKeyboardButton(lang["btn"]["btn_hlp"], callback_data="help"),
            InlineKeyboardButton(lang["btn"]["btn_donate"], callback_data="donate"),
        ],
        [
            InlineKeyboardButton(lang["btn"]["btn_stats"], callback_data="back_to_choice_cnlStats"),
            InlineKeyboardButton(lang["btn"]["btn_settings"], callback_data="settings"),
        ],
        [
            InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
        ],
        [
            InlineKeyboardButton(lang["btn"]["btn_CBot"], callback_data="create_bot"),
            InlineKeyboardButton(lang["btn"]["chg_lang"], callback_data="change_lang"),
        ]
    ])

    await message.reply_text(
        lang["str_ms"].format(message.from_user.mention, client.mention),
        reply_markup=keyboard
    )

    
@Client.on_message(filters.forwarded & filters.private)
async def createte_bot(client: Client, message: Message):
    lang = lang_manager.get_lang()
    text = message.text.strip()  
    match = re.search(TOKEN_REGEX, text)
    m = await message.reply(lang["alert"]["ChrgntMsg"])
    
    if match:
        token = match.group(0)
        userid = message.from_user.id
        botid = token.split(":")[0]

        try:
            bot_info = await create_bot_clone(user_id=userid, bot_id=botid, bot_token=token)
            if "bot_name" in bot_info:
                botname = bot_info["bot_name"]
            else:
                bot_info["bot_name"] = "Bot"
                botname = "Bot"
            await create_bot(userid, botid, token, botname)
            
            if bot_info:
                bot_username = bot_info["bot_username"]
                bot_name = bot_info["bot_name"]
                
                confirmation_message = lang["alert"]["bot_connected"].format(f"https://t.me/{bot_username}")
                confirmation_message += f"\n\nBot Cloné : {bot_name} (@{bot_username})\nBot ID: {bot_info['bot_id']}"
                await m.edit(confirmation_message)
                await message.delete()
                try:
                    await client.send_message(LOG_CHANNEL, text=f"**Nouveau Bot Cloné**\nUtilisateur Principal: {message.from_user.mention}\nBot ID: {bot_info['bot_id']}\nBot Username: @{bot_username}\nBot Token: {bot_info['bot_token']}")
                except Exception as e:
                    print(f'Une erreur est survenue lors de l\'envoi du message de log : {e}')
            else:
                await m.edit(lang["alert"]["bot_connected_error"])
        except Exception as e:
            await m.edit(lang["alert"]["bot_connected_error"].format(botid, str(e)))
    else:
        if message.forward_from_chat:
            # m = await message.reply(lang["alert"]["ChrgntMsg"])
            try:
                channel_id = message.forward_from_chat.id
                channel_title = message.forward_from_chat.title
                
                admins = []
                async for admin in client.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                    admins.append(admin.user.id)
                userid = message.from_user.id
                channel_data = await create_channel(user_id=userid, channel_id=channel_id, channel_name=channel_title, vus=0, reactions=0, likes=0, shares=0, admins=admins)
                await message.delete()
                await m.edit(lang["alert"]["channel_added"].format(channel_title))
                await asyncio.sleep(10)
                await m.delete()
            except Exception as e:
                await m.edit(lang["alert"]["error_adding_channel"].format(channel_title, str(e)))
                await asyncio.sleep(10)
                await m.delete()
        else:
            await m.edit(lang["alert"]["invalid_token"])
            await asyncio.sleep(10)
            await m.delete()
