
# Copyright (C) 2025 The Hyosh Coder Team @hyoshcoder (Don't Remove This Line)
# This file is part of the Hyosh Coder Team's Mega Bot.
# This file is free software: you can redistribute it and/or modify

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import Message
from pyrogram.types import CallbackQuery
from utils.lang import LangManager
from asyncio.exceptions import TimeoutError
from database.userdata import *
from utils.clone import stop_bot_clone
from utils.helper import ask_for_emojis, get_channel_admins, get_channel_info
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
    userid = query.from_user.id
    await update_user(userid, "lang", new_lang)

    lang = lang_manager.get_lang()
    
    try:
        await query.message.edit_text(
            lang["str_ms"].format(query.from_user.mention, client.mention),
            reply_markup=InlineKeyboardMarkup(
                [
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
                ]
            )
        )
        
        await query.answer(lang["lchangSucces"], show_alert=True)
    
    except Exception as e:
        await query.answer(lang["alert"]["chglgagan"], show_alert=True)


    
@Client.on_callback_query()
async def clbdata(client: Client, query: CallbackQuery):
    userid = query.from_user.id
    userinfo = await get_user(userid)
    lang_str = userinfo.get("lang", "fr")
    lang_manager = LangManager(lang_str)
    lang = lang_manager.get_lang()
    
    data = query.data
    if data == "help":
        try:
          await query.message.edit_text(
            lang["hlp_ms"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                        InlineKeyboardButton("1/4", callback_data="no_data"),
                        InlineKeyboardButton(lang["btn"]["btn_next"], callback_data="next_help2"),
                    ],
                ]
            )
        )
        except:
          pass
    elif data == "settings":
        userinfo_settings = await get_user_settings(client, query)

        # Mapping des formats
        format_map = {
            "normal": lang["btn"]["btn_fNormal"],
            "markdown": lang["btn"]["btn_fMarkdown"],
            "html": lang["btn"]["btn_fHtml"]
        }
        format_format = userinfo_settings.get("format_format", "normal")
        format_format_display = format_map.get(format_format, "Normal")

        settings_map = {
            "protected_msg": "btn_protected",
            "notifications": "btn_notifications",
            "auto_delete": "btn_autodelete",
            "link_preview": "btn_linkpreview",
            "default_reaction": "btn_defaultreaction"
        }

        settings_values = {
            key: lang["btn"]["btn_yes"] if userinfo_settings.get(key, False) else lang["btn"]["btn_no"]
            for key in settings_map
        }

        default_reaction_emoji = userinfo_settings.get("default_reaction_emoji", "👍")

        buttons = [
            [
                InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                InlineKeyboardButton(lang["btn"]["btn_manageBot"], callback_data="manage_bot")
            ],
            [InlineKeyboardButton(lang["btn"]["btn_manageChannel"], callback_data="manage_channel")],
            [InlineKeyboardButton("==============", callback_data="no_data")],
            [InlineKeyboardButton(format_format_display, callback_data="format_style")]
        ]

        for key, btn_key in settings_map.items():
            if key != "default_reaction":  
                value = settings_values.get(key, lang["btn"]["btn_no"])
                buttons.append([InlineKeyboardButton(lang["btn"][btn_key].format(value), callback_data=key)])

        buttons.append([InlineKeyboardButton(lang["btn"]["btn_defaultreaction"].format(settings_values.get("default_reaction", lang["btn"]["btn_no"])), callback_data="default_reaction")])

        buttons.append([InlineKeyboardButton(lang["btn"]["btn_defaultreaction_emoji"].format(default_reaction_emoji), callback_data="default_reaction_emoji")])

        try:
          await query.message.edit_text(
            lang["sett_msg"],
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        except:
          pass

    elif data == "create_bot":
        try:
          await query.message.edit_text(
            lang["cbot_msg"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                        InlineKeyboardButton("Obtenir un jeton", url="https://t.me/BotFather?newbot="),
                    ],
                ]
            )
        )
        except:
          pass
        
    elif data == "change_lang":
        await change_language(client, query)
        
    elif data == "back_to_start":
        try:
          await query.message.edit_text(
            lang["str_ms"].format(query.from_user.mention, client.mention),
            reply_markup=InlineKeyboardMarkup(
            [
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
            ]   
        )
        )
        except:
          pass
    
    elif data == "no_data":
        await query.answer(lang["alert"]["no_data"])
        
    elif data == "next_help2":
        try:
          await query.message.edit_text(
            lang["hlp_ms2"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="help"),
                        InlineKeyboardButton("2/4", callback_data="no_data"),
                        InlineKeyboardButton(lang["btn"]["btn_next"], callback_data="next_help3"),
                    ],
                ]
            )
        )
        except:
          pass
    
    elif data == "next_help3":
        try:
          await query.message.edit_text(
            lang["hlp_ms3"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="next_help2"),
                        InlineKeyboardButton("3/4", callback_data="no_data"),
                        InlineKeyboardButton(lang["btn"]["btn_next"], callback_data="next_help4"),
                    ],
                ]
            )
        ) 
        except:
          pass
    
    elif data == "next_help4":
        await query.message.edit_text(
            lang["hlp_ms4"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="next_help3"),
                        InlineKeyboardButton("4/4", callback_data="no_data"),
                    ],
                ]
            )
        )
        
    elif data == "donate":
        await query.message.edit_text(
            lang["donate_msg"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                        InlineKeyboardButton("🌷", callback_data="no_data"),
                        InlineKeyboardButton(lang["btn"]["btn_admin"], url="https://t.me/hyoshmangavf"),
                    ],
                ]
            )
        )
        
    elif data == "back_to_choice_cnlStats":
        await query.message.edit_text(
            lang["stats_cnl_msg"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                    #    lister les canaux dynamiq
                    ],
                ]
            )
        )
    elif data == "stats":
        await query.message.edit_text(
            lang["stats_msg"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                        InlineKeyboardButton("🌷", callback_data="no_data"),
                        InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="back_to_choice_cnlStats"),
                    ],
                ]
            )
        )
    
    elif data == "format_style":
        userinfo_settings = await get_user_settings(client, query)
        userid = query.from_user.id
        current_format = userinfo_settings.get("format_format", "normal")
        
        format_map = {
            "normal": ("html", "HTML"),
            "html": ("markdown", "Markdown"),
            "markdown": ("normal", "Normal")
        }

        new_format, new_format_display = format_map.get(current_format, ("normal", "Normal"))
        await update_user_settings(userid, "format_format", new_format)

        userinfo_settings = await get_user_settings(client, query)
        format_format_display_map = {
            "normal": lang["btn"]["btn_fNormal"],
            "markdown": lang["btn"]["btn_fMarkdown"],
            "html": lang["btn"]["btn_fHtml"]
        }
        format_format_display = format_format_display_map.get(userinfo_settings.get("format_format", "normal"), "Normal")
        
        settings_map = {
            "protected_msg": "btn_protected",
            "notifications": "btn_notifications",
            "auto_delete": "btn_autodelete",
            "link_preview": "btn_linkpreview",
            "default_reaction": "btn_defaultreaction"
        }
        
        buttons = [
            [InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
            InlineKeyboardButton(lang["btn"]["btn_manageBot"], callback_data="manage_bot")],
            [InlineKeyboardButton(lang["btn"]["btn_manageChannel"], callback_data="manage_channel")],
            [InlineKeyboardButton("==============", callback_data="no_data")],
            [InlineKeyboardButton(format_format_display, callback_data="format_style")]
        ]

        for key, btn_key in settings_map.items():
            btn_text = lang["btn"]["btn_yes"] if userinfo_settings.get(key, False) else lang["btn"]["btn_no"]
            buttons.append([InlineKeyboardButton(lang["btn"][btn_key].format(btn_text), callback_data=key)])

        default_reaction_emoji = userinfo_settings.get("default_reaction_emoji", "👍")
        buttons.append([InlineKeyboardButton(lang["btn"]["btn_defaultreaction_emoji"].format(default_reaction_emoji), callback_data="default_reaction_emoji")])

        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_text(
            lang["format_change_msg"].format(new_format_display),
            reply_markup=reply_markup
        )


    elif data == "protected_msg":
        userinfo_settings = await get_user_settings(client, query)
        userid = query.from_user.id
        current_protect_status = userinfo_settings.get("protected_msg", False)
        new_protected = not current_protect_status
        await update_user_settings(userid, "protected_msg", new_protected)
        userinfo_settings = await get_user_settings(client, query)

        format_options = {
            "normal": lang["btn"]["btn_fNormal"],
            "markdown": lang["btn"]["btn_fMarkdown"],
            "html": lang["btn"]["btn_fHtml"]
        }
        format_format_display = format_options.get(userinfo_settings.get("format_format", "normal"), "Normal")

        def get_status_label(key, default=False):
            return lang["btn"]["btn_yes"] if userinfo_settings.get(key, default) else lang["btn"]["btn_no"]

        protected_msg = get_status_label("protected_msg", False)
        notifications = get_status_label("notifications", True)
        auto_delete = get_status_label("auto_delete", False)
        link_preview = get_status_label("link_preview", False)
        default_reaction = get_status_label("default_reaction", False)
        default_reaction_emoji = userinfo_settings.get("default_reaction_emoji", "👍")

        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                InlineKeyboardButton(lang["btn"]["btn_manageBot"], callback_data="manage_bot")
            ],
            [InlineKeyboardButton(lang["btn"]["btn_manageChannel"], callback_data="manage_channel")],
            [InlineKeyboardButton("==============", callback_data="no_data")],
            [InlineKeyboardButton(format_format_display, callback_data="format_style")],
            [InlineKeyboardButton(lang["btn"]["btn_protected"].format(protected_msg), callback_data="protected_msg")],
            [InlineKeyboardButton(lang["btn"]["btn_notifications"].format(notifications), callback_data="notifications")],
            [InlineKeyboardButton(lang["btn"]["btn_autodelete"].format(auto_delete), callback_data="auto_delete")],
            [InlineKeyboardButton(lang["btn"]["btn_linkpreview"].format(link_preview), callback_data="link_preview")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction"].format(default_reaction), callback_data="default_reaction")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction_emoji"].format(default_reaction_emoji), callback_data="default_reaction_emoji")]
        ])

        await query.message.edit_text(
            lang["protected_change_msg"].format(new_protected),
            reply_markup=reply_markup
        )

    
    elif data == "notifications":
        userid = query.from_user.id
        userinfo_settings = await get_user_settings(client, query)

        new_status = not userinfo_settings.get("notifications", False)

        await update_user_settings(userid, "notifications", new_status)
        userinfo_settings = await get_user_settings(client, query)

        format_map = {
            "normal": lang["btn"]["btn_fNormal"],
            "markdown": lang["btn"]["btn_fMarkdown"],
            "html": lang["btn"]["btn_fHtml"]
        }
        
        format_format_display = format_map.get(userinfo_settings.get("format_format", "normal"), "Normal")

        def get_user_setting_display(key, default=False):
            return lang["btn"]["btn_yes"] if userinfo_settings.get(key, default) else lang["btn"]["btn_no"]

        protected_msg = get_user_setting_display("protected_msg")
        notifications = get_user_setting_display("notifications", True)
        auto_delete = get_user_setting_display("auto_delete")
        link_preview = get_user_setting_display("link_preview")
        default_reaction = get_user_setting_display("default_reaction")
        default_reaction_emoji = userinfo_settings.get("default_reaction_emoji", "👍")

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
            InlineKeyboardButton(lang["btn"]["btn_manageBot"], callback_data="manage_bot")],
            [InlineKeyboardButton(lang["btn"]["btn_manageChannel"], callback_data="manage_channel")],
            [InlineKeyboardButton("==============", callback_data="no_data")],
            [InlineKeyboardButton(format_format_display, callback_data="format_style")],
            [InlineKeyboardButton(lang["btn"]["btn_protected"].format(protected_msg), callback_data="protected_msg")],
            [InlineKeyboardButton(lang["btn"]["btn_notifications"].format(notifications), callback_data="notifications")],
            [InlineKeyboardButton(lang["btn"]["btn_autodelete"].format(auto_delete), callback_data="auto_delete")],
            [InlineKeyboardButton(lang["btn"]["btn_linkpreview"].format(link_preview), callback_data="link_preview")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction"].format(default_reaction), callback_data="default_reaction")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction_emoji"].format(default_reaction_emoji), callback_data="default_reaction_emoji")]
        ])
        
        await query.message.edit_text(
            lang["notifications_change_msg"].format(new_status),
            reply_markup=reply_markup
        )
    
    elif data == "auto_delete":
        userid = query.from_user.id
        userinfo_settings = await get_user_settings(client, query)

        new_autodel = not userinfo_settings.get("auto_delete", False)
        await update_user_settings(userid, "auto_delete", new_autodel)

        userinfo_settings["auto_delete"] = new_autodel
        format_format_display = {
            "normal": lang["btn"]["btn_fNormal"],
            "markdown": lang["btn"]["btn_fMarkdown"],
            "html": lang["btn"]["btn_fHtml"]
        }.get(userinfo_settings.get("format_format", "normal"), "Normal")

        def get_label(setting_key, default=False):
            return lang["btn"]["btn_yes"] if userinfo_settings.get(setting_key, default) else lang["btn"]["btn_no"]

        protected_msg = get_label("protected_msg", False)
        notifications = get_label("notifications", True)
        auto_delete = get_label("auto_delete", False)
        link_preview = get_label("link_preview", False)
        default_reaction = get_label("default_reaction", False)
        default_reaction_emoji = userinfo_settings.get("default_reaction_emoji", "👍")

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
            InlineKeyboardButton(lang["btn"]["btn_manageBot"], callback_data="manage_bot")],
            [InlineKeyboardButton(lang["btn"]["btn_manageChannel"], callback_data="manage_channel")],
            [InlineKeyboardButton("==============", callback_data="no_data")],
            [InlineKeyboardButton(format_format_display, callback_data="format_style")],
            [InlineKeyboardButton(lang["btn"]["btn_protected"].format(protected_msg), callback_data="protected_msg")],
            [InlineKeyboardButton(lang["btn"]["btn_notifications"].format(notifications), callback_data="notifications")],
            [InlineKeyboardButton(lang["btn"]["btn_autodelete"].format(auto_delete), callback_data="auto_delete")],
            [InlineKeyboardButton(lang["btn"]["btn_linkpreview"].format(link_preview), callback_data="link_preview")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction"].format(default_reaction), callback_data="default_reaction")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction_emoji"].format(default_reaction_emoji), callback_data="default_reaction_emoji")]
        ])

        await query.message.edit_text(
            lang["auto_delete_change_msg"].format(new_autodel),
            reply_markup=reply_markup
        )

    elif data == "link_preview":
        userid = query.from_user.id
        userinfo_settings = await get_user_settings(client, query)
        
        new_status = not userinfo_settings.get("link_preview", False)
        
        await update_user_settings(userid, "link_preview", new_status)
        
        userinfo_settings = await get_user_settings(client, query)

        format_map = {
            "normal": lang["btn"]["btn_fNormal"],
            "markdown": lang["btn"]["btn_fMarkdown"],
            "html": lang["btn"]["btn_fHtml"]
        }
        format_format_display = format_map.get(userinfo_settings.get("format_format", "normal"), "Normal")

        btn_values = {
            "protected_msg": lang["btn"]["btn_yes"] if userinfo_settings.get("protected_msg", False) else lang["btn"]["btn_no"],
            "notifications": lang["btn"]["btn_yes"] if userinfo_settings.get("notifications", True) else lang["btn"]["btn_no"],
            "auto_delete": lang["btn"]["btn_yes"] if userinfo_settings.get("auto_delete", False) else lang["btn"]["btn_no"],
            "link_preview": lang["btn"]["btn_yes"] if userinfo_settings.get("link_preview", False) else lang["btn"]["btn_no"],
            "default_reaction": lang["btn"]["btn_yes"] if userinfo_settings.get("default_reaction", False) else lang["btn"]["btn_no"],
            "default_reaction_emoji": userinfo_settings.get("default_reaction_emoji", "👍")
        }

        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                InlineKeyboardButton(lang["btn"]["btn_manageBot"], callback_data="manage_bot")
            ],
            [InlineKeyboardButton(lang["btn"]["btn_manageChannel"], callback_data="manage_channel")],
            [InlineKeyboardButton("==============", callback_data="no_data")],
            [InlineKeyboardButton(format_format_display, callback_data="format_style")],
            [InlineKeyboardButton(lang["btn"]["btn_protected"].format(btn_values["protected_msg"]), callback_data="protected_msg")],
            [InlineKeyboardButton(lang["btn"]["btn_notifications"].format(btn_values["notifications"]), callback_data="notifications")],
            [InlineKeyboardButton(lang["btn"]["btn_autodelete"].format(btn_values["auto_delete"]), callback_data="auto_delete")],
            [InlineKeyboardButton(lang["btn"]["btn_linkpreview"].format(btn_values["link_preview"]), callback_data="link_preview")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction"].format(btn_values["default_reaction"]), callback_data="default_reaction")],
            [InlineKeyboardButton(lang["btn"]["btn_defaultreaction_emoji"].format(btn_values["default_reaction_emoji"]), callback_data="default_reaction_emoji")]
        ])

        await query.message.edit_text(
            lang["link_preview_change_msg"].format(new_status),
            reply_markup=reply_markup
        )
    elif data == "default_reaction":
        userinfo_settings = await get_user_settings(client, query)
        userid = query.from_user.id

        new_default_reaction = not userinfo_settings.get("default_reaction", False)

        await update_user_settings(userid, "default_reaction", new_default_reaction)

        userinfo_settings = await get_user_settings(client, query)

        format_options = {
            "normal": lang["btn"]["btn_fNormal"],
            "markdown": lang["btn"]["btn_fMarkdown"],
            "html": lang["btn"]["btn_fHtml"]
        }
        format_format_display = format_options.get(userinfo_settings.get("format_format", "normal"), "Normal")

        settings_map = {
            "protected_msg": "btn_protected",
            "notifications": "btn_notifications",
            "auto_delete": "btn_autodelete",
            "link_preview": "btn_linkpreview",
            "default_reaction": "btn_defaultreaction"
        }

        buttons = [
            [
                InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                InlineKeyboardButton(lang["btn"]["btn_manageBot"], callback_data="manage_bot")
            ],
            [InlineKeyboardButton(lang["btn"]["btn_manageChannel"], callback_data="manage_channel")],
            [InlineKeyboardButton("==============", callback_data="no_data")],
            [InlineKeyboardButton(format_format_display, callback_data="format_style")]
        ]

        for key, btn_key in settings_map.items():
            value = lang["btn"]["btn_yes"] if userinfo_settings.get(key, False) else lang["btn"]["btn_no"]
            buttons.append([InlineKeyboardButton(lang["btn"][btn_key].format(value), callback_data=key)])

        default_reaction_emoji = userinfo_settings.get("default_reaction_emoji", "👍")
        buttons.append([InlineKeyboardButton(lang["btn"]["btn_defaultreaction_emoji"].format(default_reaction_emoji), callback_data="default_reaction_emoji")])

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(
            lang["default_reaction_change_msg"].format(new_default_reaction),
            reply_markup=reply_markup
        )

    elif data == "add_new_channel":
        bot_username = (await client.get_me()).username
        add_bot_link = f"https://t.me/{bot_username}?startgroup=true&admin=can_post_messages,can_edit_messages,can_delete_messages,can_invite_users,can_manage_chat,can_change_info,can_pin_messages"

        await query.message.edit_text(
            lang["add_chnl_msg"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                        InlineKeyboardButton(lang["btn"]["btn_addto_grp"], url=add_bot_link),
                    ],
                ]
            )
        )
        
    elif data == "manage_bot":
        userid = query.from_user.id
        bots = await get_bots(userid)
        
        if not bots:
            await query.message.edit_text(
                lang["alert"]["no_bots"],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                            InlineKeyboardButton(lang["btn"]["btn_CBot"], callback_data="create_bot"),
                        ],
                    ]
                )
            )
            return
        
        buttons = []
        for bot in bots:
            buttons.append([InlineKeyboardButton(bot["name"], callback_data=f"managebot_{bot['id']}")])
            
        buttons.append([InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="settings")])
        
        await query.message.edit_text(
            lang["manage_bot_msg"],
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data.startswith("managebot_"):
        bot_id = data.split("_")[1]
        userid = query.from_user.id
        
        await query.message.edit_text(
            lang["question"]["manage_bot"].format(bot_id),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_bot"),
                        InlineKeyboardButton(lang["btn"]["btn_delete"], callback_data=f"deletebot_{bot_id}"),
                    ],
                ]
            )
        )
        
    elif data.startswith("deletebot_"):
        bot_id = data.split("_")[1]
        userid = query.from_user.id
        await query.message.edit_text(
                lang["alert"]["confirmation"],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_yes"], callback_data=f"deletebotconfirm_{bot_id}"),
                            InlineKeyboardButton(lang["btn"]["btn_no"], callback_data="manage_bot"),
                        ],
                    ]
                )
            )
    elif data.startswith("deletebotconfirm_"):
        bot_id = data.split("_")[1]
        userid = query.from_user.id
        try:
            await delete_bot(userid, bot_id)
            await stop_bot_clone(bot_id)
            sessionfile = f"bot_{bot_id}.session"
            sessionjournal = f"bot_{bot_id}.session-journal"
            if os.path.exists(sessionfile):
                os.remove(sessionfile)
            if os.path.exists(sessionjournal):
                os.remove(sessionjournal)
            await query.message.edit_text(
                lang["alert"]["DeleteSuccessBot"].format(bot_id),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_bot"),
                            InlineKeyboardButton(lang["btn"]["btn_CBot"], callback_data="create_bot"),
                        ],
                    ]
                )
            )
        except Exception as e:
            await query.message.edit_text(
                lang["alert"]["DeleteErrorBot"].format(bot_id, str(e)),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_bot"),
                            InlineKeyboardButton(lang["btn"]["btn_CBot"], callback_data="create_bot"),
                        ],
                    ]
                )
            )
        
    elif data == "manage_channel":
        userid = query.from_user.id
        channels = await get_channels(userid)
        
        if not channels:
            await query.message.edit_text(
                lang["alert"]["no_channels"],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="settings"),
                            InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                        ],
                    ]
                )
            )
            return
        
        buttons = []
        for channel in channels:
            buttons.append([InlineKeyboardButton(channel["name"], callback_data=f"managechannel_{channel['id']}")])
            
        buttons.append([InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="settings")])

        await query.message.edit_text(
            lang["manage_channel_msg"],
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    elif data.startswith("managechannel_"):
        channel_id = data.split("_")[1]
        userid = query.from_user.id
        
        await query.message.edit_text(
            lang["question"]["manage_channel"].format(channel_id),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_channel"),
                        InlineKeyboardButton(lang["btn"]["btn_delete"], callback_data=f"deletechannel_{channel_id}"),
                    ],
                    [
                        InlineKeyboardButton(lang["btn"]["btn_update"], callback_data=f"updatechannel_{channel_id}"),
                    ],
                    [
                        InlineKeyboardButton(lang["btn"]["btn_viewinfo"], callback_data=f"view_channel_{channel_id}"),
                    ]
                ]
            )
        )
        
    elif data.startswith("deletechannel_"):
        channel_id = data.split("_")[1]
        userid = query.from_user.id
        await query.message.edit_text(
                lang["alert"]["confirmation"],
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_yes"], callback_data=f"deletechannelconfirm_{channel_id}"),
                            InlineKeyboardButton(lang["btn"]["btn_no"], callback_data="manage_channel"),
                        ],
                    ]
                )
            )
    elif data.startswith("deletechannelconfirm_"):
        channel_id = data.split("_")[1]
        userid = query.from_user.id
        try:
            await delete_channel(userid, channel_id)
            await query.message.edit_text(
                lang["alert"]["DeleteSuccessChannel"].format(channel_id),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_channel"),
                            InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                        ],
                    ]
                )
            )
        except Exception as e:
            await query.message.edit_text(
                lang["alert"]["DeleteErrorChannel"].format(channel_id, str(e)),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_channel"),
                            InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                        ],
                    ]
                )
            )
            
    elif data.startswith("updatechannel_"):
        channel_id = data.split("_")[1]
        userid = query.from_user.id
        
        await query.message.edit_text(
            lang["alert"]["confirmation"],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(lang["btn"]["btn_yes"], callback_data=f"updatechannelconfirm_{channel_id}"),
                        InlineKeyboardButton(lang["btn"]["btn_no"], callback_data="manage_channel"),
                    ],
                ]
            )
        )
    elif data.startswith("updatechannelconfirm_"):
        channel_id = data.split("_")[1]
        userid = query.from_user.id
        new_channels = await get_channel_info(channel_id, client)
        if new_channels:
            await update_channel(userid, channel_id, "name", new_channels["title"])
            await update_channel(userid, channel_id, "admins", new_channels["admins"])
            
            await query.message.edit_text(
                lang["alert"]["UpdateSuccessChannel"].format(channel_id),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_channel"),
                            InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                        ],
                    ]
                )
            )
        else:
            await query.answer(lang["presencerequest"].format(channel_id), show_alert=True)
            await query.message.edit_text(
                lang["alert"]["UpdateErrorChannel"].format(channel_id),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_channel"),
                            InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                        ],
                    ]
                )
            )
            
    elif data.startswith("view_channel_"):
            channel_id = int(data.split("_")[2]) 
            userid = query.from_user.id
            channels_info = await get_channels(userid)
            channel = next((chan for chan in channels_info if chan["id"] == channel_id), None)
            
            if channel:
                nom = channel["name"]
                channel_id = channel["id"]
                admins_info = await get_channel_admins(client, channel_id)
                
                mapping_admins = "\n".join(
                    f"- [{admin['name']}](tg://user?id={admin['id']}) ({'Bot' if admin['is_bot'] else 'User'})"
                    for admin in admins_info
                )
                
                await query.message.edit_text(
                    lang["cnlinfo_msg"].format(nom, nom, channel_id, mapping_admins),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="manage_channel"),
                                InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                            ],
                        ]
                    )
                )
            else:
                await query.message.edit_text(
                    lang["alert"]["no_channels"],
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(lang["btn"]["btn_back"], callback_data="settings"),
                                InlineKeyboardButton(lang["btn"]["btn_adCnl"], callback_data="add_new_channel"),
                            ],
                        ]
                    )
                )

    elif data == "default_reaction_emoji":
        user_id = query.from_user.id
        user_response = await ask_for_emojis(client, user_id, lang)
        await query.message.edit_text(lang["question"]["input_emojis"])

        if not user_response:
            await query.message.edit_text(
                lang["alert"]["timeout"],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(lang["btn"]["btn_resaie"], callback_data="default_reaction_emoji")],
                    [InlineKeyboardButton(lang["btn"]["btn_settings"], callback_data="settings")]
                ])
            )
            return

        emoji_input = user_response.text.strip() if isinstance(user_response, Message) else user_response.strip()
        if isinstance(user_response, Message):
            await user_response.delete()

        if not emoji_input or any(char.isalnum() for char in emoji_input):
            await query.message.edit_text(
                lang["alert"]["invalid_emojis"],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(lang["btn"]["btn_resaie"], callback_data="default_reaction_emoji")],
                    [InlineKeyboardButton(lang["btn"]["btn_settings"], callback_data="settings")]
                ])
            )
            return

        await update_user_settings(user_id, "default_reaction_emoji", emoji_input)

        await query.answer()
        await query.message.edit_text(
            lang["alert"]["emoji_changed"].format(emoji_input),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(lang["btn"]["btn_home"], callback_data="back_to_start"),
                    InlineKeyboardButton(lang["btn"]["btn_settings"], callback_data="settings"),
                ]
            ])
        )
