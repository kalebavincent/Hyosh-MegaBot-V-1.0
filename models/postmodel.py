from datetime import datetime
import re
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class Button(BaseModel):
    text: str
    url: str
    x: int
    y: int

class Media(BaseModel):
    url: str
    type: str

class Author(BaseModel):
    id: int
    name: str
    photo_url: Optional[str] = None
    

class Likes(BaseModel):
    x: int
    y: int
    emoji: str
    count: int
    reactors: List[int] = []

class Post(BaseModel):
    id: int
    author: Author
    text: str
    media: List[Media] = []
    buttons: List[Button] = []
    likes: List[Likes] = [] 
    status: str = "pending"
    unique_id: Optional[str] = ""
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)  

    class Config:
        arbitrary_types_allowed = True  

    def add_like(self, user_id: int, emoji: str):
        """Ajoute un like à un emoji en retirant l'ancien like de l'utilisateur sans supprimer les emojis."""
        previous_like = None

        for like in self.likes:
            if user_id in like.reactors:
                like.reactors.remove(user_id)
                like.count -= 1
                previous_like = like

        for like in self.likes:
            if like.emoji == emoji:
                if previous_like is not like:  
                    like.reactors.append(user_id)
                    like.count += 1
                return

        new_like = Likes(x=len(self.likes), y=0, emoji=emoji, count=1, reactors=[user_id])
        self.likes.append(new_like)
 

    def add_emoji(self, emoji_text: str):
        """Remplace tous les anciens emojis par les nouveaux."""
        emojis = likes_emoji_parser(emoji_text)

        if isinstance(emojis, str):
            raise ValueError(emojis)

        self.likes.clear()
        self.likes.extend(emojis)
    
    def remove_all_emoji(self):
        """Supprime tous les emojis de la publication."""
        self.likes.clear()
        
    def remove_all_buttons(self):
        """Supprime tous les boutons de la publication."""
        self.buttons.clear()

    def mark_completed(self):
        """Marque la publication comme terminée."""
        self.status = "completed"

    def mark_failed(self):
        """Marque la publication comme échouée."""
        self.status = "failed"
        
    def get_post_status(self):
        """Retourne le status actuel de la publication."""
        if self.status == "completed":
            return 1
        elif self.status == "failed":
            return 0
        else:
            return 2
            
    def add_buttons(self, buttons_str: str):
        """Supprime les anciens boutons et ajoute les nouveaux."""
        buttons = button_parser(buttons_str)
        
        if isinstance(buttons, str):
            raise ValueError(buttons)

        self.buttons.clear()  
        self.buttons.extend(buttons)

        
    def add_button(self, text: str, url: str, x: int, y: int):
        """Ajoute un bouton avec la position x et y."""
        if any(btn.x == x and btn.y == y for btn in self.buttons):
            raise ValueError(f"Un bouton existe déjà à la position ({x}, {y})")
        self.buttons.append(Button(text=text, url=url, x=x, y=y))

    def get_keyboard_layout(self) -> Dict[int, List[Dict[str, Any]]]:
        """Retourne la disposition du clavier avec les boutons organisés par ligne et colonne."""
        layout = {}
        for btn in self.buttons:
            layout.setdefault(btn.y, []).append({"text": btn.text, "url": btn.url, "x": btn.x})

        for y in layout:
            layout[y].sort(key=lambda b: b["x"]) 

        return layout

    def to_inline_keyboard(self) -> Optional[InlineKeyboardMarkup]:
        """Génère le clavier inline avec les likes et les boutons, retourne None si vide."""
        keyboard = []

        likes_layout = {}
        for like in self.likes:
            formatted_count = format_number(like.count)
            likes_layout.setdefault(like.y, []).append({
                "emoji": f"{like.emoji} {formatted_count}",
                "x": like.x
            })

        for y in likes_layout:
            likes_layout[y].sort(key=lambda l: l["x"])

        for y in sorted(likes_layout.keys()):
            row = [
                InlineKeyboardButton(
                    like["emoji"], 
                    callback_data=f"likeemoji_{self.unique_id}_{like['emoji']}"
                ) for like in likes_layout[y]
            ]
            keyboard.append(row)

        layout = self.get_keyboard_layout()
        for y in sorted(layout.keys()):
            row = [InlineKeyboardButton(btn["text"], url=btn["url"]) for btn in layout[y]]
            keyboard.append(row)

        return InlineKeyboardMarkup(keyboard) if keyboard else None



    def add_text(self, text: str):
        """Ajoute du texte au post."""
        self.text += text
    
    def add_media(self, media: Media):
        """Ajoute un média à la liste des médias."""
        self.media.clear()
        self.media.append(media)




#------------------------------------------------------------------------------
# Fonctions utilitaires
#------------------------------------------------------------------------------

def button_parser(buttons_str: str) -> List[Button]:
    buttons = []
    lines = buttons_str.strip().split('|')  

    y = 1

    for line in lines:
        line = line.strip()

        match = re.match(r'^(.*?)\s*\((https?://[^\s]+)\)$', line, re.DOTALL)

        if match:
            text = match.group(1).strip()  
            url = match.group(2).strip()
            buttons.append(Button(text=text, url=url, x=1, y=y))

        y += 1  

    return buttons


def likes_emoji_parser(emoji_text: str) -> List[Likes]:
    groups = emoji_text.split('|')
    
    result = []
    y = 1  
    x = 1  

    if len(groups) == 2:
        for group_index, group in enumerate(groups):
            emojis = group.split()

            if len(emojis) > 2:
                return "Erreur : Une ligne ne peut pas contenir plus de 2 emojis."

            for emoji in emojis:
                result.append(Likes(x=x, y=y, emoji=emoji, count=0))
                x += 1

            y += 1
            x = 1  

    elif len(groups) == 1:
        emojis = groups[0].split()

        if len(emojis) > 5:
            return f"Erreur : Une ligne ne peut pas contenir plus de 5 emojis ({len(emojis)} emojis)."

        for emoji in emojis:
            result.append(Likes(x=x, y=y, emoji=emoji, count=0))
            x += 1

            if x > 5: 
                x = 1
                y += 1

    else:
        return "Erreur : Format non pris en charge."

    return result

def format_number(number: int) -> str:
    """Formate un nombre avec des suffixes (K, M, B, etc.)."""
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    elif number == 0:
        return ""
    else:
        return str(number)


  