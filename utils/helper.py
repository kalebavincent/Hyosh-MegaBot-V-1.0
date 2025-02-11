import asyncio
import re
from typing import Dict
import uuid
from pyrogram import enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from pyrogram.errors import MessageNotModified, MessageIdInvalid
from pyromod.exceptions import ListenerTimeout
from pyrogram.errors import RPCError
from config import MEGABOTURL
from database.taskdata import delete_task, get_task_by_id, update_task
from database.userdata import get_user
from models.postmodel import button_parser, likes_emoji_parser, Post
from database.postdata import create_post, get_post_by_id, get_post_by_unique_id, update_post
from models.taskmodel import Task



async def get_channel_info(channel_id, client):
    try:
        app = client
        channel_id = int(channel_id)
        channel = await app.get_chat(channel_id)
        admins = []
        async for admin in client.get_chat_members(channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins.append(admin.user.id)
        channel_info = {
            "id": channel.id,
            "title": channel.title,
            "username": channel.username,
            "type": channel.type,
            "description": channel.description,
            "members_count": channel.members_count,
            "invite_link": channel.invite_link,
            "admins": admins
        }
        return channel_info
    except Exception as e:
        return None
    
def is_bot(user):
    return user.is_bot

async def get_channel_admins(client, channel_id):
    try:
        admins = []
        async for admin in client.get_chat_members(int(channel_id), filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins.append({
                "id": admin.user.id,
                "name": admin.user.first_name,
                "is_bot": admin.user.is_bot  
            })
        return admins
    except Exception as e:
        return []

async def extract_post_data(message):
    """
    Extrait les données d'un message et les retourne sous forme de dictionnaire.
    Args:
        message (Message): Un objet message contenant les informations du message.
    Returns:
        dict: Un dictionnaire contenant les données extraites du message, y compris l'ID du message, la légende, les entités de légende, le texte, le type de fichier (le cas échéant), et un indicateur si le message est privé.
    Exemple d'utilisation:
        message = ...  # Un objet message reçu
        post_data = await extract_post_data(message)
        print(post_data)
    """
    caption = message.caption if message.caption else ""
    text = message.text
    file_id = None
    caption_entities = message.caption_entities if message.caption_entities else None  # Récupération des entités
    filetype = None
    if message.photo:
        file_id = message.photo.file_id
        filetype = "photo"
    elif message.video:
        file_id = message.video.file_id
        filetype = "video"
    elif message.document:
        file_id = message.document.file_id
        filetype = "document"
    elif message.audio:
        file_id = message.audio.file_id
        filetype = "audio"
    elif message.voice:
        file_id = message.voice.file_id
        filetype = "voice"
    elif message.sticker:
        file_id = message.sticker.file_id
        filetype = "sticker"
    elif message.animation:
        file_id = message.animation.file_id
        filetype = "animation"

    is_private = message.chat.type == "private"

    post_data = {
        "message_id": message.id,
        "caption": caption,
        "caption_entities": caption_entities,  
        "text": text,
        "is_private": is_private
    }

    if file_id:
        post_data["file_id"] = file_id
        post_data["file_type"] = filetype

    return post_data


    
async def ask_for_emojis(client, user_id, lang):
    """Demande à l'utilisateur d'envoyer ses emojis et retourne la réponse"""
    try:
        response = await client.ask(
            user_id,
            lang["question"]["input_emojis"],
            timeout=30
        )
        return response if isinstance(response, Message) else None
    except TimeoutError:
        
        return None

async def ask_input_btn_str(client, user_id, lang):
    try:
        response = await client.ask(
            user_id,
            lang["question"]["input_btn_str"],
            timeout=30
        )

        if isinstance(response, Message) and response.text:
            return response.text

        return None

    except asyncio.TimeoutError:
        await client.send_message(user_id, lang["alert"]["timeout_retry"])
        return None

    except RPCError as e:
        print(f"Erreur RPC lors de la demande d'entrée de bouton : {e}")
        return None

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return None


async def bot_is_admin(client, channel_id):
    """Vérifie si le bot est administrateur du canal"""
    me = await client.get_me()
    bot_id = me.id
    channel_admins = await get_channel_admins(client, channel_id)
    if not channel_admins:
        return False
    for admin in channel_admins:
        if admin["id"] == bot_id:
            return True
    return False
    
async def getedit_keyboard(lang, txt, media, buttons, likes, message_id, taskid=None):
    """
    Crée un clavier de modification pour une publication existante en fonction des données fournies.

    :param lang: Langue utilisée pour afficher les messages.
    :param txt: Texte de la publication.
    :param media: Médias associés à la publication (photo, vidéo, etc.).
    :param buttons: Liste des boutons existants dans la publication.
    :param likes: Nombre de likes ou des interactions avec la publication.
    :param message_id: ID du message pour l'édition.
    :return: Un clavier interactif avec des options de modification.
    """
    
    keyboard = []
    
    if txt:
        keyboard.append([InlineKeyboardButton(lang["btn"]["edit_text"], callback_data=f"edit_text_{message_id}")])
    else:
        keyboard.append([InlineKeyboardButton(lang["btn"]["add_text"], callback_data=f"add_text_{message_id}")])
    
    if media:
        keyboard.append([InlineKeyboardButton(lang["btn"]["edit_media"], callback_data=f"edit_media_{message_id}")])
    else:
        keyboard.append([InlineKeyboardButton(lang["btn"]["add_media"], callback_data=f"add_media_{message_id}")])

    if buttons:
        keyboard.append([InlineKeyboardButton(lang["btn"]["edit_buttons"], callback_data=f"edit_buttons_{message_id}")])
        keyboard.append([InlineKeyboardButton(lang["btn"]["btn_rmbtn"], callback_data=f"rmbtn_{message_id}")])
    else:
        keyboard.append([InlineKeyboardButton(lang["btn"]["add_buttons"], callback_data=f"add_buttons_{message_id}")])

    if likes:
        keyboard.append([InlineKeyboardButton(f"{lang['btn']['edit_likes']}", callback_data=f"edit_likes_{message_id}")])
        keyboard.append([InlineKeyboardButton(lang["btn"]["btn_rmlike"], callback_data=f"rmlike_{message_id}")])
    else:
        keyboard.append([InlineKeyboardButton(lang["btn"]["add_likes"], callback_data=f"add_likes_{message_id}")])

    keyboard.append([InlineKeyboardButton(lang["btn"]["annuler"], callback_data=f"cencel_edit_{taskid}_{message_id}")])

    return InlineKeyboardMarkup(keyboard)
    
    
    
async def get_user_parsemode(enums, format_format):
    
    if format_format == "normal":
        return enums.ParseMode.HTML
    elif format_format == "markdown":
        return enums.ParseMode.MARKDOWN
    elif format_format == "html":
        return enums.ParseMode.HTML
    else:
        return enums.ParseMode.MARKDOWN

def is_valid_button_format(buttons_str: str) -> bool:
    """
    Vérifie si le format des boutons est valide.
    Retourne True si le format est correct, sinon False.
    """
    try:
        buttons = button_parser(buttons_str)
        return bool(buttons)  
    except Exception:
        return False

def is_valid_emoji_format(emoji_text: str) -> bool:
    """
    Vérifie si le format des emojis est valide.
    Retourne True si le format est correct, sinon False.
    """
    parsed = likes_emoji_parser(emoji_text)   

    if isinstance(parsed, str):  
        return False

    return bool(parsed)  





async def sendpost(client, taskid, user_id, lang):
    """Envoie un message de post à tous les canaux de la tâche en respectant les paramètres utilisateur et protège le contenu multimédia."""
    
    task = await get_task_by_id(taskid)
    if not task:
        print("⚠️ Tâche introuvable.")
        await client.send_message(chat_id=user_id, text=lang["alert"]["task_not_found"])
        return
    
    user_info = await get_user(user_id)
    settings = user_info.get("settings", {})

    format_format = settings.get("format_format", "html")
    protected_status = settings.get("protected_msg", False)
    notifications_status = settings.get("notifications", False)
    auto_delete_status = settings.get("auto_delete", False)
    link_preview_statut = settings.get("link_preview", True)
    shedoul_time = int(settings.get("schedule_time", 0))
    print(shedoul_time)
    delay_time = int(settings.get("delay_time", 0))  

    if delay_time == 0:
        auto_delete_status = False

    format_format = await get_user_parsemode(enums=enums, format_format=format_format)

    channels = task.channels_id
    posts_id = task.posts_id
    success = 0
    failed = 0
    status = ""
    canalcount = len(channels)
    postscount = len(posts_id)

    if shedoul_time > 0:
        await client.send_message(chat_id=user_id, text=lang["alert"]["schedule_time_msg"].format(canalcount, canalcount, shedoul_time), reply_markup=None)
        keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(lang["btn"]["create_post"], callback_data="create_post"),
         InlineKeyboardButton(lang["btn"]["edit_post"], callback_data="edit_post")],
        [InlineKeyboardButton(lang["btn"]["schedule_post"], callback_data="schedule_post"),
         InlineKeyboardButton(lang["btn"]["stats"], callback_data="stats")],
        [InlineKeyboardButton(lang["btn"]["btn_settings"], url=f"{MEGABOTURL}/settings")],
    ])
        await client.send_message(chat_id=user_id, text=lang["clone"]["welcome"],reply_markup=keyboard)
        await asyncio.sleep(shedoul_time)

    for message_id in posts_id:
        post_data = await get_post_by_id(int(message_id))
        if not post_data:
            print(f"⚠️ Post {message_id} introuvable.")
            continue

        caption = post_data.text or ""
        skeyboard = post_data.to_inline_keyboard()

        for channel in channels:
            try:
                sent_message = None
                common_args = {
                    "caption": caption,
                    "reply_markup": skeyboard,
                    "parse_mode": format_format,
                    "disable_notification": not notifications_status,
                    "protect_content": protected_status
                }

                # Gestion des médias
                if post_data.media and post_data.media[0].url and post_data.media[0].type:
                    fileid = post_data.media[0].url
                    media_type = post_data.media[0].type.lower()

                    if 'photo' in media_type:
                        sent_message = await client.send_photo(chat_id=channel, photo=fileid, **common_args)
                    elif 'video' in media_type:
                        sent_message = await client.send_video(chat_id=channel, video=fileid, **common_args)
                    elif 'document' in media_type:
                        sent_message = await client.send_document(chat_id=channel, document=fileid, **common_args)
                    elif 'audio' in media_type:
                        sent_message = await client.send_audio(chat_id=channel, audio=fileid, **common_args)
                    elif 'voice' in media_type:
                        sent_message = await client.send_voice(chat_id=channel, voice=fileid, **common_args)
                    elif 'sticker' in media_type:
                        sent_message = await client.send_sticker(chat_id=channel, sticker=fileid, reply_markup=skeyboard)
                    else:
                        print(f"⚠️ Type de média {media_type} non supporté pour le post {message_id}.")
                        continue
                else:
                    sent_message = await client.send_message(
                        chat_id=channel,
                        text=caption,
                        disable_web_page_preview=not link_preview_statut,
                        parse_mode=format_format,
                        reply_markup=skeyboard,
                        disable_notification=not notifications_status,
                        protect_content=protected_status
                    )

                # Gestion du message envoyé
                if sent_message:
                    postid = sent_message.id
                    unique_id = await generate_unique_id(postid, channel)
                    
                    new_post = Post(
                        id=sent_message.id,
                        author=post_data.author,
                        text=post_data.text,
                        media=post_data.media,
                        likes=post_data.likes,
                        buttons=post_data.buttons,
                        unique_id=unique_id
                    )
                    new_post.mark_completed()

                    await asyncio.sleep(3)

                    updated_skeyboard = new_post.to_inline_keyboard()
                    try:
                        await create_post(new_post)
                        success += 1
                        status += f"✅  `{channel}` `{sent_message.id}` `{unique_id}`\n"
                    except Exception as e:
                        status += f"❌  {channel} {sent_message.id} {unique_id}. Err: {e}\n"
                        
                    if updated_skeyboard and new_post.likes:
                        await asyncio.sleep(5)
                        await client.edit_message_reply_markup(
                            chat_id=channel,
                            message_id=sent_message.id,
                            reply_markup=updated_skeyboard
                        )

                    if auto_delete_status and delay_time > 0:
                        asyncio.create_task(auto_delete(client, channel, postid, delay_time))

            except Exception as e:
                failed += 1
                status += f"❌  {channel} {sent_message.id if sent_message else 'N/A'} {unique_id if 'unique_id' in locals() else 'N/A'}. Err: {e}\n"
                
    # Supprimer la tâche et envoyer un rapport
    await delete_task(taskid)
    await client.send_message(chat_id=user_id, text=lang["alert"]["report"].format(success, failed, status), reply_markup=None)
    return True

async def auto_delete(client, channel, message_id, delay_time):
    """Supprime automatiquement un message après un délai donné."""
    await asyncio.sleep(int(delay_time))
    try:
        await client.delete_messages(chat_id=channel, message_ids=[message_id])
    except Exception as e:
        pass
    
async def generate_unique_id(postid, channel_id):
    """Génère un identifiant unique de 10 caractères."""
    id = str(uuid.uuid4())
    short_id = id.replace("-", "")[:10]  
    return f"{postid}:{postid}:{short_id}:{channel_id}"




async def edit_keybord_to_post_inchannel(client,unique_id):
    """Edite le clavier inline pour un message dans un canal en fonction des données du post."""
    posts = await get_post_by_unique_id(unique_id)
    post = Post(
        id=posts.id,
        author=posts.author,
        text=posts.text,
        media=posts.media,  
        likes=posts.likes,
        buttons=posts.buttons,
        unique_id=posts.unique_id,
        timestamp=posts.timestamp
    )
    skeyboard = post.to_inline_keyboard()  # Création du clavier inline pour les boutons
    post_id, channel_post_id, short_id, channelid = unique_id.split(":")
    
    try:
      await client.edit_message_reply_markup(
        chat_id=int(channelid),
        message_id=int(post_id),
        reply_markup=skeyboard
    )
    except:
      pass
  

async def updatepostinchannel(client, message_id, user_id, lang):
    """Met à jour uniquement ce qui est modifiable (texte et boutons) sans supprimer ni republier de message média."""
    posts = await get_post_by_id(int(message_id))
    
    if not posts:
        return None

    post = Post(
        id=message_id,
        author=posts.author,
        text=posts.text,
        media=posts.media,
        likes=posts.likes,
        buttons=posts.buttons,
        unique_id=posts.unique_id,
        timestamp=posts.timestamp
    )
    author = posts.author
    authorid = author.id
    if authorid != user_id:
        client.send_message(chat_id=user_id, text=lang["alert"]["ahthor_invalid"])
        return None
    post.mark_completed()
    unique_id = posts.unique_id
    await update_post(message_id, post.model_dump())
    post_id, channel_post_id, short_id, channelid = unique_id.split(":")
    skeyboard = post.to_inline_keyboard()

    try:
        await client.edit_message_text(
            chat_id=int(channelid),
            message_id=int(message_id),
            text=post.text,
            reply_markup=skeyboard
        )

    except MessageNotModified:
        pass
    except (MessageIdInvalid):
        pass
    except Exception as e:
        pass
    return True
