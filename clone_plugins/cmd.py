from collections import defaultdict
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime
from clone_plugins import clbdata

from database.postdata import create_post, get_post_by_id, update_post
from database.taskdata import delete_task, get_task_by_id, update_task
from database.userdata import *
from config import *
from models.postmodel import Post, Author, Media
from models.taskmodel import Task
from utils.helper import ask_input_btn_str, bot_is_admin, extract_post_data, get_channel_info, get_user_parsemode, getedit_keyboard, sendpost, updatepostinchannel
from utils.lang import LangManager

lang_manager = LangManager(default_lang="fr")

mode = False
taskid = None
add_channelmode = False
messageid = None
posts = None
last_editmessageid = None
last_editermessage = None
shedouling_time = None
edimode = False
editpostid ={}



@Client.on_message(filters.command(["start"]) & filters.private)
async def start(client: Client, message: Message):
    global mode, add_channelmode, taskid
    userid = message.from_user.id
    user_info = await get_user(userid)
    add_channelmode = False
    mode = False

    if not user_info:
        lang_str = "fr"
        lang_manager = LangManager(lang_str)
        lang = lang_manager.get_lang()

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["btn_connect_megabot"], url=f"{MEGABOTURL}")],
            [InlineKeyboardButton(lang["btn"]["chg_lang"], callback_data="change_lang")]
        ])
        await message.reply(lang["clone"]["no_user_found"], reply_markup=keyboard)
        return

    lang_str = user_info.get("lang", "fr")
    lang_manager = LangManager(lang_str)
    lang = lang_manager.get_lang()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(lang["btn"]["create_post"], callback_data="create_post"),
         InlineKeyboardButton(lang["btn"]["edit_post"], callback_data="edit_post")],
        [InlineKeyboardButton(lang["btn"]["schedule_post"], callback_data="schedule_post"),
         InlineKeyboardButton(lang["btn"]["stats"], callback_data="stats")],
        [InlineKeyboardButton(lang["btn"]["btn_settings"], url=f"{MEGABOTURL}/settings")],
    ])

    await message.reply(lang["clone"]["welcome"].format(message.from_user.mention), reply_markup=keyboard)
    if taskid :
            await delete_task(taskid)
            taskid = None


@Client.on_message((filters.forwarded & filters.private) | (filters.incoming & filters.private))
async def createte_bot(client: Client, message: Message):
    global mode, posts, last_editmessageid, messageid, taskid , last_editermessage, edimode, editpostid, add_channelmode
    userid = message.from_user.id
    userinfo = await get_user(userid)
    settings = userinfo.get("settings", {})
    format_format = settings.get("format_format", "normal")
    lang_str = userinfo.get("lang", "fr")
    lang_manager = LangManager(lang_str)
    lang = lang_manager.get_lang()
    
    # ---------- 1. Cas d'annulation ----------
    if message.text == lang["btn"]["btn_cancel"]:
        await message.delete()
        mode = False
        edimode = False
        add_channelmode = False
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["create_post"], callback_data="create_post"),
             InlineKeyboardButton(lang["btn"]["edit_post"], callback_data="edit_post")],
            [InlineKeyboardButton(lang["btn"]["schedule_post"], callback_data="schedule_post"),
             InlineKeyboardButton(lang["btn"]["stats"], callback_data="stats")],
            [InlineKeyboardButton(lang["btn"]["btn_settings"], url=f"{MEGABOTURL}/settings")]
        ])
        await message.reply(lang["clone"]["welcome"].format(message.from_user.mention), reply_markup=keyboard)
        if taskid :
            await delete_task(taskid)
            taskid = None
        return
    
    elif message.text == lang["btn"]["send_post"]:
        
        """"Confirmation de l'envoi du message"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["btn_cancel"], callback_data=f"cancel_sendpost_{taskid}")],
            [InlineKeyboardButton(lang["btn"]["send_post"], callback_data=f"sendpost_{taskid}")],
            [InlineKeyboardButton(lang["btn"]["btn_save"], callback_data=f"savepost_{taskid}")],
            [InlineKeyboardButton(lang["btn"]["btn_preview"], callback_data=f"previewpost_{taskid}")]
        ])
        await message.reply(lang["clone"]["confirm_sendpost"].format(message.from_user.mention), reply_markup=keyboard)
        # await sendpost(client=client, taskid=taskid, user_id=userid, lang=lang)
        
    elif message.text == lang["btn"]["btn_preview"]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["btn_preview"], callback_data=f"previewpost_{taskid}")]
        ])
        await client.send_message(chat_id=message.chat.id, text=lang["clone"]["preview"], reply_markup=keyboard)
        
    elif message.text == lang["btn"]["btn_save"]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["btn_save"], callback_data=f"savepost_{taskid}")]
        ])
        await client.send_message(chat_id=message.chat.id, text=lang["clone"]["save"], reply_markup=keyboard)

    # ---------- 2. Cas Mode Création Actif ----------
    elif mode:
        if message.text == [
            lang["btn"]["btn_cancel"], 
            lang["btn"]["send_post"], 
            lang["btn"]["btn_save"], 
            lang["btn"]["btn_preview"]
        ]:
            return

        m = await message.reply(lang["alert"]["init_task"])
        
        parse_mode = await get_user_parsemode(enums, format_format)

        copied_messageinfo = await extract_post_data(message)
        fileid = copied_messageinfo.get("file_id")
        caption = copied_messageinfo.get("caption", "")
        message_id = copied_messageinfo.get("message_id")
        text = copied_messageinfo.get("text")
        filetype = copied_messageinfo.get("file_type")
        caption_entities = copied_messageinfo.get("caption_entities")

        keyboard = await getedit_keyboard(lang, caption, fileid, None, None, message_id, taskid)
        if text:
            caption = text
        author = Author(id=userid, name="", photo_url="")
        media = Media(url=fileid, type=filetype) if fileid else None
        posts = Post(
            id=message_id,
            author=author,
            text=caption,
            media=[media] if media else [],
            buttons=[],
            likes=[],
            timestamp=datetime.now()
        )
        postkeyboard = posts.to_inline_keyboard()
        await message.delete()

        reply_markup = postkeyboard if postkeyboard else None
        try:
            await m.edit(lang["alert"]["init_post"])
            await create_post(posts)  
            if taskid:
                task = await get_task_by_id(taskid) 
                if task:                                 
                    tasks = Task(
                        id=int(taskid),
                        user_id=userid,
                        channels_id=task.channels_id,
                        posts_id=task.posts_id
                    )
                    tasks.add_post(posts.id)
                    await update_task(taskid, tasks.model_dump())
        except Exception as e:
            await message.reply(lang["alert"]["error"])
        await m.delete()
        sent_message = None
        if message.photo:
            sent_message = await message.reply_photo(fileid, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        elif message.video:
            sent_message = await message.reply_video(fileid, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        elif message.document:
            sent_message = await message.reply_document(fileid, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        elif message.audio:
            sent_message = await message.reply_audio(fileid, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        elif message.voice:
            sent_message = await message.reply_voice(fileid, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
        elif message.sticker:
            sent_message = await message.reply_sticker(message.sticker.file_id, reply_markup=reply_markup)
        else:
            sent_message = await message.reply(text=text, reply_markup=reply_markup, protect_content=True, parse_mode=parse_mode)

        editer = await message.reply(lang["alert"]["continue_editing"], reply_markup=keyboard)
        if sent_message:
            last_editmessageid = sent_message.id
        if editer:
            last_editermessage = editer
            
    # ---------- 5. Cas d'édition d'un message ----------
    elif edimode:
        if message.text == [
            lang["btn"]["btn_cancel"], 
            lang["btn"]["send_post"], 
            lang["btn"]["btn_save"], 
            lang["btn"]["btn_preview"],
            lang["btn"]["send_modif"]
        ]:
            return
        
        # user_settings
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        
        msg = message
        msg_info = await extract_post_data(msg)
        fileid = msg_info.get("file_id")
        caption = msg_info.get("caption")
        message_id = message.forward_from_message_id
        text = msg_info.get("text")
        filetype = msg_info.get("file_type")
        caption_entities = msg_info.get("caption_entities")
        postid = editpostid.setdefault(userid, set())
        postid.add(message_id)
        edimode = False
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["edit_text"], callback_data=f"edit_text_{message_id}")],
            [InlineKeyboardButton(lang["btn"]["edit_buttons"], callback_data=f"edit_buttons_{message_id}")],
            [InlineKeyboardButton(lang["btn"]["edit_likes"], callback_data=f"edit_likes_{message_id}")]
        ])
                                        
        await message.delete()
        sent_message = None
        if msg.photo:
            sent_message = await message.reply_photo(fileid, caption=caption, reply_markup=keyboard, parse_mode=parse_mode)
        elif msg.video:
            sent_message = await message.reply_video(fileid, caption=caption, reply_markup=keyboard, parse_mode=parse_mode)
        elif msg.document:
            sent_message = await message.reply_document(fileid, caption=caption, reply_markup=keyboard, parse_mode=parse_mode)
        elif msg.audio:
            sent_message = await message.reply_audio(fileid, caption=caption, reply_markup=keyboard, parse_mode=parse_mode)
        elif msg.voice:
            sent_message = await message.reply_voice(fileid, caption=caption, reply_markup=keyboard, parse_mode=parse_mode)
        elif msg.sticker:
            sent_message = await message.reply_sticker(msg.sticker.file_id, reply_markup=keyboard)
        else:
            sent_message = await message.reply(text=text, reply_markup=keyboard, protect_content=True, parse_mode=parse_mode)

        if sent_message:
            last_editmessageid = sent_message.id
            last_editermessage = message

    # ---------- 6. Cas d'édition d'un message ----------
    elif message.text == lang["btn"]["send_modif"]:
        messageid = list(editpostid.get(userid, set()))[0]
        m = await updatepostinchannel(client, messageid, userid, lang)
        editpostid.pop(userid, None)
        if m:
            await message.reply(lang["alert"]["modify_success"])
        else:
            await message.reply(lang["alert"]["modify_error"])

    # ---------- 4. Cas Par Défaut (exemple : message transféré non valide / ajout de canal) ----------
    else:
        if not message.forward_from_chat:
            if not add_channelmode:
                return
            await message.reply(lang["alert"]["invalid_forward"])
            return
        channel_id = message.forward_from_chat.id
        is_admin = await bot_is_admin(client, channel_id)
        if not is_admin:
            await message.reply(lang["presencerequest"].format(channel_id))
            return
        channel_info = await get_channel_info(channel_id, client)
        if not add_channelmode:
            return
        channelid = channel_info["id"]
        channeltitle = channel_info["title"]
        channeladmins = channel_info["admins"]
        me = await client.get_me()
        botid = me.id
        await create_channel(userid, channelid, channeltitle, botid, 0, 0, 0, channeladmins)
        await message.delete()
        await message.reply(lang["alert"]["channel_added"].format(channeltitle))
    
    
