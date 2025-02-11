import re
from typing import List


def button_parser(buttons_str: str) -> List[dict]:
    buttons = []
    lines = buttons_str.strip().split('||')
    
    y = 1  # Ligne actuelle (y)

    for line in lines:
        button_data = line.strip().split()
        
        x = 1  # Position dans la ligne (x)
        for button in button_data:
            button = button.strip() 
            button.replace(' ', '_', 1)            # Enlever les espaces autour
            
            # Regex pour capturer tout avant '(' et l'URL après
            match = re.match(r'^(.*)\s?\((https?://[^\s]+)\)$', button)
              # Enlever les espaces autour
            if match:
                text = match.group(1).strip()  # Texte avant la parenthèse
                url = match.group(2).strip()   # URL après la parenthèse
                text = text.replace('_', ' ') # Enlever les espaces autour
                # Ajouter le bouton à la liste
                buttons.append({
                    "text": text,
                    "url": url,
                    "x": x,
                    "y": y
                })
                x += 1  # Augmenter la position horizontale
                
        y += 1  # Augmenter la position verticale

    return buttons


# Exemple de texte à parser
text = "🐦‍🔥Tout_manga_confondu_🐦‍🔥(https://t.me/hyoshmangavf) || 📖 Tout manga 📖 (https://t.me/hyoshmangavf)"
buttons = button_parser(text)
print(buttons)
