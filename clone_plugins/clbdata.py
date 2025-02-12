import asyncio
from datetime import datetime
from pyrogram import Client,enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton,ReplyKeyboardMarkup
from config import MEGABOTURL
from database.postdata import get_post_by_id, get_post_by_unique_id, update_post, update_post_by_unique_id
from database.taskdata import create_task_for_user, delete_task, get_task_by_id, update_task
from database.userdata import get_channels_by_bot, get_unassigned_channels, get_user, update_user_settings
from models.taskmodel import Task
from utils.helper import edit_keybord_to_post_inchannel, extract_post_data, get_channel_info, get_user_parsemode, getedit_keyboard, is_valid_button_format, is_valid_emoji_format, sendpost
from utils.lang import LangManager
from clone_plugins import cmd
from models.postmodel import Media, Post
import random
user_selected_channels = {}
user_times = {}
PAGE_SIZE = 7
lang_manager = LangManager(default_lang="fr")
async def change_language(client: Client, query: CallbackQuery):
    if lang_manager.current_lang == "fr":
        new_lang = "en"
    elif lang_manager.current_lang == "en":
        new_lang = "ru"
    elif lang_manager.current_lang == "ru":
        new_lang = "shw"
    elif lang_manager.current_lang == "shw":
        new_lang = "arb"
    elif lang_manager.current_lang == "arb":
        new_lang = "indi"
    else:
        new_lang = "fr"
    lang_manager.set_lang(new_lang)  
    lang = lang_manager.get_lang()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(lang["btn"]["btn_connect_megabot"], url=f"{MEGABOTURL}")],
        [InlineKeyboardButton(lang["btn"]["chg_lang"], callback_data="change_lang")]
    ])

    await query.message.edit_text(lang["clone"]["no_user_found"], reply_markup=keyboard)
    await query.answer(lang["lchangSucces"], show_alert=True)


async def send_message_based_on_type(client, chat_id, post, lang, query=None, parse_mode=None):
    caption = post.text
    fileid = post.media[0].url if post.media else None
    keyboard = post.to_inline_keyboard()
    skeybord = keyboard if keyboard else None

    keyboardedit = await getedit_keyboard(lang, caption, fileid, post.buttons, post.likes, post.id)

    if cmd.last_editmessageid and cmd.last_editermessage:
        try:
            await client.delete_messages(chat_id=query.message.chat.id, message_ids=cmd.last_editmessageid)
            await client.delete_messages(chat_id=query.message.chat.id, message_ids=cmd.last_editermessage.id)
        except Exception as e:
            print(f"Erreur de suppression de messages : {e}")

    sent_message = None
    if post.media:
        if post.media[0].url and post.media[0].type:
            if 'photo' in post.media[0].type:
                sent_message = await client.send_photo(chat_id, fileid, caption=caption, reply_markup=skeybord, parse_mode=parse_mode)
            elif 'video' in post.media[0].type:
                sent_message = await client.send_video(chat_id, fileid, caption=caption, reply_markup=skeybord, parse_mode=parse_mode)
            elif 'document' in post.media[0].type:
                sent_message = await client.send_document(chat_id, fileid, caption=caption, reply_markup=skeybord, parse_mode=parse_mode)
            elif 'audio' in post.media[0].type:
                sent_message = await client.send_audio(chat_id, fileid, caption=caption, reply_markup=skeybord, parse_mode=parse_mode)
            elif 'voice' in post.media[0].type:
                sent_message = await client.send_voice(chat_id, fileid, caption=caption, reply_markup=skeybord)
            elif 'sticker' in post.media[0].type:
                sent_message = await client.send_sticker(chat_id, fileid, reply_markup=skeybord)
    else:
        sent_message = await client.send_message(chat_id, caption, reply_markup=skeybord, parse_mode=parse_mode)

    if sent_message:
        cmd.last_editmessageid = sent_message.id

    editer = await client.send_message(chat_id, lang["alert"]["continue_editing"], reply_markup=keyboardedit)
    if editer:
        cmd.last_editermessage = editer
        


@Client.on_callback_query()
async def clbdata(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id  
    me = await client.get_me()
    bot_id = me.id
    userinfo = await get_user(user_id)
    lang_manager = LangManager(default_lang="fr")

    if userinfo:
        lang_manager = LangManager(userinfo.get("lang", "fr"))
    
    lang = lang_manager.get_lang()

    if data == "change_lang":
        await change_language(client, query)
    
    elif data == "clone_main":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["create_post"], callback_data="create_post"),
             InlineKeyboardButton(lang["btn"]["edit_post"], callback_data="edit_post")],
            [InlineKeyboardButton(lang["btn"]["schedule_post"], callback_data="schedule_post"),
             InlineKeyboardButton(lang["btn"]["stats"], callback_data="stats")],
            [InlineKeyboardButton(lang["btn"]["btn_settings"], url=f"{MEGABOTURL}/settings")]
        ])

        await query.message.edit_text(
            lang["clone"]["welcome"].format(query.from_user.mention),
            reply_markup=keyboard
        )
        cmd.add_channelmode = True
        cmd.mode = False
        cmd.add_channelmode = False
        cmd.add_channelmode = False
        user_selected_channels.pop(user_id, None)
        if cmd.taskid :
            await delete_task(cmd.taskid)
            cmd.taskid = None


    elif data == "add_new_channel":
        cmd.add_channelmode = True
        bot_username = me.username
        add_bot_link = f"https://t.me/{bot_username}?startgroup=true&admin=can_post_messages,can_edit_messages,can_delete_messages,can_invite_users,can_manage_chat,can_change_info,can_pin_messages"

        await query.message.edit_text(
            lang["clone"]["add_chnl_in_clone"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="clone_main"),
                 InlineKeyboardButton(lang["btn"]["btn_addto_grp"], url=add_bot_link)]
            ])
        )


    elif data.startswith("create_post") or data.startswith("toggle_channel_"):
        selected_channels = user_selected_channels.setdefault(user_id, set())

        page = 1
        if "_page_" in data:
            parts = data.split("_page_")
            data = parts[0]
            page = int(parts[1])

        if data.startswith("toggle_channel_"):
            channel_id = int(data.split("_")[-1])

            channel_info = await get_channel_info(channel_id, client)
            if not channel_info:
                await query.answer(lang["alert"]["bot_is_admin_required"].format(channel_id), show_alert=True)
                return  

            if channel_id in selected_channels:
                selected_channels.remove(channel_id)
            else:
                selected_channels.add(channel_id)

        channels = await get_channels_by_bot(user_id, bot_id)
        unassigned_channels = await get_unassigned_channels(user_id)

        if not channels and not unassigned_channels:
            await query.message.edit_text(
                lang["alert"]["no_channels"],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="clone_main")],
                    [InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel")],
                ])
            )


        all_channels = channels + unassigned_channels
        total_pages = (len(all_channels) + PAGE_SIZE - 1) // PAGE_SIZE
        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        paginated_channels = all_channels[start:end]

        keyboard = []
        for channel in paginated_channels:
            channel_id = channel["id"]
            is_selected = channel_id in selected_channels

            channel_button = InlineKeyboardButton(
                channel["name"], callback_data=f"toggle_channel_{channel_id}_page_{page}"
            )
            selector_button = InlineKeyboardButton(
                "✅" if is_selected else "➖", callback_data=f"toggle_channel_{channel_id}_page_{page}"
            )

            keyboard.append([channel_button, selector_button])

        if selected_channels:
            create_callback = "create_for_select_"
            keyboard.append([InlineKeyboardButton(lang["btn"]["create_post"], callback_data=create_callback)])

        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("«", callback_data=f"create_post_page_{page-1}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("»", callback_data=f"create_post_page_{page+1}"))

        if nav_buttons:
            keyboard.append(nav_buttons)

        keyboard.append([
                    InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="clone_main"),
                    InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                ])


        await query.message.edit_text(lang["alert"]["select_channel"], reply_markup=InlineKeyboardMarkup(keyboard))

    elif  data.startswith("create_for_select_"):
        channel_ids_part = data[len("create_for_select_"):]
        

        channel_ids = list(user_selected_channels.get(user_id, set()))
        taskid = random.randint(1000, 9999)
        cmd.taskid = taskid
        task = Task(
            id=taskid,
            user_id=query.from_user.id,
            channels_id=channel_ids,  
            status="pending",  
            schedule_delay=None, 
            posted_date=datetime.now()
        )
        
        task_id = await create_task_for_user(task)
        cmd.taskid = taskid
        
        buttons = [
            [KeyboardButton(lang["btn"]["send_post"]), KeyboardButton(lang["btn"]["btn_save"])],  
            [KeyboardButton(lang["btn"]["btn_cancel"]), KeyboardButton(lang["btn"]["btn_preview"])],   
        ]

        await query.message.edit_text(
            lang["clone"]["create_post_msg"].format(", ".join(map(str, channel_ids))),
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True,  
                one_time_keyboard=False  
            )
        )
        cmd.mode = True
        cmd.edimode = False     

    
    elif data.startswith("add_buttons_"):
        message_id = int(data.split("_")[2])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        await query.answer(lang["question"]["input_btn_str"], show_alert=True)

        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["input_btn_str"],
                timeout=1500
            )

            if response and response.text:
                add_btnmode = response.text.strip()
                if is_valid_button_format(add_btnmode): 
                    posts = await get_post_by_id(int(message_id))
                    posts = Post(id=message_id, author=posts.author, text=posts.text, media=posts.media, likes=posts.likes, buttons=posts.buttons, unique_id=posts.unique_id, timestamp=posts.timestamp)
                    posts.add_buttons(add_btnmode)
                    await update_post(message_id, posts.model_dump())
                    await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
                else:
                    await query.message.reply_text(lang["alert"]["invalid_btn_format"]) 
            else:
                await query.message.reply_text(lang["alert"]["no_added_btns"])

        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e:
            print(f"Erreur lors de l'ajout de boutons : {e}")

            
    elif data.startswith("add_likes_"):
        message_id = int(data.split("_")[2])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)

        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["input_likes"],
                timeout=1500
            )

            if response and response.text:
                add_likemode = response.text.strip()
                if is_valid_emoji_format(add_likemode):
                    posts = await get_post_by_id(int(message_id))
                    posts = Post(id=message_id, author=posts.author, text=posts.text, media=posts.media, likes=posts.likes, buttons=posts.buttons, unique_id=posts.unique_id, timestamp=posts.timestamp)
                    posts.add_emoji(add_likemode)
                    await update_post(message_id, posts.model_dump())
                    await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
                else:
                    await query.message.reply_text(lang["alert"]["invalid_emoji_format"])
            else:
                await query.message.reply_text(lang["alert"]["no_added_likes"])

        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e:
            print(f"Erreur lors de l'ajout des émoticônes : {e}")

            
    elif data.startswith("add_text_"):
        message_id = int(data.split("_")[2])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)

        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["input_caption"],
                timeout=1500
            )

            if response and response.text:
                add_textmode = response.text.strip()
                posts = await get_post_by_id(int(message_id))
                posts = Post(id=message_id, author=posts.author, text=posts.text, media=posts.media, likes=posts.likes, buttons=posts.buttons, unique_id=posts.unique_id, timestamp=posts.timestamp)
                posts.add_text(add_textmode)
                await update_post(message_id, posts.model_dump())
                await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
            else:
                await query.message.reply_text(lang["alert"]["no_added_text"])

        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e:
            print(f"Erreur lors de l'ajout du texte : {e}")
            
    elif data.startswith("add_media_"):
        message_id = int(data.split("_")[2])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)

        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["input_media"],
                timeout=1500
            )

            if response and (response.photo or response.video or response.document):
                if response.photo:
                    media_file_id = response.photo.file_id
                elif response.video:
                    media_file_id = response.video.file_id
                elif response.document:
                    media_file_id = response.document.file_id
                else:
                    media_file_id = None

                if media_file_id:
                    messageinfo = await extract_post_data(response)
                    mediatype = messageinfo.get("file_type")
                    filid = messageinfo.get("file_id")

                    print(filid)
                    print(mediatype)

                    posts = await get_post_by_id(int(message_id))
                    posts = Post(
                        id=message_id,
                        author=posts.author,
                        text=posts.text,
                        media=posts.media,
                        likes=posts.likes,
                        buttons=posts.buttons,
                        unique_id=posts.unique_id,
                        timestamp=posts.timestamp
                    )
                    posts.add_media(Media(url=filid, type=mediatype))
                    await update_post(message_id, posts.model_dump())
                    await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
                else:
                    await query.message.reply_text(lang["alert"]["no_added_media"])

        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e:
            print(f"Erreur lors de l'ajout du média : {e}")
            
    elif data.startswith("edit_text_"):
        message_id = int(data.split("_")[2])
        print(message_id)
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        await query.answer(lang["question"]["rinput_caption"], show_alert=True)
        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["rinput_caption"],
                timeout=1500
            )
            if response and response.text:
                posts = await get_post_by_id(int(message_id))
                posts = Post(id=message_id, author=posts.author, text=response.text, media=posts.media, likes=posts.likes, buttons=posts.buttons,unique_id=posts.unique_id, timestamp=posts.timestamp)
                await update_post(message_id, posts.model_dump())
                await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
            else:
                await query.message.reply_text(lang["alert"]["no_added_text"])
        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e:
            print(f"Erreur lors de l'ajout du texte : {e}")
    
    elif data.startswith("edit_media_"):
        message_id = int(data.split("_")[2])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        await query.answer(lang["question"]["input_media"], show_alert=True)
        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["input_media"],
                timeout=1500
            )
            if response and (response.photo or response.video or response.document):
                if response.photo:
                    media_file_id = response.photo.file_id
                elif response.video:
                    media_file_id = response.video.file_id
                elif response.document:
                    media_file_id = response.document.file_id
                else:
                    media_file_id = None
                if media_file_id:
                    messageinfo = await extract_post_data(response)
                    mediatype = messageinfo.get("file_type")
                    filid = messageinfo.get("file_id")
                    posts = await get_post_by_id(int(message_id))
                    posts = Post(
                        id=message_id,
                        author=posts.author,
                        text=posts.text,
                        media=posts.media,
                        likes=posts.likes,
                        buttons=posts.buttons,
                        unique_id=posts.unique_id,
                        timestamp=posts.timestamp
                    )
                    posts.add_media(Media(url=filid, type=mediatype))
                    await update_post(message_id, posts.model_dump())
                    await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
                else:
                    await query.message.reply_text(lang["alert"]["no_added_media"])
            else:
                await query.message.reply_text(lang["alert"]["no_added_media"])
                        
        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e:
            print(f"Erreur lors de l'ajout du média : {e}")
            
    elif data.startswith("edit_buttons_"):
        message_id = int(data.split("_")[2])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        await query.answer(lang["question"]["input_btn_str"], show_alert=True)
        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["input_btn_str"],
                timeout=1500
            )
            if response and response.text:
                add_btnmode = response.text.strip()
                if is_valid_button_format(add_btnmode): 
                    posts = await get_post_by_id(int(message_id))
                    posts = Post(id=message_id, author=posts.author, text=posts.text, media=posts.media, likes=posts.likes, buttons=posts.buttons, unique_id=posts.unique_id, timestamp=posts.timestamp)
                    posts.add_buttons(add_btnmode)
                    await update_post(message_id, posts.model_dump())
                    await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
                else:
                    await query.message.reply_text(lang["alert"]["invalid_btn_format"]) 
            else:
                await query.message.reply_text(lang["alert"]["no_added_btns"])
        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e:
            print(f"Erreur lors de l'ajout des boutons : {e}")
            
    elif data.startswith("rmbtn_"):
        message_id = int(data.split("_")[1])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        posts = await get_post_by_id(int(message_id))
        posts = Post(id=message_id, author=posts.author, text=posts.text, media=posts.media, likes=posts.likes, buttons=posts.buttons, unique_id=posts.unique_id, timestamp=posts.timestamp)
        posts.remove_all_buttons()
        await update_post(message_id, posts.model_dump())
        if cmd.last_editmessageid and cmd.last_editermessage:
            try:
                await client.delete_messages(chat_id=query.message.chat.id, message_ids=cmd.last_editmessageid)
                await client.delete_messages(chat_id=query.message.chat.id, message_ids=cmd.last_editermessage.id)
            except Exception as e:
                print(f"Erreur de suppression de messages : {e}")
        await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
    
    elif data.startswith("rmlike_"):
        message_id = int(data.split("_")[1])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        posts = await get_post_by_id(int(message_id))
        posts = Post(id=message_id, author=posts.author, text=posts.text, media=posts.media, likes=posts.likes, buttons=posts.buttons, unique_id=posts.unique_id, timestamp=posts.timestamp)
        posts.remove_all_emoji()
        await update_post(message_id, posts.model_dump())
        if cmd.last_editmessageid and cmd.last_editermessage:
            try:
                await client.delete_messages(chat_id=query.message.chat.id, message_ids=cmd.last_editmessageid)
                await client.delete_messages(chat_id=query.message.chat.id, message_ids=cmd.last_editermessage.id)
            except Exception as e:
                print(f"Erreur de suppression de messages : {e}")
        await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
            
    elif data.startswith("edit_likes_"):
        message_id = int(data.split("_")[2])
        settings = userinfo.get("settings", {})
        format_format = settings.get("format_format", "normal")
        parse_mode = await get_user_parsemode(enums, format_format)
        try:
            response = await client.ask(
                query.from_user.id,
                lang["question"]["input_likes"],
                timeout=1500
            )
            if response and response.text:
                add_likemode = response.text.strip()
                if is_valid_emoji_format(add_likemode):
                    posts = await get_post_by_id(int(message_id))
                    posts = Post(id=message_id, author=posts.author, text=posts.text, media=posts.media, likes=posts.likes, buttons=posts.buttons, unique_id=posts.unique_id, timestamp=posts.timestamp)
                    posts.add_emoji(add_likemode)
                    await update_post(message_id, posts.model_dump())
                    await send_message_based_on_type(client, query.from_user.id, posts, lang, query, parse_mode)
                else:
                    await query.message.reply_text(lang["alert"]["invalid_emoji_format"])
            else:
                await query.message.reply_text(lang["alert"]["no_added_likes"])
        except asyncio.TimeoutError:
            await query.message.reply_text(lang["alert"]["timeout"])
        except Exception as e: 
            print(f"Erreur lors de l'ajout des émoticônes : {e}")
            
    elif data.startswith("cencel_edit_"):
        taskid = int(data.split("_")[2])
        message_id = int(data.split("_")[3])
        user_id = query.from_user.id 
        try:
          if taskid:
                task = await get_task_by_id(taskid) 
                print(task)
                if task:                                 
                    tasks = Task(
                        id=int(taskid),
                        user_id=user_id,
                        channels_id=task.channels_id,
                        posts_id=task.posts_id
                    )
                    tasks.remove_post(message_id)
                    print(tasks)
                    await update_task(taskid, tasks.model_dump())
                    await query.message.reply_text(lang["alert"]["task_cenceled"])
                    await asyncio.sleep(3)
                    await query.message.delete()
        except:
          print('An exception occurred')
          
    elif data.startswith("likeemoji_"):
        userid = query.from_user.id
        lang_manager = LangManager(default_lang="fr")
        lang = lang_manager.get_lang()
        parts = data.split("_")

        if len(parts) < 3:
            await query.answer(lang["alert"]["post_in_edit_mode"])
            return

        unique_id = parts[1]
        emojis = parts[2]

        # Vérification et séparation des emojis et des likes
        emoji_parts = emojis.split(" ")
        if len(emoji_parts) < 2:
            await query.answer(lang["alert"]["post_in_edit_mode"])
            return
        
        emoji = emoji_parts[0]
        likecount = emoji_parts[1]

        # Vérification du format de unique_id
        unique_id_parts = unique_id.split(":")
        if len(unique_id_parts) != 4:
            # ⚠️ Post en édition, on informe l'utilisateur
            await query.answer(lang["alert"]["post_in_edit_mode"])
            return

        post_id, channel_post_id, short_id, channel_id = unique_id_parts

        postss = await get_post_by_unique_id(unique_id)
        if postss is None:
            await query.answer(lang["alert"]["post_not_found"])
            return

        post = Post(
            id=post_id,
            author=postss.author,
            text=postss.text,
            media=postss.media,
            likes=postss.likes,
            buttons=postss.buttons,
            status=postss.status,
            unique_id=postss.unique_id,
            timestamp=postss.timestamp
        )

        poststatus = post.get_post_status()
        if poststatus == 1:
            try:
                post.add_like(int(userid), emoji)
                await update_post_by_unique_id(unique_id, post.model_dump())
                await edit_keybord_to_post_inchannel(client, unique_id)
                await query.answer(lang["alert"]["like_success"])
            except Exception as e:
                await query.answer(lang["alert"]["like_error"])
                print(e)

                
    elif data.startswith("cancel_sendpost_"):
        parts = data.split("_")

        # Vérifier si un ID est présent et valide
        if len(parts) < 3 or not parts[2].isdigit():
            await query.answer(lang["alert"]["no_task_active"], show_alert=True)
            return

        taskid = int(data.split("_")[2])
        parts = data.split("_")

        if len(parts) < 3 or not parts[2].isdigit():
            await query.answer(lang["alert"]["no_task_active"], show_alert=True)
            return
        task = await get_task_by_id(taskid)
        if not task:
            await query.answer(lang["alert"]["task_not_found"])
            return
        await delete_task(taskid)
        await query.message.delete()
        await query.answer(lang["alert"]["task_cenceledsuccess"])
        
    elif data.startswith("sendpost_"):
        parts = data.split("_")

        # Vérifier si un ID est présent et valide
        if len(parts) < 2 or not parts[1].isdigit():
            await query.answer(lang["alert"]["no_task_active"], show_alert=True)
            return

        taskid = int(parts[1])
        task = await get_task_by_id(taskid)

        if not task:
            await query.answer(lang["alert"]["task_not_found"])
            return

        userid = query.from_user.id
        send = await sendpost(client, taskid, userid, lang)

        if send:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(lang["btn"]["create_post"], callback_data="create_post"),
                InlineKeyboardButton(lang["btn"]["edit_post"], callback_data="edit_post")],
                [InlineKeyboardButton(lang["btn"]["schedule_post"], callback_data="schedule_post"),
                InlineKeyboardButton(lang["btn"]["stats"], callback_data="stats")],
                [InlineKeyboardButton(lang["btn"]["btn_settings"], url=f"{MEGABOTURL}/settings")]
            ])

            await query.message.reply(lang["clone"]["welcome"].format(query.from_user.mention), reply_markup=keyboard)

    elif data.startswith("savepost_"):
        parts = data.split("_")

        # Vérifier si un ID est présent et valide
        if len(parts) < 2 or not parts[1].isdigit():
            await query.answer(lang["alert"]["no_task_active"], show_alert=True)
            return

        taskid = int(data.split("_")[1])
        task_id = int(taskid)
        parts = data.split("_")

        if len(parts) < 2 or not parts[1].isdigit():
            await query.answer(lang["alert"]["no_task_active"], show_alert=True)
            return
        task = await get_task_by_id(task_id)
        if task:
            task.mak_saved()
            await update_task(task_id, task.model_dump())
            user_selected_channels.pop(user_id, None)
            cmd.taskid = None
            cmd.mode = False
            await query.answer(lang["alert"]["task_saved"])
        else:
            await query.answer(lang["alert"]["task_not_found"])
    
    elif data.startswith("previewpost_"):
        user_id = query.from_user.id
        parts = data.split("_")

        if len(parts) < 2 or not parts[1].isdigit():
            await query.answer(lang["alert"]["no_task_active"], show_alert=True)
            return
        taskid = int(data.split("_")[1])
        task_id = int(taskid)
        
        task = await get_task_by_id(task_id)
        if not task:        
            await query.answer(lang["alert"]["task_not_found"])
            return
        postis =task.posts_id
        user_info = await get_user(user_id)
        settings = user_info.get("settings", {})

        format_format = settings.get("format_format", "html")
        protected_status = settings.get("protected_msg", False)
        notifications_status = settings.get("notifications", False)
        auto_delete_status = settings.get("auto_delete", False)
        link_preview_statut = settings.get("link_preview", True)
        parse_mode = await get_user_parsemode(enums, format_format)
        for message_id in postis:
            post_data = await get_post_by_id(int(message_id))
            if not post_data:
                await query.answer(lang["alert"]["no_data"])
                continue
            caption = post_data.text or ""
            skeyboard = post_data.to_inline_keyboard()
            try:
                common_args = {
                    "caption": caption,
                    "reply_markup": skeyboard,
                    "parse_mode": parse_mode,
                    "disable_notification": not notifications_status,
                    "protect_content": protected_status
                }

                if post_data.media and post_data.media[0].url and post_data.media[0].type:
                    fileid = post_data.media[0].url
                    media_type = post_data.media[0].type.lower()

                    if 'photo' in media_type:
                        sent_message = await client.send_photo(chat_id=user_id, photo=fileid, **common_args)
                    elif 'video' in media_type:
                        sent_message = await client.send_video(chat_id=user_id, video=fileid, **common_args)
                    elif 'document' in media_type:
                        sent_message = await client.send_document(chat_id=user_id, document=fileid, **common_args)
                    elif 'audio' in media_type:
                        sent_message = await client.send_audio(chat_id=user_id, audio=fileid, **common_args)
                    elif 'voice' in media_type:
                        sent_message = await client.send_voice(chat_id=user_id, voice=fileid, **common_args)
                    elif 'sticker' in media_type:
                        sent_message = await client.send_sticker(chat_id=user_id, sticker=fileid, reply_markup=skeyboard)
                    else:
                        print(f"⚠️ Type de média {media_type} non supporté pour le post {message_id}.")
                        continue
                else:
                    sent_message = await client.send_message(
                        chat_id=user_id,
                        text=caption,
                        disable_web_page_preview=not link_preview_statut,
                        parse_mode=parse_mode,
                        reply_markup=skeyboard,
                        disable_notification=not notifications_status,
                        protect_content=protected_status
                    )
                editkeyboard = await getedit_keyboard(lang, caption, skeyboard, skeyboard, skeyboard, message_id, taskid)
                await query.message.reply(lang["alert"]["continue_editing"], reply_markup=editkeyboard)
            except Exception as e:
                await query.answer(lang["alert"]["error"])
                print(e)

    elif data == "edit_post":
        buttons = [
            [KeyboardButton(lang["btn"]["send_modif"]), KeyboardButton(lang["btn"]["btn_cancel"])]  
        ]
        await query.message.reply_text(
                lang["clone"]["edit_post_msg"].format(query.from_user.mention),                 
                reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True,  
                one_time_keyboard=False  
            )
            )
        cmd.edimode = True
        cmd.mode = False
    
    elif data in ["hs_add", "hs_rem", "min_add", "min_rem", "sec_add", "sec_rem", "schedule_post", "save_schedule", "save_delay", "reset"]:
        user_id = query.from_user.id
        user_times_config = user_times.setdefault(user_id, {"hs": 0, "min": 0, "sec": 30})  

        if data == "hs_add":
            user_times_config["hs"] += 1
        elif data == "hs_rem":
            user_times_config["hs"] = max(user_times_config["hs"] - 1, 0)  
        elif data == "min_add":
            user_times_config["min"] += 10
        elif data == "min_rem":
            user_times_config["min"] = max(user_times_config["min"] - 10, 0)  
        elif data == "sec_add":
            user_times_config["sec"] += 30
        elif data == "sec_rem":
            user_times_config["sec"] = max(user_times_config["sec"] - 30, 30)
        elif data == "reset":
            user_times_config["hs"] = 0
            user_times_config["min"] = 0
            user_times_config["sec"] = 30

        if user_times_config["sec"] >= 60:
            user_times_config["sec"] = 0
            user_times_config["min"] += 1

        if user_times_config["min"] >= 60:
            user_times_config["min"] = 0
            user_times_config["hs"] += 1

        total_seconds = (user_times_config["hs"] * 3600) + (user_times_config["min"] * 60) + user_times_config["sec"]
        new_teme = total_seconds
        if new_teme == 30:
                new_teme = 0
                
        if data == "save_delay":
            await update_user_settings(user_id, "delay_time", new_teme)
            await query.answer(f"Delay sauvegardé en {new_teme} secondes", show_alert=True)
        
        if data == "save_schedule":
            await update_user_settings(user_id, "schedule_time", new_teme)
            await query.answer(f"Schedule sauvegardé en {new_teme} secondes", show_alert=True)

        Hvalue = user_times_config.get("hs", 0)
        Mvalue = user_times_config.get("min", 0)
        Svalue = user_times_config.get("sec", 30)  
        settings = userinfo.get("settings", {})
        delay_time = settings.get("delay_time", 0)
        schedule_time = settings.get("schedule_time", 0)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"H +1", callback_data="hs_add"), InlineKeyboardButton(f"Min +10", callback_data="min_add"), InlineKeyboardButton(f"Sec +30", callback_data="sec_add")],
            [InlineKeyboardButton(f"{Hvalue} H", callback_data="no_data"), InlineKeyboardButton(f"{Mvalue} Min", callback_data="no_data"), InlineKeyboardButton(f"{Svalue} Sec", callback_data="no_data")],
            [InlineKeyboardButton(f"H -1", callback_data="hs_rem"), InlineKeyboardButton(f"Min -10", callback_data="min_rem"), InlineKeyboardButton(f"Sec -30", callback_data="sec_rem")],
            [InlineKeyboardButton(lang["btn"]["save_delay"], callback_data="save_delay"), InlineKeyboardButton(lang["btn"]["save_schedule"], callback_data="save_schedule")],
            [InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="clone_main"), InlineKeyboardButton(lang["btn"]["reset"], callback_data="reset")]
        ])

        try:
            await query.edit_message_text(text=lang["clone"]["edit_time_msg"].format(total_seconds, delay_time, schedule_time), reply_markup=keyboard)
        except:
            pass