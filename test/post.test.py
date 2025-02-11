import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



from datetime import datetime
from models.postmodel import Author, Media, Post, button_parser

author = Author(id=1, name="John Doe", photo_url="https://example.com/photo.jpg")

media = Media(url="https://example.com/image.jpg")  # Un seul média

#------------------------------------------------------------------------------
# Création d'un post
#------------------------------------------------------------------------------
post = Post(
    id=1,
    author=author,
    text="Bienvenue sur ma première publication! Voici un aperçu de mes créations.",
    media=[media],  
    buttons=[],
    likes=[],
    timestamp=datetime.now()
)

#------------------------------------------------------------------------------
# Ajout de boutons d'emojis reactions
#------------------------------------------------------------------------------
post.add_emoji("😊 ❤️ | 😂 👍")  

#------------------------------------------------------------------------------
# Ajout de boutons
#------------------------------------------------------------------------------
button = "btn1(https://example.com) btn2(https://example.com) | btn3(https://example.com)"
post.add_buttons(button)

#------------------------------------------------------------------------------
# Generation du clavier inline
#------------------------------------------------------------------------------
inline_keyboard = post.to_inline_keyboard()

#------------------------------------------------------------------------------
# Affichage des informations du post
#------------------------------------------------------------------------------
print(f"Auteur: {post.author.name}")
print(f"Texte: {post.text}")
print(f"Média: {[media.url for media in post.media]}")
print(f"Likes: {[like.emoji for like in post.likes]}")

#------------------------------------------------------------------------------
# Affichage du clavier inline
#------------------------------------------------------------------------------
print("Clavier inline (boutons et likes):")
for row in inline_keyboard.inline_keyboard:
    print([btn.text if hasattr(btn, 'text') else btn.callback_data for btn in row])


#------------------------------------------------------------------------------
# Acceeder au info des boutons
#------------------------------------------------------------------------------
for btn in post.buttons:
    print(f"Texte: {btn.text}")
    print(f"URL: {btn.url}")
    print(f"X: {btn.x}")
    print(f"Y: {btn.y}")

#------------------------------------------------------------------------------
# Acceeder au info des likes
#------------------------------------------------------------------------------
for like in post.likes:
    print(f"Emoji: {like.emoji}")
    print(f"X: {like.x}")
    print(f"Y: {like.y}")

#------------------------------------------------------------------------------
# Affichage des informations du post    
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Affichage de la publication complet 
#------------------------------------------------------------------------------

print("\n\n----------------------------------")
print("Publication complet:")
print(f"ID: {post.id}")
print(f"Auteur: {post.author.name}")
print(f"Texte: {post.text}")
print(f"Média: {[media.url for media in post.media]}")
print(f"Likes: {[like.emoji for like in post.likes]}")
print(f"Boutons: {[btn.text for btn in post.buttons]}")
print(f"Date: {post.timestamp}")