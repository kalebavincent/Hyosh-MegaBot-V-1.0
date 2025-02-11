import os
from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery, InlineQueryResultPhoto, InlineQueryResultVideo,
    InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
)
from models.postmodel import Post
from database.postdata import get_post_by_unique_id
import hashlib

@Client.on_inline_query()
async def inline_query_handler(client, query: InlineQuery):
    unique_id = query.query.strip()

    if not unique_id:
        await query.answer([], cache_time=1)
        return

    post_data = await get_post_by_unique_id(unique_id)

    if not post_data:
        await query.answer([], cache_time=1)
        return

    post = Post(
        id=post_data.id,
        author=post_data.author,
        text=post_data.text,
        media=post_data.media,
        likes=post_data.likes,
        buttons=post_data.buttons,
        unique_id=post_data.unique_id,
        timestamp=post_data.timestamp
    ) 
    
    inline_keyboard = post.to_inline_keyboard()

    result_id = hashlib.md5(post.unique_id.encode()).hexdigest()[:10]

    results = []

    if post.media:
        media = post.media[0]  # Assume the first media item
        media_type = media.type
        media_id = media.url
        
        downloaded_media = await client.download_media(media_id, file_name=os.path.join("temp_", f"{result_id}.jpg"))
        mediaurl = f"temp_/{result_id}.jpg"
        print(mediaurl)
        print(downloaded_media)

        if media_type == "photo":
            results.append(
                InlineQueryResultPhoto(
                    id=result_id,
                    photo_url=mediaurl,  # Use file_id for photo
                    title=f"Post de {post.author.name}",
                    description=post.text[:50] + "...", 
                    caption=post.text,  
                    reply_markup=inline_keyboard
                )
            )
        elif media_type == "video":
            results.append(
                InlineQueryResultVideo(
                    id=result_id,
                    video_url=mediaurl,  # Use file_id for video
                    title=f"Post de {post.author.name}",
                    description=post.text[:50] + "...", 
                    caption=post.text, 
                    reply_markup=inline_keyboard,
                    mime_type="video/mp4"
                )
            )
    else:
        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=f"Post de {post.author.name}",
                description=post.text[:50] + "...",  
                input_message_content=InputTextMessageContent(
                    message_text=post.text,  
                    parse_mode="markdown"
                ),
                reply_markup=inline_keyboard
            )
        )

    await query.answer(results, cache_time=5)
    os.remove(downloaded_media)
